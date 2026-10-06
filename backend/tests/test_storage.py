"""Tests for FileStorage abstraction and LocalFileStorage."""
import os
import pytest
from app.services.storage import LocalFileStorage


@pytest.fixture
def storage(tmp_path):
    return LocalFileStorage(base_dir=str(tmp_path))


def test_save_and_retrieve_file(storage):
    data = b"CivicAI test image bytes content"
    saved_path, filename = storage.save(data, "pothole.jpg")

    assert os.path.exists(saved_path)
    assert filename.endswith(".jpg")
    assert storage.exists(saved_path) is True

    retrieved = storage.get(saved_path)
    assert retrieved == data


def test_delete_file(storage):
    data = b"Disposable asset"
    saved_path, _ = storage.save(data, "garbage.png")

    assert storage.exists(saved_path) is True
    deleted = storage.delete(saved_path)
    assert deleted is True
    assert storage.exists(saved_path) is False
    assert storage.get(saved_path) is None


def test_path_traversal_protection(storage):
    data = b"Dangerous payload"
    with pytest.raises(ValueError, match="Path traversal attempt detected"):
        storage.save(data, "test.png", subfolder="../../etc")
