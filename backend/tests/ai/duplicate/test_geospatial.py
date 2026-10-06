"""Unit tests for geospatial distance, location similarity, and bounding box geometry."""
import pytest
from app.ai.duplicate.geospatial_similarity import (
    calculate_haversine_distance,
    calculate_location_similarity,
    get_bounding_box_for_radius,
)


def test_haversine_identical_point():
    dist = calculate_haversine_distance(12.9716, 77.5946, 12.9716, 77.5946)
    assert dist == 0.0


def test_haversine_known_distance():
    # Points approx 111 meters apart (0.001 deg latitude ~ 111.3m)
    dist = calculate_haversine_distance(12.9716, 77.5946, 12.9726, 77.5946)
    assert 110.0 <= dist <= 113.0


def test_location_similarity_close_proximity():
    # 20 meters apart
    res = calculate_location_similarity(12.97160, 77.59460, 12.97178, 77.59460)
    assert res["has_location"] is True
    assert res["is_close_proximity"] is True
    assert res["distance_meters"] <= 50.0
    assert res["location_similarity"] >= 0.90


def test_location_similarity_far_distance():
    # 1.5 km apart
    res = calculate_location_similarity(12.9716, 77.5946, 12.9850, 77.5946)
    assert res["has_location"] is True
    assert res["is_close_proximity"] is False
    assert res["distance_meters"] > 1000.0
    assert res["location_similarity"] == 0.0


def test_location_similarity_missing_coordinates():
    res = calculate_location_similarity(None, 77.5946, 12.9716, 77.5946)
    assert res["has_location"] is False
    assert res["distance_meters"] is None
    assert res["location_similarity"] is None


def test_location_similarity_invalid_coordinates():
    res = calculate_location_similarity(95.0, 77.5946, 12.9716, 77.5946)
    assert res["has_location"] is False
    assert res["distance_meters"] is None


def test_bounding_box_calculation():
    min_lat, min_lon, max_lat, max_lon = get_bounding_box_for_radius(12.9716, 77.5946, radius_meters=500.0)
    assert min_lat < 12.9716 < max_lat
    assert min_lon < 77.5946 < max_lon
