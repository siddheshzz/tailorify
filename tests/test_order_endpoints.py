import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import order as order_endpoint
from app.core.security import create_access_token
from app.main import app
from app.schemas.order import OrderCreate
from app.services import order_service

client = TestClient(app)


class FakeUser:
    def __init__(self, user_id: uuid.UUID, email: str, user_type: str = "client"):
        self.id = user_id
        self.email = email
        self.user_type = user_type


@pytest.fixture()
def auth_headers_admin(monkeypatch):
    token = create_access_token({"sub": "admin@example.com"})
    fake_user = FakeUser(uuid.uuid4(), "admin@example.com", user_type="admin")
    app.dependency_overrides[order_endpoint.get_current_user] = lambda: fake_user
    yield {"Authorization": f"Bearer {token}"}
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers_client(monkeypatch):
    token = create_access_token({"sub": "client@example.com"})
    fake_user = FakeUser(uuid.uuid4(), "client@example.com", user_type="client")
    app.dependency_overrides[order_endpoint.get_current_user] = lambda: fake_user
    yield {"Authorization": f"Bearer {token}"}
    app.dependency_overrides.clear()


def test_create_order_success(monkeypatch, auth_headers_client):
    # Arrange
    created_id = uuid.uuid4()
    client_id = uuid.uuid4()

    def fake_add(order: OrderCreate):
        return SimpleNamespace(
            id=created_id,
            client_id=client_id,
            service_id=uuid.uuid4(),
            measurement_id=uuid.uuid4(),
            status="pending",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    # Dependency override for OrderServiceDep is wired in app.core.dependencies; we can monkeypatch service layer
    monkeypatch.setattr(
        order_service.OrderService, "add", staticmethod(lambda order: fake_add(order))
    )

    payload = {
        "client_id": str(client_id),
        "service_id": str(uuid.uuid4()),
        "measurement_id": str(uuid.uuid4()),
        "status": "pending",
    }

    # Act
    res = client.post("/api/v1/order/", json=payload, headers=auth_headers_client)

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert uuid.UUID(data["id"]) == created_id
    assert data["status"] == "pending"


def test_get_order_not_found_returns_404(monkeypatch, auth_headers_admin):
    # Service getId returns None -> 404
    order_id = uuid.uuid4()

    async def fake_get_id(_self, oid):
        return None

    monkeypatch.setattr(order_service.OrderService, "getId", fake_get_id)

    res = client.get(f"/api/v1/order/{order_id}", headers=auth_headers_admin)
    assert res.status_code == 404


def test_list_order_requires_admin(monkeypatch, auth_headers_client):
    # Hitting admin-protected route with client user should return 403
    res = client.get("/api/v1/order/", headers=auth_headers_client)
    assert res.status_code in (401, 403)


def test_get_order_me_enforces_ownership(monkeypatch, auth_headers_client):
    current_user = app.dependency_overrides[order_endpoint.get_current_user]()
    someone_else = uuid.uuid4()

    async def fake_get_me_id(_self, client_id, order_id):
        # Simulate not found for this user
        return None

    monkeypatch.setattr(order_service.OrderService, "getMeId", fake_get_me_id)

    res = client.get(f"/api/v1/order/me/{uuid.uuid4()}", headers=auth_headers_client)
    assert res.status_code == 404


def test_confirm_upload_validates_access(monkeypatch, auth_headers_client):
    # Arrange: order exists but belongs to a different client
    order_id = uuid.uuid4()
    other_client = uuid.uuid4()

    class OrderObj:
        def __init__(self, id, client_id):
            self.id = id
            self.client_id = client_id

    async def fake_get_id(_self, oid):
        return OrderObj(order_id, other_client)

    async def fake_save_record(_self, **kwargs):
        return SimpleNamespace(id=uuid.uuid4(), **kwargs)

    monkeypatch.setattr(order_service.OrderService, "getId", fake_get_id)
    monkeypatch.setattr(
        order_service.OrderService, "save_order_image_record", fake_save_record
    )

    payload = {
        "s3_object_path": "orders/obj.jpg",
        "s3_url": "https://example.com/download",
        "uploaded_by": str(uuid.uuid4()),
        "image_type": "before",
    }

    res = client.post(
        f"/api/v1/order/{order_id}/confirm-upload",
        json=payload,
        headers=auth_headers_client,
    )
    assert res.status_code == 403


def test_get_order_images_populates_fresh_urls(monkeypatch, auth_headers_client):
    # Arrange: order belongs to current user, images returned with s3_object_path -> s3_url is generated per image
    order_id = uuid.uuid4()

    current_user = app.dependency_overrides[order_endpoint.get_current_user]()

    class OrderObj:
        def __init__(self, id, client_id):
            self.id = id
            self.client_id = client_id

    class Img:
        def __init__(self, id, path):
            self.id = id
            self.s3_object_path = path
            self.s3_url = None

    async def fake_get_id(_self, oid):
        return OrderObj(order_id, current_user.id)

    async def fake_get_images(_self, oid):
        return [Img(uuid.uuid4(), "orders/a.jpg"), Img(uuid.uuid4(), "orders/b.jpg")]

    class FakeS3:
        def generate_download_url(self, path):
            return f"https://s3.local/{path}?token=abc"

    # Patch service and S3 client used inside endpoint
    monkeypatch.setattr(order_service.OrderService, "getId", fake_get_id)
    monkeypatch.setattr(order_service.OrderService, "getImages", fake_get_images)
    # Patch S3Service class used in endpoint scope
    import app.services.s3_service as s3_service_module

    monkeypatch.setattr(s3_service_module, "S3Service", FakeS3)

    # Act
    res = client.get(f"/api/v1/order/{order_id}/images", headers=auth_headers_client)

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["s3_url"].startswith("https://s3.local/orders/")
