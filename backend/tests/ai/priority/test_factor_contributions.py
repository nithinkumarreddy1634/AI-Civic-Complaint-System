"""Tests for exact mathematical factor contributions and transparent explanations."""
import pytest
from app.ai.priority.priority_engine import priority_engine
from app.ai.priority.explainer import priority_explainer


def test_factor_contributions_sum_to_base_score():
    res = priority_engine.calculate(
        severity_score=75.5,
        safety_risk_score=82.0,
        infrastructure_impact_score=68.0,
        public_impact_score=70.0,
        frequency_score=60.0,
        verification_confidence_score=92.0,
        location_score=50.0,
    )

    sum_contributions = sum(
        fc.contribution for fc in res.factor_breakdown.values() if fc.status == "included"
    )

    assert abs(sum_contributions - res.base_score) < 1e-4


def test_factor_contributions_sum_with_redistributed_location():
    res = priority_engine.calculate(
        severity_score=85.0,
        safety_risk_score=90.0,
        infrastructure_impact_score=75.0,
        public_impact_score=80.0,
        frequency_score=40.0,
        verification_confidence_score=95.0,
        location_score=None,  # Redistributed
    )

    sum_contributions = sum(
        fc.contribution for fc in res.factor_breakdown.values() if fc.status == "included"
    )

    assert abs(sum_contributions - res.base_score) < 1e-4
    assert res.factor_breakdown["location_impact"].contribution == 0.0


def test_explainer_content():
    res = priority_engine.calculate(
        severity_score=85.0,
        safety_risk_score=90.0,
        infrastructure_impact_score=75.0,
        public_impact_score=80.0,
        frequency_score=60.0,
        verification_confidence_score=95.0,
        location_score=50.0,
        raw_report_count=5,
        unresolved_days=3.0,
    )
    narrative = priority_explainer.generate_explanation(res)

    # Narrative must contain priority level and score
    assert res.priority_level.value in narrative
    assert f"{res.priority_score:.1f}/100" in narrative

    # Narrative must mention duplicate report count
    assert "5 citizen reports" in narrative

    # Narrative must mention aging escalation
    assert "aging boost" in narrative

    # Narrative must include disclaimer
    assert priority_explainer.DISCLAIMER in narrative
