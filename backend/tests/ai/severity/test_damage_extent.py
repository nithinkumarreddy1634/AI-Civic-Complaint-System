"""Unit tests for 2D bounding box damage extent calculation."""
import pytest
from app.ai.severity.damage_extent import calculate_damage_extent, DISCLAIMER_DAMAGE_EXTENT


def test_small_damage_extent():
    # 30x30 box in 640x480 image (area ratio: 900 / 307200 = ~0.0029)
    res = calculate_damage_extent([100, 100, 130, 130], image_width=640, image_height=480)
    assert 5.0 <= res["damage_extent_score"] <= 25.0
    assert res["is_significant"] is False
    assert res["disclaimer"] == DISCLAIMER_DAMAGE_EXTENT


def test_large_damage_extent():
    # 300x250 box in 640x480 image (area ratio: 75000 / 307200 = ~0.244, exceeds reference ratio 0.15)
    res = calculate_damage_extent([50, 50, 350, 300], image_width=640, image_height=480)
    assert res["damage_extent_score"] >= 90.0
    assert res["is_significant"] is True
    assert res["damage_area_ratio"] > 0.15


def test_zero_or_negative_geometry():
    # Flat line / zero area bbox
    res = calculate_damage_extent([100, 100, 100, 200], image_width=640, image_height=480)
    assert res["damage_extent_score"] == 5.0
    assert res["damage_area_ratio"] == 0.0


def test_invalid_image_dimensions():
    res = calculate_damage_extent([10, 10, 50, 50], image_width=0, image_height=-10)
    assert res["damage_extent_score"] == 5.0
    assert res["bbox_area"] == 0.0


def test_coordinate_clamping():
    # Coordinates exceeding image boundaries
    res = calculate_damage_extent([-50, -50, 1000, 1000], image_width=640, image_height=480)
    assert res["bbox_area"] == 640 * 480
    assert res["damage_area_ratio"] == 1.0
    assert res["damage_extent_score"] == 100.0
