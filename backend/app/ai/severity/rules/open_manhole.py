"""Open manhole category severity evaluation rule."""
from typing import List
from .base_rule import BaseCategorySeverityRule


class OpenManholeSeverityRule(BaseCategorySeverityRule):
    """
    Evaluates open manhole severity.

    Considers:
    - Inherent critical fall/drop hazard (high baseline safety risk)
    - Obstruction and exposure in accessible public thoroughfares
    - Avoids assuming specific pedestrian presence while recognizing acute hazard.
    """

    def __init__(self):
        super().__init__("open_manhole")

    def evaluate_safety_risk(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        # Open drop hazards start at very high baseline (90)
        risk = (
            self.config.safety_hazard_base * 0.55
            + damage_extent_score * 0.25 * self.config.obstruction_multiplier
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
            self.config.infrastructure_base * 0.50
            + damage_extent_score * 0.40
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
            self.config.public_impact_base * 0.50
            + damage_extent_score * 0.35
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
        factors = [
            "Critical physical drop hazard: uncovered subsurface chamber exposed to transit area.",
            "Potential high-consequence risk to motorized and non-motorized traffic.",
        ]
        if damage_extent_score >= 50.0:
            factors.append("Large uncovered manhole aperture with substantial passage hazard.")
        else:
            factors.append("Standard aperture open access point lacking protective cover or barrier.")
        return factors
