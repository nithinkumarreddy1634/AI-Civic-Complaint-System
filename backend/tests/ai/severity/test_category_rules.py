"""Unit tests for category-specific severity rules."""
import pytest
from app.ai.severity.rules.registry import get_severity_rule
from app.ai.severity.rules.pothole import PotholeSeverityRule
from app.ai.severity.rules.open_manhole import OpenManholeSeverityRule
from app.ai.severity.rules.garbage import GarbageSeverityRule


def test_pothole_rule_single_vs_multiple():
    rule = get_severity_rule("pothole")
    assert isinstance(rule, PotholeSeverityRule)

    # Single moderate pothole
    single_risk = rule.evaluate_safety_risk(damage_extent_score=50.0, detection_confidence=0.85, count=1)
    # Multiple potholes of same size
    multi_risk = rule.evaluate_safety_risk(damage_extent_score=50.0, detection_confidence=0.85, count=3)

    assert multi_risk > single_risk
    assert "Bounding box area approximates 2D surface disruption" in rule.get_disclaimer()


def test_open_manhole_inherently_high_safety_risk():
    rule = get_severity_rule("open_manhole")
    assert isinstance(rule, OpenManholeSeverityRule)

    # Even a small open manhole has significant hazard
    risk = rule.evaluate_safety_risk(damage_extent_score=25.0, detection_confidence=0.90, count=1)
    assert risk >= 60.0
    factors = rule.generate_factors(damage_extent_score=25.0, detection_confidence=0.90)
    assert any("drop hazard" in f.lower() for f in factors)


def test_garbage_rule_public_impact():
    rule = get_severity_rule("garbage")
    assert isinstance(rule, GarbageSeverityRule)

    small_public = rule.evaluate_public_impact(damage_extent_score=20.0, count=1)
    large_public = rule.evaluate_public_impact(damage_extent_score=80.0, count=2)

    assert large_public > small_public
    assert "biochemical contamination" in rule.get_disclaimer()


def test_unknown_category_fallback():
    rule = get_severity_rule("mysterious_crack_xyz")
    risk = rule.evaluate_safety_risk(damage_extent_score=40.0, detection_confidence=0.80)
    assert 20.0 <= risk <= 70.0
