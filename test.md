1. Environment bootstrap — tests/conftest.py

Before any app code is imported, this file sets env vars via os.environ.setdefault. This is critical because app/core/config.py instantiates Settings() at module load time — if the vars aren't set by then, Pydantic raises a validation error. ENABLE_CACHING=False and ENABLE_EMAIL_NOTIFICATIONS=False disable Redis and Celery/Resend so tests never touch external services.

2. The three layers and what they isolate


unit/        → no I/O at all.  Tests pure logic: validation, hashing, token encode/decode.
services/    → mocks the DB session.  Tests service method logic in isolation.
endpoints/   → mocks the services.  Tests HTTP routing, auth gates, and response shape.
Each layer mocks exactly one boundary below it, and nothing else. This keeps tests fast and failures narrow — a service test failure tells you the bug is in the service, not the endpoint or the DB.

3. How endpoint tests work (the layer you're looking at)

There are two mechanisms at play: real JWTs and dependency overrides.

Real JWTs — tests/endpoints/conftest.py

The fixtures call create_access_token from the actual app. This produces real, valid tokens. The routes have dependencies=[Depends(JWTBearer())], which is not overridden — it runs for real. So when a test sends no Authorization header, JWTBearer genuinely rejects it with 403. This is why test_requires_auth tests actually validate the auth gate rather than just asserting against a mock.

Dependency overrides — how FastAPI's DI is swapped

app.dependency_overrides is a dict on the FastAPI app instance. When you do:


app.dependency_overrides[get_current_user] = lambda: client_payload
FastAPI replaces every Depends(get_current_user) call in that request with the lambda's return value. The real get_current_user (which would decode the JWT and hit the DB) never runs. This is how the test controls who the logged-in user is.

The same pattern swaps the service layer. Look at test_services.py:41-42:


app.dependency_overrides[get_service] = lambda: SimpleNamespace(
    get=_async(svcs)
)
get_service is the dependency that normally creates a ServiceService backed by a real DB session. The override replaces it with a SimpleNamespace that has a get attribute — an async function that just returns the pre-built svcs list. The route calls service.get(), gets the fake data, and serializes it. No DB involved.

Cleanup — tests/endpoints/conftest.py:86-89

The _reset_overrides fixture is autouse=True (runs for every test automatically). It yields (does nothing on setup), then calls app.dependency_overrides.clear() on teardown. This ensures one test's overrides don't leak into the next.

4. The _async helper

Every service method the routes call is async. A plain lambda: svcs would fail because the route does await service.get(). So _async(val) wraps any value in an async function:


def _async(val):
    async def _fn(*_a, **_kw):
        return val
    return _fn
It accepts and ignores any arguments, so it works regardless of what the route passes in.

5. How service tests work (one layer down)

Instead of dependency overrides, these use unittest.mock.AsyncMock as a fake DB session. Look at tests/services/test_order_service.py:


@pytest.fixture
def session():
    return AsyncMock()

@pytest.fixture
def service(session):
    return OrderService(session)
OrderService is instantiated with a mock session. When the service calls self.session.execute(...), AsyncMock records the call and returns whatever .return_value was set to. The _mock_result helper mimics SQLAlchemy's result chain (.scalars().all(), .scalar_one_or_none(), etc.) so the service code sees the same interface it would with a real DB.

6. How unit tests work (top layer)

No mocks at all for the pure logic tests. test_schemas.py just instantiates Pydantic models with various inputs and asserts validation passes or raises. test_security.py calls get_password_hash / verify_password directly. test_db_session.py is the one exception — it monkeypatches AsyncSessionLocal with a DummyAsyncSession and uses the async generator protocol (__anext__, aclose, athrow) to exercise the exact same flow FastAPI uses when consuming a yield-based dependency.

7. The one thing the tests flagged in your app code

test_services.py:132-144 — the DELETE /{id} route on the service endpoint has Depends(JWTBearer()) but no Depends(allow_admin). The test documents that any authenticated user can delete, which is likely unintentional given that POST / (create) is admin-gated. If you want to lock it down, add Depends(allow_admin) to that route in app/api/v1/endpoints/service.py:38.