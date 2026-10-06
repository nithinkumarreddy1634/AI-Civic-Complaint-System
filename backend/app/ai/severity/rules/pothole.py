"""Pothole category severity evaluation rule."""
from typing import List
from .base_rule import BaseCategorySeverityRule


class PotholeSeverityRule(BaseCategorySeverityRule):
    """
    Evaluates pothole severity.

    Considers:
    - Visible surface disruption area (damage extent)
    - Cluster count (multiple potholes in one road section)
    - Roadway obstruction multiplier
    - User description signals without depth speculation
    """

    def __init__(self):
        super().__init__("pothole")

    def evaluate_safety_risk(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        # Base safety hazard (65) modulated by damage extent and cluster count
        count_boost = min(20.0, (count - 1) * 8.0)
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
        count_boost = min(25.0, (count - 1) * 10.0)
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
        count_boost = min(20.0, (count - 1) * 7.0)
        impact = (
            self.config.public_impact_base * 0.40
            + damage_extent_score * 0.40
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
            factors.append(f"Multiple pothole regions detected ({count} distinct defects).")
        else:
            factors.append("Isolated pothole defect detected on roadway surface.")

        if damage_extent_score >= 70.0:
            factors.append("Extensive visible road surface disruption occupying large road section.")
        elif damage_extent_score >= 40.0:
            factors.append("Moderate visible road surface defect.")
        else:
            factors.append("Localized small pothole region.")

        if text_urgency >= 60.0:
            factors.append("Citizen report indicates significant vehicular obstruction or depth hazard.")

        return factors
