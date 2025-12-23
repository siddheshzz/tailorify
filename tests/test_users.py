import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    payload = {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "strongpassword123",
        "phone": "1234567890"
    }
    response = await client.post("/api/v1/users/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_user_success(client: AsyncClient):
    # First, register a user manually in this test context
    # Then try to login
    login_payload = {
        "email": "testuser@example.com",
        "password": "strongpassword123"
    }
    response = await client.post("/api/v1/users/login", json=login_payload)
    assert response.status_code == 200