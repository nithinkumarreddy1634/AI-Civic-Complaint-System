"""Storage abstraction layer for uploaded media assets and files."""
import os
import uuid
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from app.config import get_settings


class FileStorage(ABC):
    """Abstract storage interface enabling local disk or cloud object storage."""

    @abstractmethod
    def save(self, content: bytes, original_filename: str, subfolder: str = "") -> Tuple[str, str]:
        """Save file bytes and return (storage_path, unique_filename)."""
        pass

    @abstractmethod
    def get(self, path: str) -> Optional[bytes]:
        """Retrieve file bytes from storage path."""
        pass

    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete file from storage path."""
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if file exists in storage path."""
        pass


class LocalFileStorage(FileStorage):
    """Local filesystem implementation of FileStorage."""

    def __init__(self, base_dir: Optional[str] = None):
        settings = get_settings()
        self.base_dir = os.path.abspath(base_dir or settings.UPLOAD_DIR)
        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, content: bytes, original_filename: str, subfolder: str = "") -> Tuple[str, str]:
        # Validate path traversal prevention
        clean_ext = os.path.splitext(original_filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{clean_ext}"

        target_dir = os.path.join(self.base_dir, subfolder) if subfolder else self.base_dir
        # Ensure target_dir is strictly within self.base_dir
        real_target = os.path.abspath(target_dir)
        if not real_target.startswith(self.base_dir):
            raise ValueError("Path traversal attempt detected in storage subfolder.")

        os.makedirs(real_target, exist_ok=True)
        file_path = os.path.join(real_target, unique_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        return file_path, unique_filename

    def get(self, path: str) -> Optional[bytes]:
        real_path = os.path.abspath(path)
        if not os.path.exists(real_path) or not os.path.isfile(real_path):
            return None
        with open(real_path, "rb") as f:
            return f.read()

    def delete(self, path: str) -> bool:
        real_path = os.path.abspath(path)
        if os.path.exists(real_path) and os.path.isfile(real_path):
            try:
                os.remove(real_path)
                return True
            except OSError:
                return False
        return False

    def exists(self, path: str) -> bool:
        return os.path.exists(os.path.abspath(path)) and os.path.isfile(os.path.abspath(path))


file_storage = LocalFileStorage()
