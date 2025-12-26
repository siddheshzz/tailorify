from app.core.config import settings as app_config
from app.services.storage.base import StorageServiceInterface
from app.services.storage.minio_service import MinIOStorageService
from app.services.storage.s3_service import AWSS3StorageService


class StorageServiceFactory:
    """Factory to create appropriate storage service based on configuration"""

    @staticmethod
    def create() -> StorageServiceInterface:
        """
        Create and return the appropriate storage service.

        Returns:
            StorageServiceInterface implementation
        """
        if app_config.STORAGE_BACKEND == "s3":
            print("🌐 Using AWS S3 for storage")
            return AWSS3StorageService()
        else:
            print("🏠 Using MinIO for storage")
            return MinIOStorageService()


# Singleton instance
_storage_service: StorageServiceInterface = None


def get_storage_service() -> StorageServiceInterface:
    """Get singleton storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageServiceFactory.create()
    return _storage_service
