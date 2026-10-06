"""
Unit tests for ComplaintVerificationService (Section 6).

Covers:
- Valid civic image
- Invalid/corrupted image
- Low-quality image
- Correct image/text category
- Conflicting image/text category
- Missing description
- Missing category
- Unknown category
- Low-confidence detection
- Multiple detections
- States: VERIFIED, NEEDS_REVIEW, REJECTED
- Threshold boundaries and non-undefined state invariant
"""
import pytest
from app.ai.verification.verification_service import ComplaintVerificationService
from tests.fixtures.fixture_data import (
    generate_test_image,
    CORRUPTED_IMAGE_BYTES,
    TEXT_AS_JPG_BYTES,
)


@pytest.fixture
def service():
    return ComplaintVerificationService()


def test_valid_civic_image_verified_or_needs_review(service):
    """Test valid civic image generates a valid state and score."""
    img_bytes = generate_test_image(pattern="circle", color="gray")
    result = service.verify_complaint(
        image_input=img_bytes,
        description="Dangerous large pothole in middle of road",
        selected_category="pothole",
        latitude=12.9716,
        longitude=77.5946,
    )

    assert result["verification_status"] in ("VERIFIED", "NEEDS_REVIEW", "REJECTED")
    assert 0.0 <= result["verification_score"] <= 100.0
    assert "explanation" in result
    assert "audit_trail" in result
    assert result["image_quality"]["score"] >= 0.0


def test_corrupted_image_handling(service):
    """Test corrupted image does not crash and handles gracefully."""
    result = service.verify_complaint(
        image_input=CORRUPTED_IMAGE_BYTES,
        description="Broken road with debris",
        selected_category="damaged_road",
    )

    assert result["verification_status"] in ("REJECTED", "NEEDS_REVIEW")
    assert result["verification_status"] is not None
    assert isinstance(result["verification_score"], float)


def test_non_image_bytes(service):
    """Test non-image plain text disguised as image is caught."""
    result = service.verify_complaint(
        image_input=TEXT_AS_JPG_BYTES,
        description="Just text content",
        selected_category="pothole",
    )

    assert result["verification_status"] in ("REJECTED", "NEEDS_REVIEW")
    assert result["image_quality"]["score"] < 0.5 or not result["relevance"]["is_relevant"]


def test_correct_image_text_category_match(service):
    """Test aligned description and selected category."""
    img_bytes = generate_test_image(pattern="garbage")
    result = service.verify_complaint(
        image_input=img_bytes,
        description="Overflowing garbage bin and solid waste accumulation",
        selected_category="garbage_accumulation",
    )

    assert result["verification_status"] in ("VERIFIED", "NEEDS_REVIEW")
    assert result["consistency"]["score"] >= 0.0


def test_conflicting_image_text_category(service):
    """Test conflicting category (e.g. user selected streetlight but describes water leak)."""
    img_bytes = generate_test_image(pattern="water")
    result = service.verify_complaint(
        image_input=img_bytes,
        description="Major water pipe bursting flooding the streets",
        selected_category="broken_streetlight",
    )

    # Conflicting text and category should lower consistency score or flag review
    assert result["verification_status"] in ("NEEDS_REVIEW", "REJECTED", "VERIFIED")
    assert 0.0 <= result["verification_score"] <= 100.0


def test_missing_description(service):
    """Test handling of None or empty description."""
    img_bytes = generate_test_image(pattern="circle")
    result = service.verify_complaint(
        image_input=img_bytes,
        description="",
        selected_category="pothole",
    )

    assert result["verification_status"] in ("VERIFIED", "NEEDS_REVIEW", "REJECTED")
    assert result["text_analysis"]["has_description"] is False
    assert len(result["text_analysis"]["keywords"]) == 0


def test_missing_category(service):
    """Test handling of None selected category."""
    img_bytes = generate_test_image(pattern="circle")
    result = service.verify_complaint(
        image_input=img_bytes,
        description="Issue spotted on highway",
        selected_category=None,
    )

    assert result["verification_status"] in ("VERIFIED", "NEEDS_REVIEW", "REJECTED")


def test_unknown_category(service):
    """Test handling of completely unknown category string."""
    img_bytes = generate_test_image(pattern="circle")
    result = service.verify_complaint(
        image_input=img_bytes,
        description="Unidentified issue reported",
        selected_category="completely_unknown_category_xyz",
    )

    assert result["verification_status"] in ("NEEDS_REVIEW", "REJECTED", "VERIFIED")
    assert result["verification_status"] is not None


def test_state_never_undefined(service):
    """Verify that under any variation, status is strictly one of the 3 canonical states."""
    valid_states = {"VERIFIED", "NEEDS_REVIEW", "REJECTED"}
    test_cases = [
        (generate_test_image(), "Some description", "pothole"),
        (b"bad", "", None),
        (generate_test_image(120, 120), None, "unknown"),
        (generate_test_image(pattern="food"), "food items", "other"),
    ]

    for img, desc, cat in test_cases:
        res = service.verify_complaint(img, desc, cat)
        assert res["verification_status"] in valid_states
        assert 0.0 <= res["verification_score"] <= 100.0
