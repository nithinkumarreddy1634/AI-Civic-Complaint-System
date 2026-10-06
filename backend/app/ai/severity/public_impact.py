"""Public impact score computation engine."""
from typing import Dict, Any, List
from .rules.registry import get_severity_rule


def calculate_public_impact(
    category: str,
    damage_extent_score: float,
    count: int = 1,
    text_urgency: float = 0.0,
) -> Dict[str, Any]:
    """
    Calculate public impact score (0–100) and factors.

    Considers public accessibility, transit/pathway blockage, and visible scale.
    """
    rule = get_severity_rule(category)
    score = rule.evaluate_public_impact(
        damage_extent_score=damage_extent_score,
        count=count,
        text_urgency=text_urgency,
    )

    if score >= 75.0:
        level = "HIGH"
    elif score >= 40.0:
        level = "MEDIUM"
    else:
        level = "LOW"

    factors = []
    if damage_extent_score >= 60.0:
        factors.append("Noticeable disruption to normal public thoroughfare and pedestrian access.")
    else:
        factors.append("Minor inconvenience to public passage.")

    return {
        "public_impact_score": score,
        "level": level,
        "factors": factors,
    }
