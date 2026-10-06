"""Tests for image quality validation and health state classification."""
import os
import pytest
import numpy as np
from PIL import Image
from app.ai.verification.image_quality import verify_image_quality, map_score_to_state


@pytest.fixture
def sharp_image_file(tmp_path):
    p = tmp_path / "sharp.jpg"
    arr = np.zeros((300, 300, 3), dtype=np.uint8)
    arr[:, :] = 160
    arr[::20, :, :] = 40
    arr[:, ::20, :] = 220
    Image.fromarray(arr).save(p)
    return p


@pytest.fixture
def dark_image_file(tmp_path):
    p = tmp_path / "dark.jpg"
    Image.new("RGB", (200, 200), color=(10, 10, 10)).save(p)
    return p


@pytest.fixture
def tiny_image_file(tmp_path):
    p = tmp_path / "tiny.jpg"
    Image.new("RGB", (30, 30), color=(150, 150, 150)).save(p)
    return p


def test_sharp_image_grade(sharp_image_file):
    res = verify_image_quality(sharp_image_file)
    assert res["valid"] is True
    assert res["status"] in ["GOOD", "ACCEPTABLE"]
    assert res["quality_score"] >= 60


def test_dark_image_penalized(dark_image_file):
    res = verify_image_quality(dark_image_file)
    assert any("dark" in i.lower() for i in res["issues"])
    assert res["quality_score"] < 80


def test_tiny_image_fatal(tiny_image_file):
    res = verify_image_quality(tiny_image_file)
    assert res["valid"] is False
    assert res["status"] == "INVALID"


def test_nonexistent_file(tmp_path):
    res = verify_image_quality(tmp_path / "missing.jpg")
    assert res["valid"] is False
    assert res["status"] == "INVALID"


def test_map_score_to_state():
    assert map_score_to_state(95) == "GOOD"
    assert map_score_to_state(70) == "ACCEPTABLE"
    assert map_score_to_state(45) == "POOR"
    assert map_score_to_state(20) == "INVALID"
    assert map_score_to_state(85, is_fatal=True) == "INVALID"
