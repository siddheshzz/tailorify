"""User registration / login / profile / admin-management endpoint tests."""

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from app.core.dependencies import get_user_service
from app.core.security import get_current_user
from app.main import app


def _async(val):
    async def _fn(*_a, **_kw):
        return val

    return _fn


def _user_ns(payload, **overrides):
    """Build a SimpleNamespace that satisfies UserResponse serialization."""
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=payload.id,
        email=payload.email,
        first_name=overrides.get("first_name", "Jane"),
        last_name=overrides.get("last_name", "Doe"),
        phone=None,
        address=None,
        user_type=payload.user_type,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
class TestRegister:
    def test_returns_token_on_success(self, http_client):
        fake_user = SimpleNamespace(
            id=uuid.uuid4(), user_type="client", email="new@test.com"
        )
        app.dependency_overrides[get_user_service] = lambda: SimpleNamespace(
            add=_async(fake_user)
        )

        res = http_client.post(
            "/api/v1/user/register",
            json={
                "email": "new@test.com",
                "first_name": "New",
                "last_name": "User",
                "password": "Secure123",
            },
        )
        assert res.status_code == 201
        assert "access_token" in res.json()
        assert res.json()["token_type"] == "bearer"

    def test_forces_client_role_regardless_of_input(self, http_client):
        captured = {}

        async def capture_add(user_data):
            captured["user_type"] = user_data.user_type
            return SimpleNamespace(
                id=uuid.uuid4(), user_type="client", email="x@x.com"
            )

        app.dependency_overrides[get_user_service] = lambda: SimpleNamespace(
            add=capture_add
        )

        http_client.post(
            "/api/v1/user/register",
            json={
                "email": "evil@test.com",
                "first_name": "Evil",
                "last_name": "Admin",
                "password": "Secure123",
                "user_type": "admin",  # attacker tries admin
            },
        )
        assert captured["user_type"].value == "client"

    def test_invalid_email_returns_422(self, http_client):
        res = http_client.post(
            "/api/v1/user/register",
            json={
                "email": "not-an-email",
                "first_name": "X",
                "last_name": "Y",
                "password": "Secure123",
            },
        )
        assert res.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
class TestLogin:
    def test_valid_credentials_return_token(self, http_client):
        fake_user = SimpleNamespace(
            id=uuid.uuid4(), email="me@test.com", user_type="client"
        )
        app.dependency_overrides[get_user_service] = lambda: SimpleNamespace(
            authenticate_user=_async(fake_user)
        )

        res = http_client.post(
            "/api/v1/user/login",
            json={"email": "me@test.com", "password": "Secure123"},
        )
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_invalid_credentials_return_401(self, http_client):
        app.dependency_overrides[get_user_service] = lambda: SimpleNamespace(
            authenticate_user=_async(None)
        )

        res = http_client.post(
            "/api/v1/user/login",
            json={"email": "bad@test.com", "password": "wrong"},
        )
        assert res.status_code == 401


# ---------------------------------------------------------------------------
# Profile (GET /me, PUT /me)
# ---------------------------------------------------------------------------
class TestMyProfile:
    def test_get_me_returns_profile(
        self, http_client, client_headers, client_payload
    ):
        app.dependency_overrides[get_current_user] = lambda: client_payload
        app.dependency_overrides[get_user_service] = lambda: SimpleNamespace(
            get=_async(_user_ns(client_payload))
        )

        res = http_client.get("/api/v1/user/me", headers=client_headers)
        assert res.status_code == 200
        assert res.json()["email"] == client_payload.email

    # def test_get_me_requires_auth(self, http_client):
    #     res = http_client.get("/api/v1/user/me")
    #     assert res.status_code == 403

    def test_update_me_returns_updated_profile(
        self, http_client, client_headers, client_payload
    ):
        updated = _user_ns(client_payload, first_name="Updated")
        app.dependency_overrides[get_current_user] = lambda: client_payload
        app.dependency_overrides[get_user_service] = lambda: SimpleNamespace(
            update_user_self_service=_async(updated)
        )

        res = http_client.put(
            "/api/v1/user/me", json={"first_name": "Updated"}, headers=client_headers
        )
        assert res.status_code == 200
        assert res.json()["first_name"] == "Updated"

    def test_update_me_404_when_user_not_found(
        self, http_client, client_headers, client_payload
    ):
        app.dependency_overrides[get_current_user] = lambda: client_payload
        app.dependency_overrides[get_user_service] = lambda: SimpleNamespace(
            update_user_self_service=_async(None)
        )

        res = http_client.put(
            "/api/v1/user/me", json={"first_name": "X"}, headers=client_headers
        )
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# Admin — list users / get by id
# ---------------------------------------------------------------------------
class TestAdminUsers:
    def test_list_users_rejects_client(
        self, http_client, client_headers, client_payload
    ):
        app.dependency_overrides[get_current_user] = lambda: client_payload
        res = http_client.get("/api/v1/user/", headers=client_headers)
        assert res.status_code == 403

    def test_list_users_admin_success(
        self, http_client, admin_headers, admin_payload
    ):
        now = datetime.now(timezone.utc)
        users = [
            SimpleNamespace(
                id=uuid.uuid4(),
                email="u1@test.com",
                first_name="U1",
                last_name="L1",
                phone=None,
                address=None,
                user_type="client",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        ]
        app.dependency_overrides[get_current_user] = lambda: admin_payload
        app.dependency_overrides[get_user_service] = lambda: SimpleNamespace(
            getAll=_async(users)
        )

        res = http_client.get("/api/v1/user/", headers=admin_headers)
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_get_user_by_id_admin(
        self, http_client, admin_headers, admin_payload
    ):
        uid = uuid.uuid4()
        now = datetime.now(timezone.utc)
        user = SimpleNamespace(
            id=uid,
            email="target@test.com",
            first_name="T",
            last_name="U",
            phone=None,
            address=None,
            user_type="client",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        app.dependency_overrides[get_current_user] = lambda: admin_payload
        app.dependency_overrides[get_user_service] = lambda: SimpleNamespace(
            get=_async(user)
        )

        res = http_client.get(f"/api/v1/user/{uid}", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["email"] == "target@test.com"
