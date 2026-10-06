"""Unit tests for multi-factor fusion and multi-detection aggregation."""
import pytest
from app.ai.severity.scoring import (
    calculate_single_severity_score,
    aggregate_multi_detection_severities,
    map_score_to_severity_level,
)


def test_single_detection_score_math():
    score = calculate_single_severity_score(
        damage_extent_score=60.0,
        detection_confidence=0.90,  # 90.0
        safety_risk_score=70.0,
        infrastructure_impact_score=80.0,
        public_impact_score=65.0,
    )
    # Expected: 0.2*60 (12) + 0.1*90 (9) + 0.3*70 (21) + 0.2*80 (16) + 0.2*65 (13) = 71.0
    assert 70.0 <= score <= 72.0


def test_multi_detection_aggregation_diminishing_returns():
    # 3 detections: 70, 50, 40
    # Primary: 70
    # Others: (50 * 0.30) + (40 * 0.30) = 15 + 12 = 27
    # Aggregated: 70 + 27 = 97.0
    agg = aggregate_multi_detection_severities([70.0, 50.0, 40.0])
    assert agg == 97.0


def test_multi_detection_aggregation_caps_at_100():
    # Multiple very high severity detections
    agg = aggregate_multi_detection_severities([90.0, 85.0, 80.0, 75.0])
    assert agg == 100.0


def test_severity_level_mapping():
    assert map_score_to_severity_level(95.0) == "CRITICAL"
    assert map_score_to_severity_level(75.0) == "HIGH"
    assert map_score_to_severity_level(55.0) == "MEDIUM"
    assert map_score_to_severity_level(25.0) == "LOW"
