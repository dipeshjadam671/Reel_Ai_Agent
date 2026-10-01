from typing import Optional
from backend.app.core.config import settings
from backend.app.integrations.storage.base import StorageProvider
from backend.app.core.logging import logger

class S3StorageProvider(StorageProvider):
    def __init__(
        self,
        bucket_name: str = settings.S3_BUCKET_NAME,
        endpoint_url: Optional[str] = settings.S3_ENDPOINT_URL,
        region: str = settings.S3_REGION,
        access_key: Optional[str] = settings.S3_ACCESS_KEY_ID,
        secret_key: Optional[str] = settings.S3_SECRET_ACCESS_KEY,
    ):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key

    async def save_file(self, data: bytes, file_name: str, content_type: str = "application/octet-stream") -> str:
        # In mock or local fallback when S3 credentials not provided
        if not self.access_key or settings.MOCK_EXTERNAL_APIS:
            from backend.app.integrations.storage.local import LocalStorageProvider
            return await LocalStorageProvider().save_file(data, file_name, content_type)

        try:
            import boto3
            client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                region_name=self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=data,
                ContentType=content_type,
            )
            if self.endpoint_url:
                return f"{self.endpoint_url}/{self.bucket_name}/{file_name}"
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_name}"
        except Exception as e:
            logger.error(f"S3 upload error: {e}. Falling back to local storage.")
            from backend.app.integrations.storage.local import LocalStorageProvider
            return await LocalStorageProvider().save_file(data, file_name, content_type)

    async def get_file(self, file_path_or_url: str) -> bytes:
        if not self.access_key or settings.MOCK_EXTERNAL_APIS:
            from backend.app.integrations.storage.local import LocalStorageProvider
            return await LocalStorageProvider().get_file(file_path_or_url)
        import boto3
        client = boto3.client("s3", endpoint_url=self.endpoint_url, region_name=self.region)
        key = file_path_or_url.split("/")[-1]
        response = client.get_object(Bucket=self.bucket_name, Key=key)
        return response["Body"].read()

    async def delete_file(self, file_path_or_url: str) -> bool:
        if not self.access_key or settings.MOCK_EXTERNAL_APIS:
            from backend.app.integrations.storage.local import LocalStorageProvider
            return await LocalStorageProvider().delete_file(file_path_or_url)
        import boto3
        client = boto3.client("s3", endpoint_url=self.endpoint_url, region_name=self.region)
        key = file_path_or_url.split("/")[-1]
        client.delete_object(Bucket=self.bucket_name, Key=key)
        return True
