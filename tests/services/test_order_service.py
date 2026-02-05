"""OrderService — mocked AsyncSession + mocked storage, no real DB/S3."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import DatabaseCommunicationError, OrderNotFoundError
from app.services.order_service import OrderService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _mock_result(rows):
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    result.scalar.return_value = rows[0] if rows else None
    result.scalar_one_or_none.return_value = rows[0] if rows else None
    return result


def _fake_order(order_id=None, client_id=None, status="pending"):
    order = MagicMock()
    order.id = order_id or uuid4()
    order.client_id = client_id or uuid4()
    order.service_id = uuid4()
    order.status = status
    order.description = "Test order"
    order.quoted_price = "100.00"
    return order


def _fake_image(image_id=None, order_id=None):
    img = MagicMock()
    img.id = image_id or uuid4()
    img.order_id = order_id or uuid4()
    img.s3_object_path = "orders/2025/01/01/abc.jpg"
    img.s3_url = "https://s3.example.com/abc.jpg"
    img.image_type = "before"
    img.uploaded_by = uuid4()
    return img


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def service(session):
    return OrderService(session)


# ---------------------------------------------------------------------------
# Basic CRUD
# ---------------------------------------------------------------------------
class TestOrderServiceCRUD:
    async def test_get_returns_all(self, service, session):
        orders = [_fake_order(), _fake_order()]
        session.execute.return_value = _mock_result(orders)
        assert await service.get() == orders

    async def test_getId_returns_order(self, service, session):
        order = _fake_order()
        session.execute.return_value = _mock_result([order])
        assert await service.getId(order.id) is order

    async def test_getId_returns_none_when_missing(self, service, session):
        session.execute.return_value = _mock_result([])
        assert await service.getId(uuid4()) is None

    async def test_getMe_returns_client_orders(self, service, session):
        cid = uuid4()
        orders = [_fake_order(client_id=cid)]
        session.execute.return_value = _mock_result(orders)
        assert await service.getMe(cid) == orders

    async def test_add_persists_and_returns(self, service, session):
        schema = MagicMock()
        schema.model_dump.return_value = {
            "client_id": uuid4(),
            "service_id": uuid4(),
            "description": "New",
            "quoted_price": "50.00",
        }
        result = await service.add(schema)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once()
        assert result is not None

    async def test_remove_deletes_existing(self, service, session):
        order = _fake_order()
        session.execute.return_value = _mock_result([order])
        assert await service.remove(order.id) is True
        session.delete.assert_awaited_once_with(order)

    async def test_remove_returns_false_when_missing(self, service, session):
        session.execute.return_value = _mock_result([])
        assert await service.remove(uuid4()) is False


# ---------------------------------------------------------------------------
# getMeId — ownership + error wrapping
# ---------------------------------------------------------------------------
class TestOrderServiceGetMeId:
    async def test_raises_not_found_when_missing(self, service, session):
        session.execute.return_value = _mock_result([])
        with pytest.raises(OrderNotFoundError):
            await service.getMeId(uuid4(), uuid4())

    async def test_returns_order_when_found(self, service, session):
        order = _fake_order()
        session.execute.return_value = _mock_result([order])
        assert await service.getMeId(order.client_id, order.id) is order

    async def test_wraps_sqlalchemy_error_in_db_communication_error(
        self, service, session
    ):
        session.execute.side_effect = SQLAlchemyError("db broke")
        with pytest.raises(DatabaseCommunicationError):
            await service.getMeId(uuid4(), uuid4())


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------
class TestOrderServiceUpdate:
    async def test_returns_none_when_order_missing(self, service, session):
        session.execute.return_value = _mock_result([])
        payload = MagicMock()
        payload.model_dump.return_value = {"status": "in_progress"}
        assert await service.update(uuid4(), payload) is None

    async def test_applies_fields_and_commits(self, service, session):
        order = _fake_order()
        session.execute.return_value = _mock_result([order])
        payload = MagicMock()
        payload.model_dump.return_value = {"status": "completed", "notes": "done"}
        result = await service.update(order.id, payload)
        assert order.status == "completed"
        assert order.notes == "done"
        session.commit.assert_awaited_once()
        assert result is order


# ---------------------------------------------------------------------------
# Image queries
# ---------------------------------------------------------------------------
class TestOrderServiceImageQueries:
    async def test_getOrderImages_returns_list(self, service, session):
        imgs = [_fake_image(), _fake_image()]
        session.execute.return_value = _mock_result(imgs)
        assert len(await service.getOrderImages(uuid4())) == 2

    async def test_getImageImageId_returns_image(self, service, session):
        img = _fake_image()
        session.execute.return_value = _mock_result([img])
        assert await service.getImageImageId(str(img.id)) is img

    async def test_getImageImageId_returns_none_when_missing(self, service, session):
        session.execute.return_value = _mock_result([])
        assert await service.getImageImageId(str(uuid4())) is None


# ---------------------------------------------------------------------------
# Image upload / delete / URL regeneration
# ---------------------------------------------------------------------------
class TestOrderServiceImageOps:
    async def test_delete_removes_from_storage_and_db(self, service, session):
        img = _fake_image()
        session.execute.return_value = _mock_result([img])
        mock_storage = MagicMock()

        with patch(
            "app.services.order_service.get_storage_service",
            return_value=mock_storage,
        ):
            result = await service.delete_order_image(str(img.id))

        assert result is True
        mock_storage.delete_file.assert_called_once_with(img.s3_object_path)
        session.delete.assert_awaited_once_with(img)

    async def test_delete_returns_false_when_image_missing(self, service, session):
        session.execute.return_value = _mock_result([])
        mock_storage = MagicMock()
        with patch(
            "app.services.order_service.get_storage_service",
            return_value=mock_storage,
        ):
            assert await service.delete_order_image(str(uuid4())) is False

    async def test_regenerate_urls_updates_each_image(self, service):
        imgs = [_fake_image(), _fake_image()]
        mock_storage = MagicMock()
        mock_storage.generate_presigned_download_url.side_effect = [
            "https://fresh1.com",
            "https://fresh2.com",
        ]
        with patch(
            "app.services.order_service.get_storage_service",
            return_value=mock_storage,
        ):
            result = await service.regenerate_download_urls(imgs)
        assert result[0].s3_url == "https://fresh1.com"
        assert result[1].s3_url == "https://fresh2.com"

    async def test_upload_rejects_disallowed_content_type(self, service, session):
        file = MagicMock()
        file.content_type = "application/pdf"
        file.filename = "doc.pdf"
        mock_storage = MagicMock()

        with patch(
            "app.services.order_service.get_storage_service",
            return_value=mock_storage,
        ):
            with pytest.raises(HTTPException, match="Invalid file type"):
                await service.upload_order_image_to_storage(
                    order_id=str(uuid4()),
                    file=file,
                    uploaded_by=str(uuid4()),
                    image_type="before",
                )
