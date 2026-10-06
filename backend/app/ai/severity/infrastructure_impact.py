"""Infrastructure impact score computation engine."""
from typing import Dict, Any, List
from .rules.registry import get_severity_rule


def calculate_infrastructure_impact(
    category: str,
    damage_extent_score: float,
    detection_confidence: float,
    count: int = 1,
) -> Dict[str, Any]:
    """
    Calculate physical infrastructure impact score (0–100) and factors.

    Considers physical damage scale, structural asset degradation, and asset count.
    """
    rule = get_severity_rule(category)
    score = rule.evaluate_infrastructure_impact(
        damage_extent_score=damage_extent_score,
        detection_confidence=detection_confidence,
        count=count,
    )

    if score >= 75.0:
        level = "HIGH"
    elif score >= 40.0:
        level = "MEDIUM"
    else:
        level = "LOW"

    factors = []
    if damage_extent_score >= 60.0:
        factors.append(f"Substantial physical disruption to {category} infrastructure element.")
    else:
        factors.append(f"Localized surface damage to municipal asset.")

    if count > 1:
        factors.append(f"Cumulative structural damage across {count} defect loci.")

    return {
        "infrastructure_impact_score": score,
        "level": level,
        "factors": factors,
    }
