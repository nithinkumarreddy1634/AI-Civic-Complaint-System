"""Unit tests for safety risk, infrastructure impact, and public impact calculators."""
import pytest
from app.ai.severity.safety_risk import calculate_safety_risk
from app.ai.severity.infrastructure_impact import calculate_infrastructure_impact
from app.ai.severity.public_impact import calculate_public_impact


def test_safety_risk_calculation():
    res = calculate_safety_risk(
        category="pothole",
        damage_extent_score=75.0,
        detection_confidence=0.92,
        count=2,
        text_urgency=80.0,
    )
    assert 70.0 <= res["safety_risk_score"] <= 100.0
    assert res["level"] in ["HIGH", "CRITICAL"]
    assert len(res["factors"]) >= 1


def test_infrastructure_impact_calculation():
    res = calculate_infrastructure_impact(
        category="damaged_road",
        damage_extent_score=80.0,
        detection_confidence=0.88,
        count=1,
    )
    assert res["infrastructure_impact_score"] >= 65.0
    assert res["level"] in ["HIGH", "CRITICAL"]
    assert len(res["factors"]) >= 1


def test_public_impact_calculation():
    res = calculate_public_impact(
        category="fallen_tree",
        damage_extent_score=85.0,
        count=1,
        text_urgency=75.0,
    )
    assert res["public_impact_score"] >= 70.0
    assert res["level"] == "HIGH"
