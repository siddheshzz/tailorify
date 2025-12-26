from abc import ABC, abstractmethod
from typing import Optional


class StorageServiceInterface(ABC):
    """Abstract interface for storage services"""

    @abstractmethod
    def upload_file(self, file_path: str, object_name: Optional[str] = None) -> str:
        """
        Upload a file to storage.

        Args:
            file_path: Local path to file
            object_name: Optional custom object name

        Returns:
            S3 object path
        """
        pass

    @abstractmethod
    def download_file(self, object_name: str, file_path: str) -> str:
        """
        Download a file from storage.

        Args:
            object_name: Object name in storage
            file_path: Local path to save file

        Returns:
            Local file path
        """
        pass

    @abstractmethod
    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from storage.

        Args:
            object_name: Object name in storage

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    def generate_presigned_download_url(
        self, object_name: str, expiry_minutes: int = 360
    ) -> str:
        """
        Generate a presigned URL for downloading.

        Args:
            object_name: Object name in storage
            expiry_minutes: URL expiry time in minutes

        Returns:
            Presigned download URL
        """
        pass

    @abstractmethod
    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            object_name: Object name in storage

        Returns:
            True if file exists
        """
        pass

    @abstractmethod
    def generate_object_name(self, file_extension: str = "") -> str:
        """
        Generate a unique object name.

        Args:
            file_extension: File extension (e.g., '.jpg')

        Returns:
            Unique object name with path
        """
        pass
