import asyncio
import os
import sys
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.session import get_session as get_db
from app.main import app
from app.models.base import Base

# Point this to your local test container
TEST_DATABASE_URL = "postgresql+asyncpg://user:password@db_test:5432/test_db"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine_test, expire_on_commit=False, class_=AsyncSession
)


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        # This ensures PG-specific types like UUID and Enum work
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ... keep the override_get_db and client fixtures from before ...
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# @pytest.fixture(autouse=True)
# async def setup_db():
#     """Create a clean database for every test run."""
#     async with engine_test.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with engine_test.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Dependency Override: Tell FastAPI to use the Test DB
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async client for hitting endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
