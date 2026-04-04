"""Service CRUD endpoint tests — admin-gated create/delete via JWTBearer + RoleChecker."""

import uuid
from types import SimpleNamespace

from app.core.dependencies import get_service
from app.core.security import get_current_user
from app.main import app


def _async(val):
    async def _fn(*_a, **_kw):
        return val

    return _fn


def _fake_svc(sid=None):
    return SimpleNamespace(
        id=sid or uuid.uuid4(),
        name="Hemming",
        description="Basic hem fix",
        base_price=150.0,
        category="alterations",
        estimated_days=2,
        image_url=None,
        is_active=True,
    )


class TestListServices:
    # def test_requires_auth(self, http_client):
    #     res = http_client.get("/api/v1/service/")
    #     assert res.status_code == 403

    def test_any_authenticated_user_can_list(
        self, http_client, client_headers, client_payload
    ):
        svcs = [_fake_svc(), _fake_svc()]
        app.dependency_overrides[get_current_user] = lambda: client_payload
        app.dependency_overrides[get_service] = lambda: SimpleNamespace(
            get=_async(svcs)
        )
        res = http_client.get("/api/v1/service/", headers=client_headers)
        assert res.status_code == 200
        assert len(res.json()) == 2


class TestGetService:
    def test_returns_service_by_id(
        self, http_client, client_headers, client_payload
    ):
        svc = _fake_svc()
        app.dependency_overrides[get_current_user] = lambda: client_payload
        app.dependency_overrides[get_service] = lambda: SimpleNamespace(
            getId=_async(svc)
        )
        res = http_client.get(f"/api/v1/service/{svc.id}", headers=client_headers)
        assert res.status_code == 200
        assert res.json()["name"] == "Hemming"


class TestCreateService:
    def test_admin_can_create(self, http_client, admin_headers, admin_payload):
        svc = _fake_svc()
        app.dependency_overrides[get_current_user] = lambda: admin_payload
        app.dependency_overrides[get_service] = lambda: SimpleNamespace(
            add=_async(svc)
        )
        res = http_client.post(
            "/api/v1/service/",
            json={
                "name": "Hemming",
                "base_price": 150.0,
                "category": "alterations",
                "estimated_days": 2,
            },
            headers=admin_headers,
        )
        assert res.status_code == 200
        assert res.json()["name"] == "Hemming"

    def test_client_is_rejected(
        self, http_client, client_headers, client_payload
    ):
        app.dependency_overrides[get_current_user] = lambda: client_payload
        res = http_client.post(
            "/api/v1/service/",
            json={
                "name": "X",
                "base_price": 10.0,
                "category": "y",
                "estimated_days": 1,
            },
            headers=client_headers,
        )
        assert res.status_code == 403


class TestUpdateService:
    def test_admin_can_update(self, http_client, admin_headers, admin_payload):
        svc = _fake_svc()
        svc.name = "Updated"
        app.dependency_overrides[get_current_user] = lambda: admin_payload
        app.dependency_overrides[get_service] = lambda: SimpleNamespace(
            update=_async(svc)
        )
        res = http_client.put(
            f"/api/v1/service/{svc.id}",
            json={
                "name": "Updated",
                "base_price": 200.0,
                "category": "premium",
                "estimated_days": 5,
            },
            headers=admin_headers,
        )
        assert res.status_code == 200


class TestDeleteService:
    def test_admin_can_delete(self, http_client, admin_headers, admin_payload):
        app.dependency_overrides[get_current_user] = lambda: admin_payload
        app.dependency_overrides[get_service] = lambda: SimpleNamespace(
            remove=_async(True)
        )
        res = http_client.delete(
            f"/api/v1/service/{uuid.uuid4()}", headers=admin_headers
        )
        assert res.status_code == 200

    def test_client_is_rejected(
        self, http_client, client_headers, client_payload
    ):
        app.dependency_overrides[get_current_user] = lambda: client_payload
        res = http_client.delete(
            f"/api/v1/service/{uuid.uuid4()}", headers=client_headers
        )
        assert res.status_code == 403
