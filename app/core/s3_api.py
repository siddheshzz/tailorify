# import uuid
# from app.core.exceptions import S3ObjectDoesntExistException
# from app.schemas.s3 import (
#     DownloanLinkSchemaOut,
#     UploadUrlSchemaOut,
# )

# from app.services.s3_service import S3Service


# async def generate_presigned_upload_url(file_extension: str = "",
#     content_type: str = "application/octet-stream") -> UploadUrlSchemaOut:
#     """Generate presigned url for file upload directly to S3 storage."""
#     s3_service: S3Service = S3Service()
#     url, s3_object_path = s3_service.generate_presigned_upload_url()
#     print("xxxxxxxx")
#     print("xxxxxxxx")
#     print("PRESIGNED_URL: ",url)
#     print("xxxxxxxx")
#     print("xxxxxxxx")


#     return UploadUrlSchemaOut(url=url, s3_object_path=s3_object_path)

# # async def upload_file_content(self, content: bytes, file_extension: str) -> str:
# #         """
# #         Upload raw file bytes directly to S3.
# #         """
# #         import io

# #         # Generate path: orders/2025/12/24/<uuid>.jpg
# #         s3_object_path = f"{self.__generate_upload_path()}{uuid.uuid4()}{file_extension}"

# #         try:
# #             # Convert bytes to a stream MinIO can read
# #             data_stream = io.BytesIO(content)

# #             self.internal_minio_client.put_object(
# #                 bucket_name=self.storage_configuration.S3_BUCKET_NAME,
# #                 object_name=s3_object_path,
# #                 data=data_stream,
# #                 length=len(content),
# #                 # No content_type needed, MinIO will infer or you can pass it
# #             )
# #             return s3_object_path
# #         except Exception as e:
# #             raise RuntimeError(f"Failed to upload to S3: {str(e)}")


# async def generate_download_url(
#    file_path: str,
# ) -> DownloanLinkSchemaOut:
#    """Generate presigned url for file download from S3 storage."""
#    s3_service: S3Service = S3Service()
#    download_link: str = s3_service.generate_download_url(file_path)
#    return DownloanLinkSchemaOut(download_link=download_link)
