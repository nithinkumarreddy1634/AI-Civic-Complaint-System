"""Safety risk score computation engine."""
from typing import Dict, Any, List
from .rules.registry import get_severity_rule


def calculate_safety_risk(
    category: str,
    damage_extent_score: float,
    detection_confidence: float,
    count: int = 1,
    text_urgency: float = 0.0,
) -> Dict[str, Any]:
    """
    Calculate safety risk score and explanatory factors.

    Represents potential safety implications based on observable evidence,
    avoiding unsupported claims about verified injuries or accidents.
    """
    rule = get_severity_rule(category)
    score = rule.evaluate_safety_risk(
        damage_extent_score=damage_extent_score,
        detection_confidence=detection_confidence,
        count=count,
        text_urgency=text_urgency,
    )

    if score >= 75.0:
        level = "CRITICAL" if score >= 90.0 else "HIGH"
    elif score >= 40.0:
        level = "MEDIUM"
    else:
        level = "LOW"

    factors = []
    if score >= 75.0:
        factors.append(f"Elevated safety risk associated with {category} defect geometry.")
    elif score >= 40.0:
        factors.append(f"Moderate potential safety concern under standard transit conditions.")
    else:
        factors.append(f"Low acute safety hazard observed.")

    if count > 1:
        factors.append(f"Multiple defect sites ({count}) increase composite traversal risk.")

    return {
        "safety_risk_score": score,
        "level": level,
        "factors": factors,
    }
