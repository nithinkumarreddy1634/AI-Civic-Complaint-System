"""Unit tests for duplicate scoring and decision rules."""
import pytest
from app.ai.duplicate.scoring import compute_duplicate_score


def test_high_similarity_all_dimensions_likely_duplicate():
    # 20m apart (0.96), high visual match (0.90), high text similarity (0.85), same category (1.0)
    res = compute_duplicate_score(
        location_sim=0.96,
        image_sim=0.90,
        text_sim=0.85,
        category_sim=1.0,
        distance_meters=20.0,
    )
    assert res["duplicate_score"] >= 80.0
    assert res["decision"] == "LIKELY_DUPLICATE"


def test_moderate_similarity_possible_duplicate():
    res = compute_duplicate_score(
        location_sim=0.70,
        image_sim=0.65,
        text_sim=0.60,
        category_sim=1.0,
        distance_meters=150.0,
    )
    assert 60.0 <= res["duplicate_score"] < 80.0
    assert res["decision"] == "POSSIBLE_DUPLICATE"


def test_category_conflict_override():
    # High visual and close location, but different categories (e.g. streetlight vs garbage)
    res = compute_duplicate_score(
        location_sim=0.95,
        image_sim=0.90,
        text_sim=0.80,
        category_sim=0.0,  # Conflict
        distance_meters=15.0,
    )
    assert res["decision"] == "NEW"
    assert res["duplicate_score"] <= 45.0
    assert any("categories conflict" in r.lower() for r in res["safety_reasons"])


def test_distant_location_override():
    # High visual similarity and same category, but 3 km apart
    res = compute_duplicate_score(
        location_sim=0.0,
        image_sim=0.92,
        text_sim=0.85,
        category_sim=1.0,
        distance_meters=3000.0,
    )
    assert res["decision"] == "NEW"
    assert res["duplicate_score"] <= 30.0


def test_no_location_scoring():
    # GPS missing: relies on visual, text, and category
    res = compute_duplicate_score(
        location_sim=None,
        image_sim=0.92,
        text_sim=0.85,
        category_sim=1.0,
        distance_meters=None,
    )
    # 0.5*0.92 + 0.3*0.85 + 0.2*1.0 = 0.46 + 0.255 + 0.20 = 0.915 -> 91.5
    assert res["duplicate_score"] >= 85.0
    assert res["decision"] == "LIKELY_DUPLICATE"
