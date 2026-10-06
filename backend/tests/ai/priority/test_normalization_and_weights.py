"""Tests for Priority weights validation and configuration integrity."""
import pytest
from app.ai.priority.config import (
    PriorityWeights,
    PriorityThresholds,
    PriorityConfig,
    priority_config,
)


def test_default_weights_sum_to_one():
    weights = PriorityWeights()
    weights.validate()
    total = (
        weights.severity
        + weights.safety_risk
        + weights.infrastructure_impact
        + weights.public_impact
        + weights.complaint_frequency
        + weights.location_impact
        + weights.verification_confidence
    )
    assert abs(total - 1.0) < 1e-4


def test_invalid_weights_sum_raises_error():
    with pytest.raises(ValueError, match="must sum to 1.0"):
        bad_weights = PriorityWeights(
            severity=0.5,
            safety_risk=0.5,
            infrastructure_impact=0.5,  # Sum = 1.5
        )
        bad_weights.validate()


def test_out_of_bounds_weights_raises_error():
    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        bad_weights = PriorityWeights(
            severity=-0.1,
            safety_risk=0.35,
            infrastructure_impact=0.25,
            public_impact=0.25,
            complaint_frequency=0.10,
            location_impact=0.10,
            verification_confidence=0.05,
        )
        bad_weights.validate()


def test_thresholds_strictly_ascending():
    thresh = PriorityThresholds()
    thresh.validate()
    assert thresh.low < thresh.medium < thresh.high < thresh.urgent


def test_invalid_thresholds_raises_error():
    with pytest.raises(ValueError, match="strictly ascending"):
        bad_thresh = PriorityThresholds(
            urgent=70.0,
            high=80.0,  # High > Urgent is invalid
            medium=40.0,
            low=0.0,
        )
        bad_thresh.validate()


def test_config_loader():
    cfg = PriorityConfig.load()
    assert cfg.version == "v1.0.0"
    assert abs(sum(cfg.weights.to_dict().values()) - 1.0) < 1e-4
    assert cfg.thresholds.urgent == 90.0
    assert cfg.thresholds.high == 70.0
    assert cfg.thresholds.medium == 40.0
