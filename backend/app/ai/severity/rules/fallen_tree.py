"""Fallen tree category severity evaluation rule."""
from typing import List
from .base_rule import BaseCategorySeverityRule


class FallenTreeSeverityRule(BaseCategorySeverityRule):
    """
    Evaluates fallen tree severity.

    Considers:
    - Visible blockage scale across roadway or thoroughfare (high obstruction)
    - Overhead line interference or total blockage proxy
    - Disclaimer: Avoids speculating on unseen structural damage outside image.
    """

    def __init__(self):
        super().__init__("fallen_tree")

    def evaluate_safety_risk(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        # Fallen trees block entire roads and represent acute hazards
        risk = (
            self.config.safety_hazard_base * 0.45
            + damage_extent_score * 0.35 * self.config.obstruction_multiplier
            + (detection_confidence * 100.0) * 0.10
            + text_urgency * 0.10
        )
        return round(min(100.0, max(0.0, risk)), 1)

    def evaluate_infrastructure_impact(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
    ) -> float:
        impact = (
            self.config.infrastructure_base * 0.45
            + damage_extent_score * 0.45
            + (detection_confidence * 100.0) * 0.10
        )
        return round(min(100.0, max(0.0, impact)), 1)

    def evaluate_public_impact(
        self,
        damage_extent_score: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        impact = (
            self.config.public_impact_base * 0.45
            + damage_extent_score * 0.40
            + text_urgency * 0.15
        )
        return round(min(100.0, max(0.0, impact)), 1)

    def generate_factors(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> List[str]:
        factors = ["Fallen tree or major branch obstructing public right-of-way."]
        if damage_extent_score >= 60.0:
            factors.append("Substantial physical blockage spanning broad portion of thoroughfare.")
        return factors
