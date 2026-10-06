"""Broken streetlight category severity evaluation rule."""
from typing import List
from .base_rule import BaseCategorySeverityRule


class BrokenStreetlightSeverityRule(BaseCategorySeverityRule):
    """
    Evaluates broken streetlight severity.

    Considers:
    - Structural luminaire damage / exposed fixture
    - Potential nighttime visibility impairment
    - Disclaimer: Avoids speculating on specific crime or accidents.
    """

    def __init__(self):
        super().__init__("broken_streetlight")

    def evaluate_safety_risk(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        count_boost = min(15.0, (count - 1) * 7.0)
        risk = (
            self.config.safety_hazard_base * 0.45
            + damage_extent_score * 0.35
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
            self.config.infrastructure_base * 0.50
            + damage_extent_score * 0.40
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
        count_boost = min(20.0, (count - 1) * 8.0)
        impact = (
            self.config.public_impact_base * 0.45
            + damage_extent_score * 0.35
            + text_urgency * 0.20
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
        if count > 1:
            factors.append(f"Multiple streetlight fixtures inoperative or damaged ({count} fixtures).")
        else:
            factors.append("Damaged or inoperative street lighting fixture detected.")

        factors.append("Loss of nocturnal roadway/walkway illumination factor.")
        return factors
