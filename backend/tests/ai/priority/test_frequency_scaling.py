"""Tests for sublinear saturating frequency scaling."""
import pytest
from app.ai.priority.frequency_scaling import frequency_scaler, FrequencyScaler


def test_base_single_report_score():
    score = frequency_scaler.scale(1)
    assert score == 15.0


def test_breakpoints_accuracy():
    assert frequency_scaler.scale(1) == 15.0
    assert frequency_scaler.scale(3) == 40.0
    assert frequency_scaler.scale(5) == 60.0
    assert frequency_scaler.scale(10) == 85.0
    assert frequency_scaler.scale(20) == 100.0


def test_linear_interpolation_between_points():
    # Between 3 (40.0) and 5 (60.0), count 4 should be 50.0
    score_4 = frequency_scaler.scale(4)
    assert score_4 == 50.0

    # Between 1 (15.0) and 2 (28.0)
    score_2 = frequency_scaler.scale(2)
    assert score_2 == 28.0


def test_saturation_cap():
    # Beyond 20 reports, score must be capped at 100.0
    assert frequency_scaler.scale(20) == 100.0
    assert frequency_scaler.scale(50) == 100.0
    assert frequency_scaler.scale(500) == 100.0


def test_zero_and_negative_counts():
    assert frequency_scaler.scale(0) == 0.0
    assert frequency_scaler.scale(-5) == 0.0


def test_strictly_monotonic_non_decreasing():
    prev = 0.0
    for count in range(1, 30):
        current = frequency_scaler.scale(count)
        assert current >= prev
        prev = current
