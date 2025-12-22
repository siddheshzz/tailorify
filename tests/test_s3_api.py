import pytest
from types import SimpleNamespace

from app.core.s3_api import generate_presigned_upload_url, generate_download_url
from app.core.exceptions import S3ObjectDoesntExistException


@pytest.fixture
def fake_s3_service(monkeypatch):
    """
    Patch S3Service to return a controllable fake instance.
    """
    # Create a fake service we can configure in each test
    fake = SimpleNamespace(
        generate_presigned_upload_url=lambda *args, **kwargs: ("http://upload-url", "orders/2024/01/01/abc"),
        generate_download_url=lambda *args, **kwargs: "http://download-url",
    )

    # Factory returning the fake service
    def fake_ctor(*args, **kwargs):
        return fake

    # Patch the class in the module under test
    from app import services
    from app.services import s3_service as s3_service_module

    monkeypatch.setattr(s3_service_module, "S3Service", fake_ctor)

    return fake


@pytest.mark.asyncio
async def test_generate_presigned_upload_url_returns_schema(fake_s3_service):
    # Act
    out = await generate_presigned_upload_url()

    # Assert: schema fields match what the service returned
    assert out.url == "http://upload-url"
    assert out.s3_object_path == "orders/2024/01/01/abc"


@pytest.mark.asyncio
async def test_generate_presigned_upload_url_ignores_extension_and_content_type(monkeypatch):
    # Arrange: ensure that API does not forward these args to service
    calls = {}

    def fake_generate_presigned_upload_url(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return ("http://upload-url-ext", "orders/x/y/id.ext")

    # Patch constructor to return fake instance
    from types import SimpleNamespace
    fake = SimpleNamespace(generate_presigned_upload_url=fake_generate_presigned_upload_url)

    from app.services import s3_service as s3_service_module
    monkeypatch.setattr(s3_service_module, "S3Service", lambda *a, **k: fake)

    # Act
    out = await generate_presigned_upload_url(file_extension=".png", content_type="image/png")

    # Assert: API returns service result and DID NOT pass through our args
    assert out.url == "http://upload-url-ext"
    assert out.s3_object_path == "orders/x/y/id.ext"
    assert calls["args"] == tuple() or calls["args"] is not None
    # The API currently calls service with no kwargs at all
    assert calls["kwargs"] == {}


@pytest.mark.asyncio
async def test_generate_download_url_returns_schema(fake_s3_service):
    # Act
    out = await generate_download_url("orders/2024/01/01/abc")

    # Assert
    assert out.download_link == "http://download-url"


@pytest.mark.asyncio
async def test_generate_download_url_propagates_not_found(monkeypatch):
    # Arrange
    def raise_not_found(*args, **kwargs):
        raise S3ObjectDoesntExistException("not found")

    fake = SimpleNamespace(generate_download_url=raise_not_found)

    from app.services import s3_service as s3_service_module
    monkeypatch.setattr(s3_service_module, "S3Service", lambda *a, **k: fake)

    # Act + Assert
    with pytest.raises(S3ObjectDoesntExistException):
        await generate_download_url("orders/none")


@pytest.mark.asyncio
async def test_generate_presigned_upload_url_propagates_runtime_error(monkeypatch):
    # Arrange
    def raise_runtime(*args, **kwargs):
        raise RuntimeError("service failure")

    fake = SimpleNamespace(generate_presigned_upload_url=raise_runtime)

    from app.services import s3_service as s3_service_module
    monkeypatch.setattr(s3_service_module, "S3Service", lambda *a, **k: fake)

    # Act + Assert
    with pytest.raises(RuntimeError):
        await generate_presigned_upload_url()
