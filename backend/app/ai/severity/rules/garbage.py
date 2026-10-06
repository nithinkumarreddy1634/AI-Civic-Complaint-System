"""Garbage category severity evaluation rule."""
from typing import List
from .base_rule import BaseCategorySeverityRule


class GarbageSeverityRule(BaseCategorySeverityRule):
    """
    Evaluates garbage accumulation severity.

    Considers:
    - Visible accumulation area (damage extent)
    - Number of separate waste deposits
    - Pathway and public access obstruction
    - Disclaimer: Avoids speculating on biohazard/disease contamination.
    """

    def __init__(self):
        super().__init__("garbage")

    def evaluate_safety_risk(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        # Base safety hazard (40) is lower than road drops, but rises if obstruction is large
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
        count_boost = min(15.0, (count - 1) * 7.0)
        impact = (
            self.config.infrastructure_base * 0.40
            + damage_extent_score * 0.50
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
        # Public impact is inherently high for uncollected solid waste
        count_boost = min(20.0, (count - 1) * 8.0)
        impact = (
            self.config.public_impact_base * 0.45
            + damage_extent_score * 0.40
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
        if count > 1:
            factors.append(f"Multiple separate waste piles detected ({count} accumulation spots).")
        else:
            factors.append("Waste accumulation detected in public vicinity.")

        if damage_extent_score >= 70.0:
            factors.append("Large visual waste accumulation volume encroaching on public space.")
        elif damage_extent_score >= 40.0:
            factors.append("Moderate visible refuse accumulation.")
        else:
            factors.append("Localized minor waste scatter.")

        if text_urgency >= 60.0:
            factors.append("Report notes pedestrian obstruction or prolonged uncollected duration.")

        return factors
