"""Tests for civic infrastructure relevance module."""
from app.ai.verification.relevance import check_civic_relevance


def test_relevant_pothole_detection():
    dets = [{"class_name": "pothole", "confidence": 0.92}]
    res = check_civic_relevance(dets)
    assert res["is_relevant"] is True
    assert res["relevance_score"] >= 80.0
    assert "pothole" in res["detected_issues"]


def test_irrelevant_person_detection():
    dets = [{"class_name": "person", "confidence": 0.88}]
    res = check_civic_relevance(dets)
    assert res["is_relevant"] is False
    assert res["relevance_score"] == 0.0
    assert len(res["detected_issues"]) == 0
    assert "person" in res["irrelevant_detections"]


def test_empty_detections():
    res = check_civic_relevance([])
    assert res["is_relevant"] is False
    assert res["relevance_score"] == 0.0


def test_mixed_detections():
    dets = [
        {"class_name": "garbage", "confidence": 0.85},
        {"class_name": "car", "confidence": 0.70}
    ]
    res = check_civic_relevance(dets)
    assert res["is_relevant"] is True
    assert "garbage" in res["detected_issues"]
    assert "car" in res["irrelevant_detections"]
