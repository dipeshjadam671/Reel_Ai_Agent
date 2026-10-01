from typing import Protocol, runtime_checkable

@runtime_checkable
class StorageProvider(Protocol):
    async def save_file(self, data: bytes, file_name: str, content_type: str = "application/octet-stream") -> str:
        ...

    async def get_file(self, file_path_or_url: str) -> bytes:
        ...

    async def delete_file(self, file_path_or_url: str) -> bool:
        ...
