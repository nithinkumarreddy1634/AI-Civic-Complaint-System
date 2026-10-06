"""Unit tests for visual and textual embedding extraction."""
import pytest
import numpy as np
from PIL import Image
from app.ai.duplicate.embedding_service import EmbeddingService


@pytest.fixture
def embed_service():
    return EmbeddingService()


def test_image_embedding_generation(embed_service):
    img = Image.new("RGB", (200, 200), color=(128, 64, 32))
    emb = embed_service.generate_image_embedding(img)
    assert len(emb) == 512
    # Verify L2 normalization
    norm = np.linalg.norm(emb)
    assert pytest.approx(norm, rel=1e-2) == 1.0


def test_image_embedding_empty_fallback(embed_service):
    emb = embed_service.generate_image_embedding(b"")
    assert len(emb) == 512
    assert emb[0] == 1.0


def test_text_embedding_generation(embed_service):
    text = "Large pothole in the road near the market bus stop"
    emb = embed_service.generate_text_embedding(text)
    assert len(emb) == 384
    norm = np.linalg.norm(emb)
    assert pytest.approx(norm, rel=1e-2) == 1.0


def test_text_embedding_empty_fallback(embed_service):
    emb = embed_service.generate_text_embedding("")
    assert len(emb) == 384
    assert emb[0] == 1.0
