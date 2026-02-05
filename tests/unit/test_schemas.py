"""Pydantic schema validation — no I/O, no DB, no network."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.booking import BookingCreate
from app.schemas.order import OrderCreate
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.schemas.user import UserCreate, UserUpdateSelf


# ---------------------------------------------------------------------------
# UserCreate
# ---------------------------------------------------------------------------
class TestUserCreateValidation:
    def _base(self, **overrides):
        return {
            "email": "user@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "Secure1234",
            "user_type": "client",
            **overrides,
        }

    def test_valid_payload(self):
        user = UserCreate(**self._base())
        assert user.email == "user@example.com"
        assert user.first_name == "Jane"
        assert user.user_type == "client"

    # -- password rules --
    def test_password_too_short(self):
        with pytest.raises(ValidationError, match="at least 8 characters"):
            UserCreate(**self._base(password="Ab1"))

    def test_password_no_digit(self):
        with pytest.raises(ValidationError, match="at least one digit"):
            UserCreate(**self._base(password="NoDigitsHere"))

    def test_password_no_letter(self):
        with pytest.raises(ValidationError, match="at least one letter"):
            UserCreate(**self._base(password="12345678"))

    # -- name rules --
    def test_blank_first_name(self):
        with pytest.raises(ValidationError, match="empty or just whitespace"):
            UserCreate(**self._base(first_name="   "))

    def test_blank_last_name(self):
        with pytest.raises(ValidationError, match="empty or just whitespace"):
            UserCreate(**self._base(last_name=""))

    # -- optional field coercion --
    def test_phone_whitespace_becomes_none(self):
        assert UserCreate(**self._base(phone="   ")).phone is None

    def test_address_whitespace_becomes_none(self):
        assert UserCreate(**self._base(address="  ")).address is None

    def test_phone_is_stripped(self):
        assert UserCreate(**self._base(phone=" +919876543210 ")).phone == "+919876543210"

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(**self._base(email="not-an-email"))


class TestUserUpdateSelfValidation:
    def test_all_fields_optional(self):
        # empty payload is valid for a partial update
        update = UserUpdateSelf()
        assert update.first_name is None
        assert update.password is None

    def test_partial_update_accepted(self):
        update = UserUpdateSelf(first_name="New")
        assert update.first_name == "New"
        assert update.last_name is None


# ---------------------------------------------------------------------------
# BookingCreate
# ---------------------------------------------------------------------------
class TestBookingCreateValidation:
    def test_valid_booking_defaults_status_to_pending(self):
        booking = BookingCreate(
            service_id=uuid4(),
            appointment_time=datetime.now(timezone.utc),
        )
        assert booking.status == "pending"

    def test_missing_service_id_raises(self):
        with pytest.raises(ValidationError):
            BookingCreate(appointment_time=datetime.now(timezone.utc))

    def test_missing_appointment_time_raises(self):
        with pytest.raises(ValidationError):
            BookingCreate(service_id=uuid4())


# ---------------------------------------------------------------------------
# OrderCreate
# ---------------------------------------------------------------------------
class TestOrderCreateValidation:
    def test_valid_order_defaults(self):
        order = OrderCreate(
            client_id=uuid4(),
            service_id=uuid4(),
            quoted_price=Decimal("99.99"),
        )
        assert order.status == "pending"
        assert order.priority == "normal"

    def test_missing_quoted_price_raises(self):
        with pytest.raises(ValidationError):
            OrderCreate(client_id=uuid4(), service_id=uuid4())

    def test_missing_client_id_raises(self):
        with pytest.raises(ValidationError):
            OrderCreate(service_id=uuid4(), quoted_price=Decimal("10.00"))

    def test_missing_service_id_raises(self):
        with pytest.raises(ValidationError):
            OrderCreate(client_id=uuid4(), quoted_price=Decimal("10.00"))


# ---------------------------------------------------------------------------
# ServiceCreate / ServiceUpdate
# ---------------------------------------------------------------------------
class TestServiceSchemaValidation:
    def _base(self, **overrides):
        return {
            "name": "Hemming",
            "base_price": 150.0,
            "category": "alterations",
            "estimated_days": 3,
            **overrides,
        }

    def test_valid_service_create(self):
        svc = ServiceCreate(**self._base())
        assert svc.is_active is True
        assert svc.image_url is None

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            ServiceCreate(base_price=100.0, category="x", estimated_days=1)

    def test_missing_base_price_raises(self):
        with pytest.raises(ValidationError):
            ServiceCreate(name="X", category="y", estimated_days=1)

    def test_update_accepts_all_fields(self):
        update = ServiceUpdate(**self._base(name="Updated", base_price=200.0))
        assert update.name == "Updated"
        assert update.base_price == 200.0
