"""
Unit tests for LocalFileStorage and Storage Layer (Section 5 & 16).
"""
import os
import pytest
import tempfile
from app.services.storage import LocalFileStorage


@pytest.fixture
def temp_storage():
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalFileStorage(base_dir=tmpdir)
        yield storage


def test_storage_save_and_get(temp_storage):
    """Test saving file bytes and retrieving them."""
    content = b"CIVIC_AI_TEST_IMAGE_BYTES"
    file_path, filename = temp_storage.save(content, "original_pothole.jpg")

    assert os.path.exists(file_path)
    assert temp_storage.exists(file_path)

    retrieved = temp_storage.get(file_path)
    assert retrieved == content


def test_storage_delete(temp_storage):
    """Test deleting file from storage."""
    file_path, _ = temp_storage.save(b"TO_DELETE", "delete_me.png")
    assert temp_storage.exists(file_path)

    deleted = temp_storage.delete(file_path)
    assert deleted is True
    assert not temp_storage.exists(file_path)

    # Deleting again returns False
    assert temp_storage.delete(file_path) is False


def test_storage_path_traversal_detection(temp_storage):
    """Test that path traversal attempts in subfolders raise ValueError."""
    with pytest.raises(ValueError, match="Path traversal"):
        temp_storage.save(b"PAYLOAD", "test.jpg", subfolder="../../etc")
