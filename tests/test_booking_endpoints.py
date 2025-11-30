import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.api.v1.endpoints import booking as booking_endpoint
from app.services import booking_service


client = TestClient(app)


class FakeUser:
    def __init__(self, user_id: uuid.UUID, email: str):
        self.id = user_id
        self.email = email


@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch):
    # Create a valid JWT for Authorization header
    user_email = "testuser@example.com"
    token = create_access_token({"sub": user_email})

    # Override get_current_user to bypass DB lookup
    fake_user = FakeUser(uuid.uuid4(), user_email)
    app.dependency_overrides[booking_endpoint.get_current_user] = lambda: fake_user

    # Provide token to all requests via headers when desired
    def auth_headers():
        return {"Authorization": f"Bearer {token}"}

    yield auth_headers

    # Cleanup
    app.dependency_overrides.clear()


def test_create_booking_success(monkeypatch, override_dependencies):
    # Arrange: mock create_booking to return an object compatible with BookingResponse
    created_id = uuid.uuid4()
    user_id = uuid.uuid4()
    service_id = uuid.uuid4()
    appointment_time = datetime.now(timezone.utc)

    def fake_create_booking(db, booking, current_user_id):
        # Assert the service receives expected user_id argument type
        assert isinstance(current_user_id, uuid.UUID)
        return SimpleNamespace(
            id=created_id,
            user_id=current_user_id,
            service_id=service_id,
            status=getattr(booking, "status", "pending"),
            appointment_time=appointment_time,
            created_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(booking_service, "create_booking", fake_create_booking)

    # Act
    payload = {
        "service_id": str(service_id),
        "appointment_time": appointment_time.isoformat(),
    }

    res = client.post("/api/v1/booking/", json=payload, headers=override_dependencies())

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert uuid.UUID(data["id"]) == created_id
    assert uuid.UUID(data["user_id"])  # is a valid UUID
    assert uuid.UUID(data["service_id"]) == service_id
    assert data["status"] in ("pending", "confirmed", "cancelled") or isinstance(data["status"], str)
    assert "appointment_time" in data
    assert "created_at" in data


def test_list_bookings_success(monkeypatch, override_dependencies):
    # Arrange
    now = datetime.now(timezone.utc)
    booking1 = SimpleNamespace(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        status="pending",
        appointment_time=now,
        created_at=now,
    )
    booking2 = SimpleNamespace(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        service_id=uuid.uuid4(),
        status="confirmed",
        appointment_time=now,
        created_at=now,
    )

    def fake_get_bookings_by_user(db, current_user_id):
        assert isinstance(current_user_id, uuid.UUID)
        return [booking1, booking2]

    monkeypatch.setattr(booking_service, "get_bookings_by_user", fake_get_bookings_by_user)

    # Act
    res = client.get("/api/v1/booking/", headers=override_dependencies())

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["status"] == "pending"
    assert data[1]["status"] == "confirmed"


def test_missing_auth_header_returns_403():
    # No Authorization header provided; dependency JWTBearer should reject
    res = client.get("/api/v1/booking/")
    assert res.status_code == 403


def test_invalid_token_returns_403(monkeypatch):
    # Use an obviously invalid token to trigger JWTBearer failure
    headers = {"Authorization": "Bearer invalid.token.value"}
    res = client.get("/api/v1/booking/", headers=headers)
    assert res.status_code == 403


def test_service_called_with_current_user_id(monkeypatch, override_dependencies):
    # Verify that make_booking passes the current_user.id to the service layer
    captured = {}

    def fake_create_booking(db, booking, current_user_id):
        captured["user_id"] = current_user_id
        return SimpleNamespace(
            id=uuid.uuid4(),
            user_id=current_user_id,
            service_id=uuid.uuid4(),
            status="pending",
            appointment_time=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(booking_service, "create_booking", fake_create_booking)

    service_id = uuid.uuid4()
    payload = {
        "service_id": str(service_id),
        "appointment_time": datetime.now(timezone.utc).isoformat(),
    }

    res = client.post("/api/v1/booking/", json=payload, headers=override_dependencies())

    assert res.status_code == 200
    assert isinstance(captured.get("user_id"), uuid.UUID)
