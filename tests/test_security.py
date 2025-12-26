import uuid
from datetime import datetime, timezone

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.core.security import (
    JWTBearer,
    RoleChecker,
    create_access_token,
    decode_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

app = FastAPI()


# Simple protected route for exercising JWTBearer and get_current_user
@app.get("/protected")
async def protected_route(payload: dict = Depends(JWTBearer())):
    return {"sub": payload.get("sub"), "exp": payload.get("exp")}


# Route protected by RoleChecker for ADMIN role
@app.get("/admin")
async def admin_only(user=Depends(RoleChecker(["admin"]))):
    return {"role": user.user_type}


client = TestClient(app)


@pytest.fixture
def valid_user_payload():
    return {
        "user_id": str(uuid.uuid4()),
        "user_email": "user@example.com",
        "user_type": "admin",
        "sub": "user@example.com",
    }


# 1. Password hashing behaviors


def test_password_hash_and_verify_roundtrip():
    pwd = "S3cureP@ss!"
    hashed = get_password_hash(pwd)
    assert hashed and isinstance(hashed, str)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False


# 2. Token creation and decoding behaviors


def test_create_and_decode_access_token_contains_exp(valid_user_payload):
    token = create_access_token(valid_user_payload)
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == valid_user_payload["sub"]
    # exp should be in the future at creation time
    assert int(payload["exp"]) >= int(datetime.now(timezone.utc).timestamp())


def test_decode_access_token_returns_none_on_invalid():
    assert decode_access_token("not.a.jwt") is None


# 3. JWTBearer behaviors


def test_jwtbearer_rejects_missing_header():
    res = client.get("/protected")
    assert res.status_code == 403


def test_jwtbearer_accepts_valid_token(valid_user_payload):
    token = create_access_token(valid_user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/protected", headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["sub"] == valid_user_payload["sub"]
    assert isinstance(body["exp"], int)


# 4. get_current_user behaviors


def test_get_current_user_builds_schema(valid_user_payload):
    token = create_access_token(valid_user_payload)
    headers = {"Authorization": f"Bearer {token}"}

    @app.get("/me")
    async def me(user=Depends(get_current_user)):
        return {"id": user.id, "email": user.email, "user_type": user.user_type}

    res = client.get("/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == valid_user_payload["user_id"]
    assert data["email"] == valid_user_payload["user_email"]
    assert data["user_type"] == valid_user_payload["user_type"]


def test_get_current_user_403_on_missing_fields():
    # missing user_id should trigger 403
    bad_payload = {"user_type": "client", "user_email": "a@b.com"}
    token = create_access_token(bad_payload)
    headers = {"Authorization": f"Bearer {token}"}

    @app.get("/me2")
    async def me2(user=Depends(get_current_user)):
        return {"id": user.id}

    res = client.get("/me2", headers=headers)
    assert res.status_code == 403


# 5. RoleChecker behaviors


def test_rolechecker_allows_admin(valid_user_payload):
    token = create_access_token(valid_user_payload)
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/admin", headers=headers)
    assert res.status_code == 200
    assert res.json()["role"] == "admin"


def test_rolechecker_forbids_when_role_not_allowed(valid_user_payload):
    # same user, but endpoint requires admin, and we switch to client role
    client_payload = {**valid_user_payload, "user_type": "client"}
    token = create_access_token(client_payload)
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/admin", headers=headers)
    assert res.status_code == 403
