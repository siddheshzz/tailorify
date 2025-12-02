from app.schemas.s3 import (
    UploadUrlSchemaOut,
)

from app.services.s3_service import S3Service



async def generate_presigned_upload_url(file_extension: str = "",
    content_type: str = "application/octet-stream") -> UploadUrlSchemaOut:
    """Generate presigned url for file upload directly to S3 storage."""
    s3_service: S3Service = S3Service()
    url, s3_object_path = s3_service.generate_presigned_upload_url()
    return UploadUrlSchemaOut(url=url, s3_object_path=s3_object_path)

