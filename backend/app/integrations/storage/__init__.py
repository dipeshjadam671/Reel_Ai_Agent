from backend.app.core.config import settings
from backend.app.integrations.storage.base import StorageProvider
from backend.app.integrations.storage.local import LocalStorageProvider
from backend.app.integrations.storage.s3 import S3StorageProvider

def get_storage_provider() -> StorageProvider:
    if settings.STORAGE_BACKEND == "s3" and settings.S3_ACCESS_KEY_ID:
        return S3StorageProvider()
    return LocalStorageProvider()
