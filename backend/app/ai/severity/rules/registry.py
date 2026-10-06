"""Rule registry for category severity evaluators."""
from typing import Dict
from .base_rule import BaseCategorySeverityRule
from .pothole import PotholeSeverityRule
from .garbage import GarbageSeverityRule
from .open_manhole import OpenManholeSeverityRule
from .damaged_road import DamagedRoadSeverityRule
from .broken_streetlight import BrokenStreetlightSeverityRule
from .water_leakage import WaterLeakageSeverityRule
from .damaged_sidewalk import DamagedSidewalkSeverityRule
from .fallen_tree import FallenTreeSeverityRule
from .illegal_dumping import IllegalDumpingSeverityRule


class DefaultSeverityRule(BaseCategorySeverityRule):
    """Fallback rule for unmapped or generic civic issues."""

    def __init__(self, category_name: str = "other"):
        super().__init__(category_name)

    def evaluate_safety_risk(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        risk = (
            self.config.safety_hazard_base * 0.40
            + damage_extent_score * 0.40
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
    ) -> list[str]:
        return [f"General civic defect detected ({self.category_name})."]


_REGISTRY: Dict[str, BaseCategorySeverityRule] = {
    "pothole": PotholeSeverityRule(),
    "garbage": GarbageSeverityRule(),
    "garbage_accumulation": GarbageSeverityRule(),
    "open_manhole": OpenManholeSeverityRule(),
    "damaged_road": DamagedRoadSeverityRule(),
    "broken_streetlight": BrokenStreetlightSeverityRule(),
    "water_leakage": WaterLeakageSeverityRule(),
    "damaged_sidewalk": DamagedSidewalkSeverityRule(),
    "fallen_tree": FallenTreeSeverityRule(),
    "illegal_dumping": IllegalDumpingSeverityRule(),
}


def get_severity_rule(category_name: str) -> BaseCategorySeverityRule:
    """Retrieve the rule evaluator for a given category name."""
    norm = str(category_name).lower().strip().replace(" ", "_")
    if norm in _REGISTRY:
        return _REGISTRY[norm]
    return DefaultSeverityRule(category_name=norm)
