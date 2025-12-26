import os
import uuid
from datetime import datetime, timedelta
from typing import Optional

from minio.error import S3Error
from urllib3 import ProxyManager

from app.core.config import settings as app_config
from app.services.storage.base import StorageServiceInterface
from minio import Minio


class MinIOStorageService(StorageServiceInterface):
    """MinIO implementation for local development"""

    def __init__(self):
        self.bucket_name = app_config.MINIO_BUCKET_NAME

        # Use internal endpoint for server-side operations
        self.client = Minio(
            app_config.MINIO_ENDPOINT,
            access_key=app_config.MINIO_ACCESS_KEY,
            secret_key=app_config.MINIO_SECRET_KEY,
            secure=app_config.MINIO_SECURE,
            http_client=ProxyManager(app_config.MINIO_INTERNAL_URL)
            if app_config.MINIO_USE_PROXY
            else None,
        )
        self.public_client = Minio(
            app_config.MINIO_EXTERNAL_ENDPOINT,  # localhost:9000 for browser
            access_key=app_config.MINIO_ACCESS_KEY,
            secret_key=app_config.MINIO_SECRET_KEY,
            secure=False,  # Use HTTP for local dev
        )

        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"✅ Created MinIO bucket: {self.bucket_name}")
        except S3Error as e:
            print(f"❌ Error checking/creating bucket: {e}")

    def generate_object_name(self, file_extension: str = "") -> str:
        """Generate unique object path: orders/YYYY/MM/DD/uuid.ext"""
        date_path = datetime.now().strftime("%Y/%m/%d")
        unique_id = str(uuid.uuid4())
        return f"orders/{date_path}/{unique_id}{file_extension}"

    def _get_content_type(self, file_path: str) -> str:
        """Determine content type from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return content_types.get(ext, "application/octet-stream")

    def upload_file(self, file_path, object_name: Optional[str] = None) -> str:
        """Upload file to MinIO"""
        if object_name is None:
            ext = os.path.splitext(file_path)[1]
            object_name = self.generate_object_name(ext)

        try:
            content_type = self._get_content_type(file_path)

            self.client.fput_object(
                self.bucket_name, object_name, file_path, content_type=content_type
            )
            return object_name
        except S3Error as e:
            raise Exception(f"Failed to upload to MinIO: {str(e)}")

    def download_file(self, object_name: str, file_path: str) -> str:
        """Download file from MinIO"""
        try:
            self.client.fget_object(self.bucket_name, object_name, file_path)
            return file_path
        except S3Error as e:
            raise Exception(f"Failed to download from MinIO: {str(e)}")

    # def get_file_stream(self, object_name: str):
    #     """Returns the raw byte stream from MinIO"""
    #     try:
    #         # get_object returns an HTTPResponse which is iterable
    #         return self.client.get_object(self.bucket_name, object_name)
    #     except S3Error as e:
    #         raise Exception(f"Failed to fetch from MinIO: {str(e)}")

    def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Failed to delete from MinIO: {str(e)}")
            return False

    def generate_presigned_download_url(
        self, object_name: str, expiry_minutes: int = 360
    ) -> str:
        """Generate presigned download URL"""
        try:
            url = self.client.presigned_get_object(
                self.bucket_name, object_name, expires=timedelta(minutes=expiry_minutes)
            )

            # Change internal endpoint with external endpoint for browser access
            if app_config.MINIO_USE_PROXY:
                url = url.replace(
                    app_config.MINIO_ENDPOINT,
                    app_config.MINIO_EXTERNAL_ENDPOINT
                )
            print(f"✅ Generated URL: {url}")
            return url
        except S3Error as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists"""
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False
