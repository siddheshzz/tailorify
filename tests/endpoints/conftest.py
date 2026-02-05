"""Shared fixtures for all endpoint tests.

Provides:
  - admin / client user payloads & JWT headers
  - http_client  — TestClient that auto-clears dependency overrides after each test
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app
from app.schemas.user import UserAuthPayload


# ---------------------------------------------------------------------------
# Stable IDs
# ---------------------------------------------------------------------------
@pytest.fixture
def admin_id():
    return uuid.uuid4()


@pytest.fixture
def client_id():
    return uuid.uuid4()


# ---------------------------------------------------------------------------
# Auth payloads
# ---------------------------------------------------------------------------
@pytest.fixture
def admin_payload(admin_id):
    return UserAuthPayload(
        id=str(admin_id), email="admin@tailorify.com", user_type="admin"
    )


@pytest.fixture
def client_payload(client_id):
    return UserAuthPayload(
        id=str(client_id), email="client@tailorify.com", user_type="client"
    )


# ---------------------------------------------------------------------------
# Tokens & headers (real JWTs — JWTBearer will accept these)
# ---------------------------------------------------------------------------
@pytest.fixture
def admin_token(admin_payload):
    return create_access_token(
        {
            "user_id": admin_payload.id,
            "user_email": admin_payload.email,
            "user_type": admin_payload.user_type,
        }
    )


@pytest.fixture
def client_token(client_payload):
    return create_access_token(
        {
            "user_id": client_payload.id,
            "user_email": client_payload.email,
            "user_type": client_payload.user_type,
        }
    )


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def client_headers(client_token):
    return {"Authorization": f"Bearer {client_token}"}


# ---------------------------------------------------------------------------
# HTTP client — dependency overrides are cleared after every test
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _reset_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def http_client():
    with TestClient(app) as c:
        yield c
