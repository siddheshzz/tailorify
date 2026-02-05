"""UserService — mocked AsyncSession, no real DB."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.schemas.user import UserCreate, UserUpdateAdmin, UserUpdateSelf
from app.services.user_service import UserService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _mock_result(rows):
    """Mimics the object returned by session.execute(select(...))."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = rows
    result.scalars.return_value.first.return_value = rows[0] if rows else None
    result.scalar.return_value = rows[0] if rows else None
    result.scalar_one_or_none.return_value = rows[0] if rows else None
    return result


def _fake_user(uid=None, email="user@test.com"):
    user = MagicMock()
    user.id = uid or uuid4()
    user.email = email
    user.hashed_password = "hashed"
    user.first_name = "Test"
    user.last_name = "User"
    user.user_type = "client"
    user.is_active = True
    return user


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def service(session):
    return UserService(session)


# ---------------------------------------------------------------------------
# get / getAll / get_by_email
# ---------------------------------------------------------------------------
class TestUserServiceGet:
    async def test_get_returns_user_by_id(self, service, session):
        fake = _fake_user()
        session.get.return_value = fake
        assert await service.get(fake.id) is fake
        session.get.assert_awaited_once()

    async def test_get_returns_none_for_unknown_id(self, service, session):
        session.get.return_value = None
        assert await service.get(uuid4()) is None


class TestUserServiceGetAll:
    async def test_returns_list_of_users(self, service, session):
        users = [_fake_user(), _fake_user()]
        session.execute.return_value = _mock_result(users)
        assert await service.getAll() == users


class TestUserServiceGetByEmail:
    async def test_returns_user_when_found(self, service, session):
        fake = _fake_user(email="found@test.com")
        session.execute.return_value = _mock_result([fake])
        assert await service.get_by_email("found@test.com") is fake

    async def test_returns_none_when_not_found(self, service, session):
        session.execute.return_value = _mock_result([])
        assert await service.get_by_email("nope@test.com") is None


# ---------------------------------------------------------------------------
# add (register)
# ---------------------------------------------------------------------------
class TestUserServiceAdd:
    async def test_hashes_password_and_persists(self, service, session):
        payload = UserCreate(
            email="new@test.com",
            first_name="New",
            last_name="User",
            password="Secure123",
            user_type="client",
        )
        with patch(
            "app.services.user_service.get_password_hash", return_value="hashed_pw"
        ):
            await service.add(payload)

        session.add.assert_called_once()
        added_user = session.add.call_args[0][0]
        assert added_user.hashed_password == "hashed_pw"
        assert added_user.email == "new@test.com"
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once()


# ---------------------------------------------------------------------------
# authenticate_user
# ---------------------------------------------------------------------------
class TestUserServiceAuthenticate:
    async def test_returns_user_on_valid_credentials(self, service, session):
        fake = _fake_user()
        session.execute.return_value = _mock_result([fake])
        with patch("app.services.user_service.verify_password", return_value=True):
            result = await service.authenticate_user("user@test.com", "correct")
        assert result is fake

    async def test_returns_none_when_user_not_found(self, service, session):
        session.execute.return_value = _mock_result([])
        assert await service.authenticate_user("no@test.com", "pw") is None

    async def test_returns_none_on_wrong_password(self, service, session):
        fake = _fake_user()
        session.execute.return_value = _mock_result([fake])
        with patch("app.services.user_service.verify_password", return_value=False):
            result = await service.authenticate_user("user@test.com", "wrong")
        assert result is None


# ---------------------------------------------------------------------------
# update_user_self_service / update_user_admin_service
# ---------------------------------------------------------------------------
class TestUserServiceUpdate:
    async def test_update_self_executes_and_commits(self, service, session):
        fake = _fake_user()
        session.execute.return_value = _mock_result([fake])
        payload = UserUpdateSelf(first_name="Updated")
        result = await service.update_user_self_service(fake.id, payload)
        session.execute.assert_awaited_once()
        session.commit.assert_awaited_once()
        assert result is fake

    async def test_update_self_hashes_new_password(self, service, session):
        fake = _fake_user()
        session.execute.return_value = _mock_result([fake])
        payload = UserUpdateSelf(password="NewPass123")
        with patch(
            "app.services.user_service.get_password_hash", return_value="new_hash"
        ):
            await service.update_user_self_service(fake.id, payload)
        session.execute.assert_awaited_once()

    async def test_update_admin_executes_and_commits(self, service, session):
        fake = _fake_user()
        session.execute.return_value = _mock_result([fake])
        payload = UserUpdateAdmin(first_name="AdminSet")
        result = await service.update_user_admin_service(fake.id, payload)
        session.commit.assert_awaited_once()
        assert result is fake
