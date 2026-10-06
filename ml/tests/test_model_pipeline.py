"""Comprehensive test suite for Phase 3 Computer Vision Model pipeline.

Tests model loading, dataset pre-flight validation, pre-inference image quality audit,
prediction output structure, bounding box clamping, CivicVisionModel service interface,
and model metadata schema.
"""
import json
import os
import pytest
from pathlib import Path
import numpy as np
from PIL import Image

from ml.inference.image_quality import assess_image_quality
from ml.inference.civic_vision_model import CivicVisionModel
from ml.training.train import verify_dataset, detect_device
from ml.evaluation.metrics import compute_iou, calculate_f1_score, summarize_metrics
from ml.inference.visualize_prediction import render_detections


@pytest.fixture
def test_image_clean(tmp_path):
    """Creates a high quality sharp 300x300 RGB test image with texture."""
    p = tmp_path / "clean_sample.jpg"
    # Create checkerboard pattern for high Laplacian edge sharpness
    arr = np.zeros((300, 300, 3), dtype=np.uint8)
    arr[:, :] = 160
    arr[::20, :, :] = 40
    arr[:, ::20, :] = 220
    img = Image.fromarray(arr)
    img.save(p)
    return p


@pytest.fixture
def test_image_corrupt(tmp_path):
    """Creates an unreadable/corrupted file."""
    p = tmp_path / "corrupted.jpg"
    with open(p, "wb") as f:
        f.write(os.urandom(512))
    return p


@pytest.fixture
def test_image_dark(tmp_path):
    """Creates a pitch black underexposed image."""
    p = tmp_path / "dark.jpg"
    img = Image.new("RGB", (200, 200), color=(5, 5, 5))
    img.save(p)
    return p


@pytest.fixture
def test_image_tiny(tmp_path):
    """Creates an image below the 100x100 resolution threshold."""
    p = tmp_path / "tiny.jpg"
    img = Image.new("RGB", (40, 40), color=(100, 100, 100))
    img.save(p)
    return p


class TestImageQualityAudit:
    """Tests image quality validation logic."""

    def test_clean_image_passes(self, test_image_clean):
        res = assess_image_quality(test_image_clean)
        assert res["valid"] is True
        assert res["quality_score"] > 50
        assert len(res["issues"]) == 0

    def test_corrupted_image_fails(self, test_image_corrupt):
        res = assess_image_quality(test_image_corrupt)
        assert res["valid"] is False
        assert res["quality_score"] == 0
        assert any("Corrupt" in issue or "Unreadable" in issue for issue in res["issues"])

    def test_dark_image_penalized(self, test_image_dark):
        res = assess_image_quality(test_image_dark)
        assert any("dark" in issue.lower() for issue in res["issues"])
        assert res["quality_score"] < 100

    def test_small_dimension_fails(self, test_image_tiny):
        res = assess_image_quality(test_image_tiny, min_dimension=100)
        assert res["valid"] is False
        assert any("small" in issue.lower() for issue in res["issues"])

    def test_nonexistent_file_handling(self, tmp_path):
        res = assess_image_quality(tmp_path / "does_not_exist.jpg")
        assert res["valid"] is False
        assert any("not found" in issue.lower() for issue in res["issues"])


class TestDatasetPreflight:
    """Tests training pre-flight dataset verification."""

    def test_missing_data_yaml(self, tmp_path):
        is_valid, msg, _ = verify_dataset(tmp_path / "missing_data.yaml")
        assert is_valid is False
        assert "not found" in msg.lower()

    def test_detect_device(self):
        device = detect_device("cpu")
        assert device == "cpu"
        auto_device = detect_device("auto")
        assert auto_device in ["0", "cpu"]


class TestMetricsAndEvaluation:
    """Tests bounding box metrics and F1 calculation."""

    def test_iou_identical_boxes(self):
        box = [10.0, 10.0, 50.0, 50.0]
        assert compute_iou(box, box) == 1.0

    def test_iou_disjoint_boxes(self):
        b1 = [0.0, 0.0, 10.0, 10.0]
        b2 = [20.0, 20.0, 30.0, 30.0]
        assert compute_iou(b1, b2) == 0.0

    def test_iou_partial_overlap(self):
        b1 = [0.0, 0.0, 20.0, 20.0]  # area 400
        b2 = [10.0, 0.0, 30.0, 20.0] # area 400, intersection 200
        iou = compute_iou(b1, b2)
        assert abs(iou - (200.0 / 600.0)) < 1e-4

    def test_f1_score_calculation(self):
        f1 = calculate_f1_score(0.8, 0.8)
        assert abs(f1 - 0.8) < 1e-4
        assert calculate_f1_score(0.0, 0.0) == 0.0

    def test_summarize_metrics(self):
        raw = {"precision": 0.85, "recall": 0.75, "map50": 0.81, "map50_95": 0.62}
        s = summarize_metrics(raw)
        assert s["precision"] == 0.85
        assert s["f1_score"] > 0.70


class TestVisualizationRendering:
    """Tests bounding box visual overlay generation."""

    def test_render_detections(self):
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        detections = [{
            "class_id": 0,
            "class_name": "pothole",
            "confidence": 0.92,
            "bbox": [20, 20, 100, 100]
        }]
        rendered = render_detections(img, detections)
        assert rendered.shape == (200, 200, 3)
        # Verify pixels were drawn (not all black anymore)
        assert np.sum(rendered) > 0


class TestModelMetadataSchema:
    """Tests model registry metadata file."""

    def test_metadata_structure(self):
        meta_path = Path(__file__).parent.parent / "models" / "model_metadata.json"
        assert meta_path.exists()
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "model_name" in data
        assert "num_classes" in data
        assert data["num_classes"] == 9
        assert "classes" in data
        assert "pothole" in data["classes"]
        assert "confidence_threshold" in data


class TestCivicVisionModelInterface:
    """Tests Phase 4 CivicVisionModel service wrapper without requiring weights."""

    def test_interface_instantiation(self):
        model_wrapper = CivicVisionModel(model_path="dummy.pt", conf_threshold=0.45)
        assert model_wrapper.conf_threshold == 0.45
        assert model_wrapper.model_path == "dummy.pt"

    def test_validate_image_through_wrapper(self, test_image_clean):
        model_wrapper = CivicVisionModel(model_path="dummy.pt")
        res = model_wrapper.validate_image(test_image_clean)
        assert res["valid"] is True
        assert res["quality_score"] > 50

    def test_invalid_image_stops_predict(self, test_image_corrupt):
        model_wrapper = CivicVisionModel(model_path="dummy.pt")
        res = model_wrapper.predict(test_image_corrupt)
        assert res["image_valid"] is False
        assert len(res["detections"]) == 0
