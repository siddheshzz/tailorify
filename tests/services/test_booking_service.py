"""BookingService — mocked AsyncSession, no real DB."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.schemas.booking import BookingCreate
from app.services.booking_service import BookingService


def _mock_result(rows):
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    return result


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def service(session):
    return BookingService(session)


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------
class TestBookingServiceAdd:
    async def test_creates_booking_with_correct_user_id(self, service, session):
        user_id = uuid4()
        svc_id = uuid4()
        payload = BookingCreate(
            service_id=svc_id,
            appointment_time=datetime.now(timezone.utc),
        )

        await service.add(payload, user_id)

        session.add.assert_called_once()
        booking_obj = session.add.call_args[0][0]
        assert booking_obj.user_id == user_id
        assert booking_obj.service_id == svc_id
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once()

    async def test_returns_persisted_booking(self, service, session):
        result = await service.add(
            BookingCreate(
                service_id=uuid4(),
                appointment_time=datetime.now(timezone.utc),
            ),
            uuid4(),
        )
        # refresh is called on the returned object
        assert result is not None
        session.refresh.assert_awaited_once_with(result)


# ---------------------------------------------------------------------------
# get_bookings_by_user
# ---------------------------------------------------------------------------
class TestBookingServiceList:
    async def test_returns_bookings_for_user(self, service, session):
        bookings = [MagicMock(), MagicMock()]
        session.execute.return_value = _mock_result(bookings)
        assert await service.get_bookings_by_user(uuid4()) == bookings

    async def test_returns_empty_list_when_none(self, service, session):
        session.execute.return_value = _mock_result([])
        assert await service.get_bookings_by_user(uuid4()) == []
