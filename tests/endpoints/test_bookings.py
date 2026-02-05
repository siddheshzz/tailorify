"""Booking endpoint tests — dependency-overridden services, real JWT tokens."""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from app.core.dependencies import get_booking_service
from app.core.security import get_current_user
from app.main import app


def _async(val):
    async def _fn(*_a, **_kw):
        return val

    return _fn


class TestCreateBooking:
    def test_success_returns_booking(self, http_client, client_headers, client_payload):
        booking = SimpleNamespace(
            id=uuid.uuid4(),
            user_id=uuid.UUID(client_payload.id),
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        app.dependency_overrides[get_current_user] = lambda: client_payload
        app.dependency_overrides[get_booking_service] = lambda: SimpleNamespace(
            add=_async(booking)
        )

        res = http_client.post(
            "/api/v1/booking/",
            json={
                "service_id": str(uuid.uuid4()),
                "appointment_time": datetime.now(timezone.utc).isoformat(),
            },
            headers=client_headers,
        )
        assert res.status_code == 200
        assert res.json()["status"] == "pending"

    # def test_requires_auth(self, http_client):
    #     res = http_client.post(
    #         "/api/v1/booking/",
    #         json={
    #             "service_id": str(uuid.uuid4()),
    #             "appointment_time": datetime.now(timezone.utc).isoformat(),
    #         },
    #     )
    #     assert res.status_code == 403

    def test_invalid_payload_returns_422(
        self, http_client, client_headers, client_payload
    ):
        app.dependency_overrides[get_current_user] = lambda: client_payload
        app.dependency_overrides[get_booking_service] = lambda: SimpleNamespace(
            add=_async(None)
        )
        # missing both required fields
        res = http_client.post("/api/v1/booking/", json={}, headers=client_headers)
        assert res.status_code == 422


class TestListBookings:
    def test_returns_user_bookings(
        self, http_client, client_headers, client_payload
    ):
        now = datetime.now(timezone.utc)
        bookings = [
            SimpleNamespace(
                id=uuid.uuid4(),
                user_id=uuid.UUID(client_payload.id),
                status="pending",
                created_at=now,
            ),
            SimpleNamespace(
                id=uuid.uuid4(),
                user_id=uuid.UUID(client_payload.id),
                status="confirmed",
                created_at=now,
            ),
        ]
        app.dependency_overrides[get_current_user] = lambda: client_payload
        app.dependency_overrides[get_booking_service] = lambda: SimpleNamespace(
            get_bookings_by_user=_async(bookings)
        )

        res = http_client.get("/api/v1/booking/", headers=client_headers)
        assert res.status_code == 200
        assert len(res.json()) == 2

    # def test_requires_auth(self, http_client):
    #     res = http_client.get("/api/v1/booking/")
    #     assert res.status_code == 403

    def test_empty_list(self, http_client, client_headers, client_payload):
        app.dependency_overrides[get_current_user] = lambda: client_payload
        app.dependency_overrides[get_booking_service] = lambda: SimpleNamespace(
            get_bookings_by_user=_async([])
        )
        res = http_client.get("/api/v1/booking/", headers=client_headers)
        assert res.status_code == 200
        assert res.json() == []
