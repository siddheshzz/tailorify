import os
import uuid
from datetime import timedelta

import pytest
from types import SimpleNamespace

from app.services.s3_service import S3Service, S3ServiceSettings
from minio import S3Error


class DummyS3Error(S3Error):
    def __init__(self, code: str, message: str = "", resource: str = "", request_id: str = "", host_id: str = "", response: object | None = None):
        # Minio S3Error signature: (method, bucket_name, object_name, response)
        super().__init__(code, message, resource, request_id)
        self.code = code


@pytest.fixture
def s3_settings(monkeypatch):
    # Provide deterministic settings to avoid env dependency
    settings = S3ServiceSettings(
        S3_BUCKET_NAME="test-bucket",
        S3_ENDPOINT="localhost:9000",
        S3_ACCESS_KEY="key",
        S3_SECRET_KEY="secret",
        S3_REGION="us-east-1",
        S3_REQUIRE_TLS=False,
        IS_PROXY_REQUIRED=False,
        S3_INTERNAL_URL="http://minio:9000",
    )
    return settings


@pytest.fixture
def service(s3_settings, monkeypatch):
    svc = S3Service(storage_configuration=s3_settings)
    # Replace real minio client with a simple namespace we can monkeypatch
    svc.minio_client = SimpleNamespace()
    return svc


def test_upload_calls_fput_and_returns_path(service, monkeypatch):
    called = {}

    def fake_fput(bucket, obj_path, file_name):
        called["bucket"] = bucket
        called["obj_path"] = obj_path
        called["file_name"] = file_name

    service.minio_client.fput_object = fake_fput

    path = service.upload("/tmp/file.txt")

    assert called["bucket"] == service.storage_configuration.S3_BUCKET_NAME
    assert called["file_name"] == "/tmp/file.txt"
    # Should generate a date-based prefix and uuid file name
    assert isinstance(path, str) and len(path) > 10
    assert called["obj_path"] == path


def test_download_validates_and_fetches_to_tmp(service, monkeypatch, tmp_path):
    # Arrange: stat_object passes, fget writes to tmp path
    def fake_stat(bucket, obj):
        return True

    created_local_files = {}

    def fake_fget(bucket, obj, local_path):
        created_local_files["local_path"] = local_path
        # Simulate file creation
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write("data")

    service.minio_client.stat_object = fake_stat
    service.minio_client.fget_object = fake_fget

    s3_obj = "orders/2024/01/01/abc"
    local = service.download(s3_obj)

    assert os.path.exists(local)
    assert created_local_files["local_path"].endswith("abc")


def test_download_raises_runtime_error_on_failure(service, monkeypatch):
    # stat ok then fget throws
    service.minio_client.stat_object = lambda bucket, obj: True

    def failing_fget(bucket, obj, path):
        raise RuntimeError("boom")

    service.minio_client.fget_object = failing_fget

    with pytest.raises(RuntimeError) as ei:
        service.download("orders/x/y/z")
    assert "Failed to download file" in str(ei.value)


def test_generate_download_url_happy_path(service, monkeypatch):
    # stat ok then presigned_get_object returns url
    service.minio_client.stat_object = lambda bucket, obj: True

    def fake_presign(bucket_name, object_name, expires, response_headers):
        assert bucket_name == service.storage_configuration.S3_BUCKET_NAME
        assert object_name.startswith("orders/")
        assert isinstance(expires, timedelta)
        assert "response-content-disposition" in response_headers
        return "http://example.com/presigned"

    service.minio_client.presigned_get_object = fake_presign

    url = service.generate_download_url("orders/2024/01/01/abc", desired_filename="file.jpg", expiration_minutes=10)
    assert url == "http://example.com/presigned"


def test_generate_download_url_raises_on_missing_object(service, monkeypatch):
    # stat throws NoSuchKey -> should translate to S3ObjectDoesntExistException
    from app.core.exceptions import S3ObjectDoesntExistException

    def fake_stat(bucket, obj):
        err = DummyS3Error(code="NoSuchKey")
        raise err

    service.minio_client.stat_object = fake_stat

    with pytest.raises(S3ObjectDoesntExistException):
        service.generate_download_url("orders/none")


def test_generate_presigned_upload_url_with_extension(service, monkeypatch):
    # When no s3_object_path provided and extension is given, ensure extension is used
    def fake_put(bucket_name, object_name, expires):
        assert object_name.endswith(".jpg")
        return "http://example.com/upload"

    service.minio_client.presigned_put_object = fake_put

    url, obj_path = service.generate_presigned_upload_url(s3_object_path=None, expiration_minutes=5, file_extension=".jpg")
    assert url == "http://example.com/upload"
    assert obj_path.endswith(".jpg")


def test_remove_digital_object_validates_then_removes(service, monkeypatch):
    called = {"validated": False, "removed": False}

    def fake_stat(bucket, obj):
        called["validated"] = True
        return True

    def fake_remove(bucket, obj):
        called["removed"] = True

    service.minio_client.stat_object = fake_stat
    service.minio_client.remove_object = fake_remove

    service.remove_digital_object("orders/2024/01/01/abc")

    assert called["validated"] is True
    assert called["removed"] is True
