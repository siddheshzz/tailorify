"""ServiceService — mocked AsyncSession, no real DB."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.service import ServiceService


def _mock_result(rows):
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    result.scalar.return_value = rows[0] if rows else None
    result.scalar_one_or_none.return_value = rows[0] if rows else None
    return result


def _fake_service(sid=None):
    svc = MagicMock()
    svc.id = sid or uuid4()
    svc.name = "Hemming"
    svc.base_price = 150.0
    svc.is_active = True
    return svc


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def service(session):
    return ServiceService(session)


# ---------------------------------------------------------------------------
# get / getId
# ---------------------------------------------------------------------------
class TestServiceServiceRead:
    async def test_get_returns_all_services(self, service, session):
        svcs = [_fake_service(), _fake_service()]
        session.execute.return_value = _mock_result(svcs)
        assert await service.get() == svcs

    async def test_getId_returns_matching_service(self, service, session):
        svc = _fake_service()
        session.execute.return_value = _mock_result([svc])
        assert await service.getId(svc.id) is svc

    async def test_getId_returns_none_when_missing(self, service, session):
        session.execute.return_value = _mock_result([])
        assert await service.getId(uuid4()) is None


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------
class TestServiceServiceAdd:
    async def test_add_persists_and_returns(self, service, session):
        payload = ServiceCreate(
            name="Tailoring", base_price=200.0, category="custom", estimated_days=5
        )
        result = await service.add(payload)
        session.add.assert_called_once()
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once()
        assert result is not None


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------
class TestServiceServiceRemove:
    async def test_remove_deletes_existing(self, service, session):
        svc = _fake_service()
        session.execute.return_value = _mock_result([svc])
        assert await service.remove(svc.id) is True
        session.delete.assert_awaited_once_with(svc)
        session.commit.assert_awaited_once()

    async def test_remove_returns_false_when_missing(self, service, session):
        session.execute.return_value = _mock_result([])
        assert await service.remove(uuid4()) is False


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------
class TestServiceServiceUpdate:
    async def test_update_applies_fields_and_commits(self, service, session):
        svc = _fake_service()
        session.execute.return_value = _mock_result([svc])
        payload = ServiceUpdate(
            name="Updated", base_price=300.0, category="premium", estimated_days=7
        )
        result = await service.update(svc.id, payload)
        assert svc.name == "Updated"
        assert svc.base_price == 300.0
        session.commit.assert_awaited_once()
        assert result is svc

    async def test_update_returns_none_when_service_missing(self, service, session):
        session.execute.return_value = _mock_result([])
        payload = ServiceUpdate(
            name="X", base_price=1.0, category="y", estimated_days=1
        )
        assert await service.update(uuid4(), payload) is None
