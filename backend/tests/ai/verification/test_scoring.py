"""Tests for verification score calculation, safety vetoes, and threshold logic."""
from app.ai.verification.scoring import calculate_verification_score, make_verification_decision
from app.ai.verification.config import DEFAULT_VERIFICATION_CONFIG


def test_calculate_verification_score_math():
    score = calculate_verification_score(
        quality_score=90.0,
        detection_conf=0.90,
        relevance_score=95.0,
        consistency_score=95.0,
        category_agreement_score=100.0,
        config=DEFAULT_VERIFICATION_CONFIG
    )
    # Expected weighted score:
    # 90*0.10(9) + 90*0.35(31.5) + 95*0.20(19) + 95*0.20(19) + 100*0.15(15) = 93.5
    assert 90.0 <= score <= 96.0


def test_fatal_quality_rejected():
    quality = {"status": "INVALID", "quality_score": 10, "issues": ["Corrupt file"]}
    relevance = {"is_relevant": False, "relevance_score": 0.0, "detected_issues": []}
    consistency = {"consistency_score": 0.0, "matched": False, "category_match": False}
    text = {"has_description": False}

    status, score, explanations = make_verification_decision(
        quality_result=quality,
        relevance_result=relevance,
        consistency_result=consistency,
        detections=[],
        text_result=text,
        config=DEFAULT_VERIFICATION_CONFIG
    )
    assert status == "REJECTED"
    assert score <= 15.0
    assert any("corrupt" in e.lower() or "unreadable" in e.lower() for e in explanations)


def test_borderline_confidence_needs_review():
    quality = {"status": "GOOD", "quality_score": 85, "issues": []}
    relevance = {"is_relevant": True, "relevance_score": 80.0, "detected_issues": ["pothole"]}
    consistency = {"consistency_score": 80.0, "matched": True, "category_match": True}
    dets = [{"class_name": "pothole", "confidence": 0.38}]
    text = {"has_description": True, "clean_text": "small pothole", "text_categories": [{"category": "pothole"}]}

    status, score, explanations = make_verification_decision(
        quality_result=quality,
        relevance_result=relevance,
        consistency_result=consistency,
        detections=dets,
        text_result=text,
        config=DEFAULT_VERIFICATION_CONFIG
    )
    assert status == "NEEDS_REVIEW"
    assert any("borderline" in e.lower() for e in explanations)
