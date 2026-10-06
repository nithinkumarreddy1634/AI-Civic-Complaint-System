"""Tests for cross-modal consistency and category matching."""
from app.ai.verification.consistency import evaluate_consistency


def test_exact_category_match():
    vision = [{"class_name": "pothole", "confidence": 0.90}]
    text = [{"category": "pothole", "confidence": 0.95}]
    res = evaluate_consistency(vision, text, user_selected_category="pothole")
    assert res["matched"] is True
    assert res["consistency_score"] >= 85.0
    assert res["category_match"] is True


def test_affinity_category_match():
    vision = [{"class_name": "pothole", "confidence": 0.85}]
    text = [{"category": "damaged_road", "confidence": 0.80}]
    res = evaluate_consistency(vision, text)
    assert res["matched"] is True
    assert res["consistency_score"] >= 70.0


def test_mismatched_category_conflict():
    vision = [{"class_name": "garbage", "confidence": 0.88}]
    text = [{"category": "broken_streetlight", "confidence": 0.92}]
    res = evaluate_consistency(vision, text, user_selected_category="broken_streetlight")
    assert res["matched"] is False
    assert res["consistency_score"] <= 30.0
    assert res["category_match"] is False


def test_no_text_provided():
    vision = [{"class_name": "pothole", "confidence": 0.88}]
    res = evaluate_consistency(vision, [], user_selected_category="pothole")
    assert res["matched"] is True
    assert res["consistency_score"] >= 70.0
