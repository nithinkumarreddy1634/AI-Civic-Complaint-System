"""Unit tests for DepartmentRecommendationService and configuration."""
import pytest
from app.ai.department.department_service import department_recommendation_service
from app.ai.department.config import DepartmentConfig


def test_single_category_recommendations():
    """Verify standard civic categories map to appropriate municipal departments."""
    test_cases = [
        ("pothole", "roads"),
        ("damaged_road", "roads"),
        ("open_manhole", "roads"),
        ("damaged_sidewalk", "roads"),
        ("garbage", "sanitation"),
        ("garbage_accumulation", "sanitation"),
        ("illegal_dumping", "sanitation"),
        ("broken_streetlight", "electrical"),
        ("water_leakage", "water"),
        ("fallen_tree", "horticulture"),
    ]

    for category, expected_dept in test_cases:
        res = department_recommendation_service.recommend(category=category)
        assert res["department_id"] == expected_dept, f"Expected {expected_dept} for {category}, got {res['department_id']}"
        assert res["is_manual_review"] is False
        assert 0.0 < res["recommendation_confidence"] <= 1.0
        assert "jurisdiction" in res["reason"] or "classified as" in res["reason"]


def test_unknown_category_manual_review_fallback():
    """Unrecognized, ambiguous, or 'other' categories must route to MANUAL_REVIEW without guessing."""
    ambiguous_categories = ["other", "unknown", "unrecognized", "alien_invasion", "", None]

    for cat in ambiguous_categories:
        res = department_recommendation_service.recommend(category=cat)
        assert res["is_manual_review"] is True
        assert res["department_id"] == "manual_review"
        assert "Manual Review" in res["department_name"]
        assert "Manual Review / Triage Team" in res["reason"]


def test_multi_issue_complaint():
    """Complaints with multiple detected issues must recommend multiple departments with a primary."""
    detections = [
        {"class_name": "pothole", "confidence": 0.92},
        {"class_name": "garbage_accumulation", "confidence": 0.88},
    ]

    res = department_recommendation_service.recommend(
        category="pothole",
        detections=detections,
        description="Pothole full of garbage on the street",
    )

    assert res["is_manual_review"] is False
    assert len(res["departments"]) == 2
    dept_ids = [d["department_id"] for d in res["departments"]]
    assert "roads" in dept_ids
    assert "sanitation" in dept_ids
    assert "Multi-issue complaint detected" in res["reason"]
    # Check that exactly one department is designated as primary
    primary_count = sum(1 for d in res["departments"] if d.get("is_primary"))
    assert primary_count == 1


def test_confidence_calibration():
    """Confidence must increase with verified status and rich metadata."""
    res_verified = department_recommendation_service.recommend(
        category="pothole",
        description="Dangerous deep crater right in the intersection",
        location={"latitude": 12.9716, "longitude": 77.5946},
        detection_confidence=0.95,
        verification_status="VERIFIED",
    )

    res_borderline = department_recommendation_service.recommend(
        category="pothole",
        description=None,
        location=None,
        detection_confidence=0.60,
        verification_status="NEEDS_REVIEW",
    )

    assert res_verified["recommendation_confidence"] > res_borderline["recommendation_confidence"]
    assert res_verified["recommendation_confidence"] <= 0.99
    assert res_borderline["recommendation_confidence"] >= 0.10
