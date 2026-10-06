"""Comprehensive integration tests covering the 7 core verification test scenarios."""
import pytest
import numpy as np
from PIL import Image
from app.ai.verification.verification_service import ComplaintVerificationService


@pytest.fixture
def service():
    return ComplaintVerificationService()


@pytest.fixture
def clear_test_image(tmp_path):
    p = tmp_path / "clear_test.jpg"
    arr = np.zeros((300, 300, 3), dtype=np.uint8)
    arr[:, :] = 160
    arr[::20, :, :] = 40
    arr[:, ::20, :] = 220
    Image.fromarray(arr).save(p)
    return p


@pytest.fixture
def blurry_test_image(tmp_path):
    p = tmp_path / "blurry.jpg"
    # Uniform smooth gradient with low Laplacian variance
    arr = np.ones((200, 200, 3), dtype=np.uint8) * 128
    Image.fromarray(arr).save(p)
    return p


def test_scenario_1_valid_pothole(service, clear_test_image):
    """Test 1: Clear pothole image + matching description -> VERIFIED."""
    mock_dets = [{"class_name": "pothole", "confidence": 0.92, "bbox": [100, 100, 200, 200]}]
    res = service.verify_complaint(
        image_input=clear_test_image,
        description="Large pothole near the main road causing traffic issues.",
        selected_category="pothole",
        mock_detections=mock_dets
    )
    assert res["verification_status"] == "VERIFIED"
    assert res["verification_score"] >= 75.0
    assert res["detected_category"] == "pothole"
    assert len(res["explanation"]) > 0


def test_scenario_2_irrelevant_image(service, clear_test_image):
    """Test 2: Non-civic image (person/selfie) -> REJECTED."""
    mock_dets = [{"class_name": "person", "confidence": 0.88, "bbox": [50, 50, 150, 250]}]
    res = service.verify_complaint(
        image_input=clear_test_image,
        description="Selfie with friends downtown.",
        selected_category=None,
        mock_detections=mock_dets
    )
    assert res["verification_status"] == "REJECTED"
    assert res["relevance"]["is_relevant"] is False


def test_scenario_3_image_text_mismatch(service, clear_test_image):
    """Test 3: Garbage photo + 'broken streetlight' description -> NEEDS_REVIEW."""
    mock_dets = [{"class_name": "garbage", "confidence": 0.89, "bbox": [50, 50, 200, 200]}]
    res = service.verify_complaint(
        image_input=clear_test_image,
        description="Broken streetlight not turning on at night.",
        selected_category="broken_streetlight",
        mock_detections=mock_dets
    )
    assert res["verification_status"] == "NEEDS_REVIEW"
    assert res["consistency"]["matched"] is False


def test_scenario_4_low_quality_blurry_image(service, blurry_test_image):
    """Test 4: Extremely blurry image -> NEEDS_REVIEW or REJECTED."""
    mock_dets = [{"class_name": "pothole", "confidence": 0.50, "bbox": [50, 50, 150, 150]}]
    res = service.verify_complaint(
        image_input=blurry_test_image,
        description="Pothole in the street.",
        selected_category="pothole",
        mock_detections=mock_dets
    )
    # With poor blur metrics, it should either be NEEDS_REVIEW or REJECTED, not VERIFIED
    assert res["verification_status"] in ["NEEDS_REVIEW", "REJECTED"]


def test_scenario_5_high_confidence_detection(service, clear_test_image):
    """Test 5: Clear defect + high confidence -> High verification score."""
    mock_dets = [{"class_name": "open_manhole", "confidence": 0.96, "bbox": [60, 60, 220, 220]}]
    res = service.verify_complaint(
        image_input=clear_test_image,
        description="Missing open manhole cover creating danger.",
        selected_category="open_manhole",
        mock_detections=mock_dets
    )
    assert res["verification_status"] == "VERIFIED"
    assert res["verification_score"] >= 85.0


def test_scenario_6_borderline_detection(service, clear_test_image):
    """Test 6: Borderline confidence detection (0.38) -> NEEDS_REVIEW."""
    mock_dets = [{"class_name": "damaged_road", "confidence": 0.38, "bbox": [10, 10, 100, 100]}]
    res = service.verify_complaint(
        image_input=clear_test_image,
        description="Cracked asphalt surface.",
        selected_category="damaged_road",
        mock_detections=mock_dets
    )
    assert res["verification_status"] == "NEEDS_REVIEW"
    assert any("borderline" in e.lower() for e in res["explanation"])


def test_scenario_7_multiple_issues(service, clear_test_image):
    """Test 7: Multiple detections (pothole + garbage) -> All recorded with high consistency."""
    mock_dets = [
        {"class_name": "pothole", "confidence": 0.91, "bbox": [20, 20, 120, 120]},
        {"class_name": "garbage", "confidence": 0.86, "bbox": [150, 150, 250, 250]},
    ]
    res = service.verify_complaint(
        image_input=clear_test_image,
        description="There is a pothole and garbage accumulated on this street.",
        selected_category="pothole",
        mock_detections=mock_dets
    )
    assert res["verification_status"] == "VERIFIED"
    assert len(res["detections"]) == 2
    assert "pothole" in res["relevance"]["detected_issues"]
    assert "garbage" in res["relevance"]["detected_issues"]
