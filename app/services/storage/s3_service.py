import os
import uuid
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings as app_config
from app.services.storage.base import StorageServiceInterface


class AWSS3StorageService(StorageServiceInterface):
    """AWS S3 implementation for production"""

    def __init__(self):
        self.bucket_name = app_config.AWS_S3_BUCKET_NAME

        print("🔧 Initializing AWS S3...")
        print(f"   Bucket: {self.bucket_name}")
        print(f"   Region: {app_config.AWS_REGION}")

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=app_config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=app_config.AWS_SECRET_ACCESS_KEY,
            region_name=app_config.AWS_REGION,
        )

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 bucket exists: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                # Create bucket
                try:
                    if app_config.AWS_REGION == "us-east-1":
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={
                                "LocationConstraint": app_config.AWS_REGION
                            },
                        )

                    # Set bucket policy for private access
                    self._set_bucket_policy()

                    print(f"✅ Created S3 bucket: {self.bucket_name}")
                except ClientError as create_error:
                    print(f"❌ Error creating bucket: {create_error}")

    def _set_bucket_policy(self):
        """Set bucket policy for secure access"""
        # Block public access
        try:
            self.s3_client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                },
            )
        except ClientError as e:
            print(f"⚠️ Could not set public access block: {e}")

    def generate_object_name(self, file_extension: str = "") -> str:
        """Generate unique object path"""
        date_path = datetime.now().strftime("%Y/%m/%d")
        unique_id = str(uuid.uuid4())
        return f"orders/{date_path}/{unique_id}{file_extension}"

    def upload_file(self, file_path: str, object_name: str = None) -> str:
        """Upload file to S3"""
        if object_name is None:
            ext = os.path.splitext(file_path)[1]
            object_name = self.generate_object_name(ext)

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                raise Exception(f"File not found: {file_path}")
            # Get file size
            file_size = os.path.getsize(file_path)
            print(f"📤 Uploading to S3: {object_name} ({file_size} bytes)")
            # Determine content type
            content_type = self._get_content_type(file_path)

            # Upload with progress
            with open(file_path, "rb") as file_data:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=file_data,
                    ContentType=content_type,
                    ServerSideEncryption="AES256",
                )

            print(f"✅ Uploaded to S3: {object_name}")

            # Verify upload
            if not self.file_exists(object_name):
                raise Exception("Upload verification failed")

            return object_name

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            print(f"❌ S3 Upload Error: {error_code} - {error_msg}")
            raise Exception(f"Failed to upload to S3: {error_msg}")
        except Exception as e:
            print(f"❌ Upload Error: {str(e)}")
            raise

        #     # Determine content type
        #     content_type = 'application/octet-stream'
        #     if ext := os.path.splitext(file_path)[1].lower():
        #         content_types = {
        #             '.jpg': 'image/jpeg',
        #             '.jpeg': 'image/jpeg',
        #             '.png': 'image/png',
        #             '.gif': 'image/gif',
        #             '.webp': 'image/webp'
        #         }
        #         content_type = content_types.get(ext, content_type)

        #     self.s3_client.upload_file(
        #         file_path,
        #         self.bucket_name,
        #         object_name,
        #         ExtraArgs={
        #             'ContentType': content_type,
        #             'ServerSideEncryption': 'AES256'  # Encrypt at rest
        #         }
        #     )
        #     return object_name
        # except ClientError as e:
        #     raise Exception(f"Failed to upload to S3: {str(e)}")

    def _get_content_type(self, file_path: str) -> str:
        """Determine content type"""
        ext = os.path.splitext(file_path)[1].lower()
        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return content_types.get(ext, "application/octet-stream")

    def download_file(self, object_name: str, file_path: str) -> str:
        """Download file from S3"""
        try:
            self.s3_client.download_file(self.bucket_name, object_name, file_path)
            return file_path
        except ClientError as e:
            raise Exception(f"Failed to download from S3: {str(e)}")

    def delete_file(self, object_name: str) -> bool:
        """Delete file from S3"""
        try:
            print("*********")
            print("IN AWS SERVICE,", object_name)

            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"Failed to delete from S3: {str(e)}")
            return False

    def generate_presigned_download_url(
        self, object_name: str, expiry_minutes: int = 360
    ) -> str:
        """Generate presigned download URL"""
        try:
            if not self.file_exists(object_name):
                raise Exception(f"File not found: {object_name}")

            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_name},
                ExpiresIn=expiry_minutes * 60,  # Convert to seconds
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError:
            return False
