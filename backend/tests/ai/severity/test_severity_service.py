"""Comprehensive service test suite covering the 10 user-specified scenarios."""
import pytest
from app.ai.severity.severity_service import SeverityAssessmentService


@pytest.fixture
def service():
    return SeverityAssessmentService()


@pytest.fixture
def img_meta():
    return {"width": 640, "height": 480}


# Test 1: Small pothole
def test_scenario_1_small_pothole(service, img_meta):
    detections = [{"class_name": "pothole", "confidence": 0.88, "bbox": [100, 100, 140, 140]}]
    res = service.assess(detections, img_meta, description="Minor pothole on road side")
    assert res["severity_score"] < 60.0
    assert res["severity_level"] in ["LOW", "MEDIUM"]


# Test 2: Large pothole
def test_scenario_2_large_pothole(service, img_meta):
    # 250x200 box
    detections = [{"class_name": "pothole", "confidence": 0.94, "bbox": [50, 50, 300, 250]}]
    res = service.assess(detections, img_meta, description="Huge crater in the center of the lane")
    assert res["severity_score"] >= 70.0
    assert res["severity_level"] in ["HIGH", "CRITICAL"]


# Test 3: Multiple potholes
def test_scenario_3_multiple_potholes(service, img_meta):
    single_pothole = [{"class_name": "pothole", "confidence": 0.85, "bbox": [100, 100, 200, 200]}]
    multi_potholes = [
        {"class_name": "pothole", "confidence": 0.85, "bbox": [100, 100, 200, 200]},
        {"class_name": "pothole", "confidence": 0.82, "bbox": [250, 150, 350, 250]},
        {"class_name": "pothole", "confidence": 0.80, "bbox": [400, 200, 480, 280]},
    ]
    res_single = service.assess(single_pothole, img_meta)
    res_multi = service.assess(multi_potholes, img_meta)
    assert res_multi["severity_score"] > res_single["severity_score"]
    assert len(res_multi["detection_analysis"]) == 3


# Test 4: Small garbage accumulation
def test_scenario_4_small_garbage(service, img_meta):
    detections = [{"class_name": "garbage", "confidence": 0.85, "bbox": [100, 100, 150, 150]}]
    res = service.assess(detections, img_meta, description="Small pile of litter on corner")
    assert res["severity_score"] < 55.0
    assert res["severity_level"] in ["LOW", "MEDIUM"]


# Test 5: Large garbage accumulation
def test_scenario_5_large_garbage(service, img_meta):
    detections = [{"class_name": "garbage", "confidence": 0.92, "bbox": [50, 50, 350, 350]}]
    res = service.assess(detections, img_meta, description="Huge heap of solid waste completely blocking pathway")
    assert res["severity_score"] >= 65.0
    assert res["public_impact_score"] >= 65.0


# Test 6: Open manhole has elevated safety risk
def test_scenario_6_open_manhole(service, img_meta):
    detections = [{"class_name": "open_manhole", "confidence": 0.90, "bbox": [100, 100, 220, 220]}]
    res = service.assess(detections, img_meta, description="Open manhole cover missing")
    assert res["safety_risk_score"] >= 75.0
    assert any("drop hazard" in f.lower() for f in res["factors"])


# Test 7: Low-confidence detection
def test_scenario_7_low_confidence_detection(service, img_meta):
    high_conf = [{"class_name": "pothole", "confidence": 0.95, "bbox": [100, 100, 200, 200]}]
    low_conf = [{"class_name": "pothole", "confidence": 0.35, "bbox": [100, 100, 200, 200]}]
    res_high = service.assess(high_conf, img_meta)
    res_low = service.assess(low_conf, img_meta)
    assert res_high["severity_score"] > res_low["severity_score"]
    assert res_low["evidence"]["detection_confidence"] == 35.0


# Test 8: Missing description
def test_scenario_8_missing_description(service, img_meta):
    detections = [{"class_name": "damaged_road", "confidence": 0.85, "bbox": [100, 100, 250, 250]}]
    res = service.assess(detections, img_meta, description=None)
    assert "severity_score" in res
    assert res["evidence"]["text_signal"] == 50.0  # Neutral baseline


# Test 9: No location context
def test_scenario_9_no_location(service, img_meta):
    detections = [{"class_name": "broken_streetlight", "confidence": 0.86, "bbox": [100, 50, 200, 300]}]
    res = service.assess(detections, img_meta, location=None)
    assert "severity_score" in res
    assert res["severity_score"] > 0.0


# Test 10: Multiple defect categories
def test_scenario_10_multiple_categories(service, img_meta):
    detections = [
        {"class_name": "pothole", "confidence": 0.90, "bbox": [100, 100, 220, 220]},
        {"class_name": "garbage", "confidence": 0.85, "bbox": [300, 200, 420, 320]},
    ]
    res = service.assess(detections, img_meta, description="Broken road with garbage dumped nearby")
    assert len(res["detection_analysis"]) == 2
    cats = [d["category"] for d in res["detection_analysis"]]
    assert "pothole" in cats and "garbage" in cats


# Edge Case: Zero detections
def test_zero_detections(service, img_meta):
    res = service.assess([], img_meta)
    assert res["severity_score"] == 10.0
    assert res["severity_level"] == "LOW"
    assert len(res["detection_analysis"]) == 0
