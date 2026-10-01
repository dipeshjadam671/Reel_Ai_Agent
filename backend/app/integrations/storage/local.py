import os
from pathlib import Path
from backend.app.core.config import settings
from backend.app.integrations.storage.base import StorageProvider

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_path: str = settings.LOCAL_STORAGE_PATH):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(self, data: bytes, file_name: str, content_type: str = "application/octet-stream") -> str:
        target_path = self.base_path / file_name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(data)
        return str(target_path)

    async def get_file(self, file_path_or_url: str) -> bytes:
        if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
            import httpx
            import asyncio
            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(timeout=45.0, follow_redirects=True) as client:
                        res = await client.get(
                            file_path_or_url,
                            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                        )
                        if res.status_code == 200:
                            return res.content
                        if attempt == 2:
                            raise FileNotFoundError(f"Failed to fetch remote media: {file_path_or_url} (status {res.status_code})")
                except Exception as e:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1.0)

        if os.path.exists(file_path_or_url):
            with open(file_path_or_url, "rb") as f:
                return f.read()

        path = self.base_path / file_path_or_url
        with open(path, "rb") as f:
            return f.read()

    async def delete_file(self, file_path_or_url: str) -> bool:
        path = Path(file_path_or_url)
        if not path.is_absolute():
            path = self.base_path / file_path_or_url
        if path.exists():
            path.unlink()
            return True
        return False
