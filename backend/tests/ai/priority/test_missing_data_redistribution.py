"""Tests for dynamic missing-data weight redistribution in PriorityEngine."""
import pytest
from app.ai.priority.priority_engine import priority_engine, PriorityEngine


def test_effective_weights_sum_to_one_with_location():
    res = priority_engine.calculate(
        severity_score=80.0,
        safety_risk_score=75.0,
        infrastructure_impact_score=70.0,
        public_impact_score=65.0,
        frequency_score=40.0,
        verification_confidence_score=90.0,
        location_score=60.0,
    )
    assert abs(res.total_effective_weight - 1.0) < 1e-4
    assert res.factor_breakdown["location_impact"].status == "included"
    assert res.factor_breakdown["location_impact"].effective_weight > 0.0


def test_effective_weights_sum_to_one_without_location():
    res = priority_engine.calculate(
        severity_score=80.0,
        safety_risk_score=75.0,
        infrastructure_impact_score=70.0,
        public_impact_score=65.0,
        frequency_score=40.0,
        verification_confidence_score=90.0,
        location_score=None,  # Missing GPS
    )
    assert abs(res.total_effective_weight - 1.0) < 1e-4
    assert res.factor_breakdown["location_impact"].status == "redistributed"
    assert res.factor_breakdown["location_impact"].effective_weight == 0.0
    assert res.metadata["missing_gps_redistributed"] is True

    # Check that nominal weights were scaled up proportionately
    # e.g., severity was nominal 0.25; available nominal sum was 0.95 -> effective = 0.25 / 0.95 ~ 0.2632
    assert res.factor_breakdown["severity"].effective_weight > res.factor_breakdown["severity"].nominal_weight


def test_missing_location_can_still_reach_maximum_score():
    res = priority_engine.calculate(
        severity_score=100.0,
        safety_risk_score=100.0,
        infrastructure_impact_score=100.0,
        public_impact_score=100.0,
        frequency_score=100.0,
        verification_confidence_score=100.0,
        location_score=None,  # Missing GPS
    )
    assert res.priority_score == 100.0
    assert res.priority_level.value == "URGENT"


def test_missing_location_can_still_reach_minimum_score():
    res = priority_engine.calculate(
        severity_score=0.0,
        safety_risk_score=0.0,
        infrastructure_impact_score=0.0,
        public_impact_score=0.0,
        frequency_score=0.0,
        verification_confidence_score=0.0,
        location_score=None,  # Missing GPS
    )
    assert res.priority_score == 0.0
    assert res.priority_level.value == "LOW"
