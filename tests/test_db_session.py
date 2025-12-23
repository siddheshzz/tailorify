import asyncio
from types import SimpleNamespace

import pytest

# Target module
import app.db.session as db_session


@pytest.fixture(autouse=True)
def restore_module_state():
    # Ensure we restore patched globals after each test
    orig_engine = db_session.engine
    orig_async_session_local = db_session.AsyncSessionLocal
    yield
    db_session.engine = orig_engine
    db_session.AsyncSessionLocal = orig_async_session_local


# def test_engine_configuration_uses_env_and_echo_toggle(monkeypatch):
#     calls = {}

#     class DummyEngine:
#         pass

#     def fake_create_async_engine(url, echo=False, pool_pre_ping=False, pool_size=None, max_overflow=None):
#         calls.update({
#             "url": url,
#             "echo": echo,
#             "pool_pre_ping": pool_pre_ping,
#             "pool_size": pool_size,
#             "max_overflow": max_overflow,
#         })
#         return DummyEngine()

#     # Patch sqlalchemy factory
#     monkeypatch.setattr(db_session, "create_async_engine", fake_create_async_engine)

#     # Patch settings
#     fake_settings = SimpleNamespace(DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db", ENVIRONMENT="development")
#     monkeypatch.setattr(db_session, "settings", fake_settings)

#     # Re-import style rebuild of globals in module under test
#     # Emulate the two-step engine creation performed in module
#     db_session.DATABASE_URL = fake_settings.DATABASE_URL
#     db_session.engine = db_session.create_async_engine(
#         db_session.DATABASE_URL,
#         echo=True,
#     )
#     db_session.engine = db_session.create_async_engine(
#         db_session.DATABASE_URL,
#         echo=fake_settings.ENVIRONMENT == "development",
#         pool_pre_ping=True,
#         pool_size=10,
#         max_overflow=20,
#     )

#     assert isinstance(db_session.engine, DummyEngine)
#     assert calls["url"] == fake_settings.DATABASE_URL
#     assert calls["echo"] is True  # because ENVIRONMENT == development
#     assert calls["pool_pre_ping"] is True
#     assert calls["pool_size"] == 10
#     assert calls["max_overflow"] == 20


def test_get_session_yields_async_session_and_closes_on_success(monkeypatch):
    events = {"entered": False, "exited": False, "closed": False}

    class DummyAsyncSession:
        def __init__(self):
            self.closed = False

        async def __aenter__(self):
            events["entered"] = True
            return self

        async def __aexit__(self, exc_type, exc, tb):
            events["exited"] = True

        async def rollback(self):
            pass

        async def close(self):
            events["closed"] = True
            self.closed = True

    def fake_sessionmaker(**kwargs):
        # Return a callable that produces our DummyAsyncSession and supports async context manager via __aenter__/__aexit__
        def factory():
            return DummyAsyncSession()
        return factory

    monkeypatch.setattr(db_session, "AsyncSessionLocal", fake_sessionmaker())

    async def run():
        agen = db_session.get_session()
        session = None
        async for s in agen:
            session = s
            break
        assert isinstance(session, DummyAsyncSession)

    asyncio.get_event_loop().run_until_complete(run())

    assert events["entered"] is True
    assert events["exited"] is True
    assert events["closed"] is True


def test_get_session_rolls_back_and_closes_on_exception(monkeypatch):
    events = {"rolled_back": False, "closed": False}

    class DummyAsyncSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False  # do not suppress

        async def rollback(self):
            events["rolled_back"] = True

        async def close(self):
            events["closed"] = True

    class ExplodingIterator:
        def __init__(self, session):
            self.session = session
            self.yielded = False

        def __aiter__(self):
            return self

        async def __anext__(self):
            if not self.yielded:
                self.yielded = True
                # Simulate exception in consumer after first yield
                raise RuntimeError("consumer failure")
            raise StopAsyncIteration

    def fake_sessionmaker(**kwargs):
        def factory():
            return DummyAsyncSession()
        return factory

    monkeypatch.setattr(db_session, "AsyncSessionLocal", fake_sessionmaker())

    async def consume_with_exception():
        agen = db_session.get_session()
        # Enter the context and then trigger exception to exercise rollback path
        try:
            # Advance to first yield to create session
            async for _ in agen:
                # immediately raise to trigger except/finally in get_session
                raise RuntimeError("force error")
        except RuntimeError:
            pass

    asyncio.get_event_loop().run_until_complete(consume_with_exception())

    assert events["rolled_back"] is True
    assert events["closed"] is True
