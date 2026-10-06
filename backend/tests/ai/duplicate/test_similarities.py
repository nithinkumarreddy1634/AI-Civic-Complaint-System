"""Unit tests for image, text, and category similarity metrics."""
import pytest
from PIL import Image
from app.ai.duplicate.embedding_service import EmbeddingService
from app.ai.duplicate.image_similarity import calculate_image_similarity, DISCLAIMER_IMAGE_SIMILARITY
from app.ai.duplicate.text_similarity import calculate_text_similarity
from app.ai.duplicate.scoring import calculate_category_similarity


@pytest.fixture
def embed_service():
    return EmbeddingService()


def test_identical_image_similarity(embed_service):
    img = Image.new("RGB", (150, 150), color=(100, 150, 200))
    emb = embed_service.generate_image_embedding(img)
    res = calculate_image_similarity(emb, emb)
    assert res["image_similarity"] >= 0.99
    assert res["is_high_visual_match"] is True
    assert res["disclaimer"] == DISCLAIMER_IMAGE_SIMILARITY


def test_text_semantic_synonym_similarity(embed_service):
    text_a = "Large pothole near the bus stop."
    text_b = "Deep road hole beside the bus stop."
    text_unrelated = "Broken streetlight blinking at night."

    emb_a = embed_service.generate_text_embedding(text_a)
    emb_b = embed_service.generate_text_embedding(text_b)
    emb_c = embed_service.generate_text_embedding(text_unrelated)

    sim_synonym = calculate_text_similarity(emb_a, emb_b)
    sim_unrelated = calculate_text_similarity(emb_a, emb_c)

    assert sim_synonym["text_similarity"] > sim_unrelated["text_similarity"]
    assert sim_synonym["text_similarity"] >= 0.70


def test_category_similarity():
    # Identical
    assert calculate_category_similarity("pothole", "pothole") == 1.0
    # Affinity
    assert calculate_category_similarity("pothole", "damaged_road") == 0.70
    assert calculate_category_similarity("garbage", "illegal_dumping") == 0.70
    # Conflict
    assert calculate_category_similarity("broken_streetlight", "garbage") == 0.0
    # Missing / None
    assert calculate_category_similarity(None, "pothole") == 0.50
