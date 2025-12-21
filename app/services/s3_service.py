import os
import uuid
from datetime import datetime
from datetime import timedelta

from minio import Minio
from minio import S3Error
from pydantic import BaseModel
from urllib3 import ProxyManager

from app.core.exceptions import S3ObjectDoesntExistException
from app.core.config import settings


class S3ServiceSettings(BaseModel):
    """
    S3 client settings
    """

    S3_BUCKET_NAME: str = settings.S3_BUCKET_NAME
    # External S3 endpoint
    S3_ENDPOINT: str = settings.S3_EXTERNAL_HOST
    S3_ACCESS_KEY: str = settings.S3_ACCESS_KEY
    S3_SECRET_KEY: str = settings.S3_SECRET_KEY
    S3_REGION: str = settings.S3_REGION
    S3_REQUIRE_TLS: bool = settings.S3_REQUIRE_TLS
    # Proxy is required in local environment with docker compose
    IS_PROXY_REQUIRED: bool = settings.IS_PROXY_REQUIRED
    # Internal docker URL. To set if IS_PROXY_REQUIRED=True
    S3_INTERNAL_URL: str = settings.S3_INTERNAL_URL


class S3Service:
    """
    Class that provides a façade for application to access the underlying S3 storage.
    """

    storage_configuration: S3ServiceSettings
    minio_client: Minio
    tmp_path: str

    def __init__(self, storage_configuration: S3ServiceSettings | None = None):
        if storage_configuration is None:
            storage_configuration = S3ServiceSettings()
        self.storage_configuration = storage_configuration
        self.minio_client = Minio(
            self.storage_configuration.S3_ENDPOINT,
            access_key=self.storage_configuration.S3_ACCESS_KEY,
            secret_key=self.storage_configuration.S3_SECRET_KEY,
            region=self.storage_configuration.S3_REGION,
            secure=self.storage_configuration.S3_REQUIRE_TLS,
            http_client=ProxyManager(self.storage_configuration.S3_INTERNAL_URL)
            if self.storage_configuration.IS_PROXY_REQUIRED
            else None,
        )
        self.tmp_path: str = "./tmp"

    def __generate_upload_path(self) -> str:
        """
        Generate a directory path based on the current date.

        Returns:
        - str: A string representing the directory path in the format "YYYY/MM/DD/".
        """
        current_yyyy_mm_dd: str = datetime.now().strftime("%Y/%m/%d")
        path: str = "orders/"+current_yyyy_mm_dd + "/"
        return path

    def __generate_upload_path_with_file_name(self) -> str:
        """
        Generate a unique S3 object path with a file name.

        Combines the current date directory path with a UUID as the file name.

        Returns:
        - str: A string representing the full S3 object path in the format "YYYY/MM/DD/<UUID>".
        """
        s3_object_file_name: str = str(uuid.uuid4())
        s3_object_path = f"{self.__generate_upload_path()}{s3_object_file_name}"
        return s3_object_path

    def __validate_object_existance(self, s3_object_path: str) -> None:
        """
        Validate the existence of an object in the S3 bucket.

        Checks if the object with the given path exists in the configured S3 bucket.
        If the object does not exist, raises an `S3ObjectDoesntExistException`.

        Parameters:
        - s3_object_path (str): The path of the object in the S3 bucket to validate.

        Raises:
        - S3ObjectDoesntExistException: If the object does not exist in the S3 bucket.
        - S3Error: For other S3-related errors.
        """
        try:
            self.minio_client.stat_object(
                self.storage_configuration.S3_BUCKET_NAME, s3_object_path
            )
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise S3ObjectDoesntExistException(
                    f"The S3 object with path='{s3_object_path}' does not exist in the bucket."
                ) from e
            raise

    def remove_digital_object(self, s3_object_path: str) -> None:
        """
        Removes a digital object from the S3 bucket.

        Parameters:
        - s3_object_path (str): The path of the digital object to be removed in the S3 bucket.

        Raises:
        - FileNotFoundError: If the specified object does not exist in the bucket.
        - S3Error: If there is an issue with the S3-compatible storage service.
        """
        self.__validate_object_existance(s3_object_path=s3_object_path)
        self.minio_client.remove_object(
            self.storage_configuration.S3_BUCKET_NAME, s3_object_path
        )

    def upload(self, file_name: str) -> str:
        """
        Upload file to S3 storage.

        Parameters:
        - file_name (str): relative path to file to upload
        """
        s3_object_path: str = self.__generate_upload_path_with_file_name()
        self.minio_client.fput_object(
            self.storage_configuration.S3_BUCKET_NAME, s3_object_path, file_name
        )
        return s3_object_path

    def download(self, s3_object_path: str, local_file_name: str | None = None) -> str:
        """
        Download a file from S3 storage to the tmp directory.

        Parameters:
        - object_name (str): The path of the object in the S3 store (including file name).
        - local_file_name (str, optional): Name of the local file to save. Defaults to the object's
          name.

        Returns:
        - str: The path to the downloaded file in the local tmp directory.
        """
        self.__validate_object_existance(s3_object_path=s3_object_path)
        file_name_to_create: str = (
            local_file_name if local_file_name else os.path.basename(s3_object_path)
        )
        local_file_path: str = os.path.join(self.tmp_path, file_name_to_create)
        try:
            self.minio_client.fget_object(
                self.storage_configuration.S3_BUCKET_NAME,
                s3_object_path,
                local_file_path,
            )
            return local_file_path
        except Exception as e:
            raise RuntimeError(
                f"Failed to download file '{s3_object_path}': {str(e)}"
            ) from e

    def generate_download_url(
        self,
        s3_object_path: str,
        desired_filename: str | None = None,
        expiration_minutes: int = 360,
    ) -> str:
        """
        Generate a pre-signed URL for downloading an object from S3 with a specific filename.

        Parameters:
        - s3_object_path (str): The path of the object in the S3 bucket.
        - desired_filename (str | None, optional): The filename the user should see when
          downloading the file.
        - expiration_minutes (int): The validity duration of the pre-signed URL in minutes.

        Returns:
        - (str): A pre-signed URL to download the object.
        """
        self.__validate_object_existance(s3_object_path=s3_object_path)
        file_name: str = (
            desired_filename if desired_filename else os.path.basename(s3_object_path)
        )
        response_headers: dict[str, str] = {
            "response-content-disposition": f"attachment; filename={file_name}"
        }
        try:
            presigned_url: str = self.minio_client.presigned_get_object(
                bucket_name=self.storage_configuration.S3_BUCKET_NAME,
                object_name=s3_object_path,
                expires=timedelta(minutes=expiration_minutes),
                response_headers=response_headers,  # type: ignore
            )
            return presigned_url
        except Exception as e:
            raise RuntimeError(f"Failed to generate download link: {str(e)}") from e

    def generate_presigned_upload_url(
        self, s3_object_path: str | None = None, expiration_minutes: int = 360, file_extension: str = ""
    ) -> tuple[str, str]:
        """
        Generate a pre-signed URL for uploading files directly from the frontend.

        Parameters:
        - s3_object_path (str, optional): The path of the object in S3 (including file name).
        - expiration_minutes (int): The number of minutes the pre-signed URL is valid for.

        Returns:
        - (tuple(str, str)): The pre-signed URL for file upload and s3_object_path
        """
        # if s3_object_path is None:
        #     s3_object_path = self.__generate_upload_path_with_file_name()

        if s3_object_path is None:
        # Generate path with extension if provided
            if file_extension:
                s3_object_path = self.__generate_upload_path() + str(uuid.uuid4()) + file_extension
            else:
                s3_object_path = self.__generate_upload_path_with_file_name()
    
        try:
            presigned_url = self.minio_client.presigned_put_object(
                bucket_name=self.storage_configuration.S3_BUCKET_NAME,
                object_name=s3_object_path,
                expires=timedelta(minutes=expiration_minutes),
            )
            return presigned_url, s3_object_path
        except Exception as e:
            raise RuntimeError(f"Failed to generate pre-signed URL: {str(e)}") from e
