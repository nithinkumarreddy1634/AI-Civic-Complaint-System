"""Damaged road category severity evaluation rule."""
from typing import List
from .base_rule import BaseCategorySeverityRule


class DamagedRoadSeverityRule(BaseCategorySeverityRule):
    """
    Evaluates damaged road severity.

    Considers:
    - Asphalt fracturing, rutting, structural degradation
    - High infrastructure impact score
    - Multi-defect aggregation for extended road sections
    """

    def __init__(self):
        super().__init__("damaged_road")

    def evaluate_safety_risk(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        count_boost = min(15.0, (count - 1) * 6.0)
        risk = (
            self.config.safety_hazard_base * 0.40
            + damage_extent_score * 0.40 * self.config.obstruction_multiplier
            + (detection_confidence * 100.0) * 0.10
            + text_urgency * 0.10
            + count_boost
        )
        return round(min(100.0, max(0.0, risk)), 1)

    def evaluate_infrastructure_impact(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
    ) -> float:
        count_boost = min(20.0, (count - 1) * 8.0)
        impact = (
            self.config.infrastructure_base * 0.45
            + damage_extent_score * 0.45
            + (detection_confidence * 100.0) * 0.10
            + count_boost
        )
        return round(min(100.0, max(0.0, impact)), 1)

    def evaluate_public_impact(
        self,
        damage_extent_score: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        count_boost = min(15.0, (count - 1) * 6.0)
        impact = (
            self.config.public_impact_base * 0.40
            + damage_extent_score * 0.45
            + text_urgency * 0.15
            + count_boost
        )
        return round(min(100.0, max(0.0, impact)), 1)

    def generate_factors(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> List[str]:
        factors = []
        if damage_extent_score >= 65.0:
            factors.append("Extensive structural road surface deterioration over wide thoroughfare area.")
        else:
            factors.append("Visible road surface degradation and pavement cracking.")

        if count > 1:
            factors.append(f"Multiple damaged pavement segments detected ({count} regions).")

        return factors
