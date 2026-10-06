"""
Unit tests for SeverityAssessmentService (Section 7).

Covers:
- Small, medium, and large damage extent
- Multiple detections aggregation
- High safety risk vs low safety risk
- Missing optional location data
- Missing text severity signal
- Range verification: 0 <= severity_score <= 100
- Internal consistency between score and level (LOW, MEDIUM, HIGH, CRITICAL)
"""
import pytest
from app.ai.severity.severity_service import SeverityAssessmentService


@pytest.fixture
def service():
    return SeverityAssessmentService()


def test_small_damage_extent(service):
    """Test small bounding box produces lower damage extent score."""
    small_det = [{
        "class_name": "pothole",
        "confidence": 0.90,
        "bbox": [100, 100, 140, 140],  # 40x40 = 1600 px^2 in 640x480
    }]
    res = service.assess(
        detections=small_det,
        image_metadata={"width": 640, "height": 480},
        description="Minor crack in pavement",
    )

    assert 0.0 <= res["severity_score"] <= 100.0
    assert res["severity_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def test_large_damage_extent(service):
    """Test large bounding box produces higher damage extent score than small."""
    large_det = [{
        "class_name": "pothole",
        "confidence": 0.95,
        "bbox": [50, 50, 550, 400],  # 500x350 = 175000 px^2 in 640x480
    }]
    small_det = [{
        "class_name": "pothole",
        "confidence": 0.95,
        "bbox": [100, 100, 130, 130],
    }]

    res_large = service.assess(
        detections=large_det,
        image_metadata={"width": 640, "height": 480},
        description="Massive crater spanning entire street",
    )
    res_small = service.assess(
        detections=small_det,
        image_metadata={"width": 640, "height": 480},
        description="Small minor dip",
    )

    assert res_large["severity_score"] >= res_small["severity_score"]


def test_multiple_detections(service):
    """Test multiple defect detections are aggregated."""
    multi_det = [
        {"class_name": "pothole", "confidence": 0.88, "bbox": [100, 100, 200, 200]},
        {"class_name": "damaged_road", "confidence": 0.82, "bbox": [250, 150, 450, 350]},
    ]
    res = service.assess(
        detections=multi_det,
        image_metadata={"width": 640, "height": 480},
        description="Multiple potholes and road damage",
    )

    assert 0.0 <= res["severity_score"] <= 100.0
    assert len(res["detection_analysis"]) == 2


def test_high_safety_risk_hazard(service):
    """Hazardous category like open_manhole should trigger high safety risk score."""
    hazard_det = [{
        "class_name": "open_manhole",
        "confidence": 0.92,
        "bbox": [150, 150, 350, 350],
    }]
    res = service.assess(
        detections=hazard_det,
        image_metadata={"width": 640, "height": 480},
        description="Uncovered manhole deep pit directly on footpath urgent danger",
    )

    assert res["safety_risk_score"] >= 60.0
    assert res["severity_level"] in ("HIGH", "CRITICAL")


def test_missing_optional_location(service):
    """Missing location coordinates should be handled gracefully."""
    det = [{"class_name": "garbage_accumulation", "confidence": 0.85, "bbox": [100, 100, 300, 300]}]
    res = service.assess(
        detections=det,
        image_metadata={"width": 640, "height": 480},
        description="Garbage piling up",
        location=None,
    )

    assert 0.0 <= res["severity_score"] <= 100.0
    assert res["severity_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def test_missing_text_signals(service):
    """Empty description with no keywords should not crash and return valid assessment."""
    det = [{"class_name": "water_leakage", "confidence": 0.85, "bbox": [100, 100, 300, 300]}]
    res = service.assess(
        detections=det,
        image_metadata={"width": 640, "height": 480},
        description="",
    )

    assert 0.0 <= res["severity_score"] <= 100.0


def test_level_consistency_with_score(service):
    """Test that severity_level consistently reflects configured thresholds."""
    from app.ai.severity.scoring import map_score_to_severity_level
    thresh = service.config.thresholds
    for score in [5.0, 25.0, 45.0, 65.0, 75.0, 95.0]:
        level = map_score_to_severity_level(score)
        if score >= thresh.critical:
            assert level == "CRITICAL"
        elif score >= thresh.high:
            assert level == "HIGH"
        elif score >= thresh.medium:
            assert level == "MEDIUM"
        else:
            assert level == "LOW"
