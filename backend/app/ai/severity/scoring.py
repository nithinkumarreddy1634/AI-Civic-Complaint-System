"""Multi-factor evidence fusion and severity aggregation engine."""
from typing import Dict, Any, List
from .config import severity_config


def calculate_single_severity_score(
    damage_extent_score: float,
    detection_confidence: float,
    safety_risk_score: float,
    infrastructure_impact_score: float,
    public_impact_score: float,
) -> float:
    """
    Compute composite severity score for a single detection from its dimension components.

    Formula:
        Score = w_damage * damage_extent
              + w_conf * (confidence * 100)
              + w_safety * safety_risk
              + w_infra * infrastructure_impact
              + w_public * public_impact
    """
    w = severity_config.weights
    conf_score = detection_confidence * 100.0

    raw_score = (
        w.damage_extent * damage_extent_score
        + w.detection_confidence * conf_score
        + w.safety_risk * safety_risk_score
        + w.infrastructure_impact * infrastructure_impact_score
        + w.public_impact * public_impact_score
    )

    return round(max(0.0, min(100.0, raw_score)), 1)


def aggregate_multi_detection_severities(
    detection_contributions: List[float],
) -> float:
    """
    Aggregate severity contributions from multiple detected defects.

    Uses a soft-saturating diminishing marginal contribution algorithm:
        Aggregated = Primary_Max + sum_{others} (other_i * factor)
    clamped at 100.0.

    Ensures multiple defects increase overall severity while preventing artificial overflow.
    """
    if not detection_contributions:
        return 0.0

    sorted_scores = sorted(detection_contributions, reverse=True)
    primary = sorted_scores[0]

    factor = severity_config.multi_detection_factor
    remaining_sum = sum(s * factor for s in sorted_scores[1:])

    aggregated = primary + remaining_sum
    return round(max(0.0, min(100.0, aggregated)), 1)


def map_score_to_severity_level(score: float) -> str:
    """Map continuous severity score (0–100) to discrete severity level."""
    t = severity_config.thresholds
    if score >= t.critical:
        return "CRITICAL"
    elif score >= t.high:
        return "HIGH"
    elif score >= t.medium:
        return "MEDIUM"
    else:
        return "LOW"
