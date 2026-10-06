"""Base interface for category-specific severity rules."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..config import CategorySeverityConfig, severity_config


class BaseCategorySeverityRule(ABC):
    """Abstract base class for issue-specific severity evaluation rules."""

    def __init__(self, category_name: str):
        self.category_name = category_name
        self.config: CategorySeverityConfig = severity_config.categories.get(
            category_name.lower(),
            severity_config.categories.get("other", CategorySeverityConfig())
        )

    @abstractmethod
    def evaluate_safety_risk(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        """Calculate safety risk contribution (0–100) for this issue."""
        pass

    @abstractmethod
    def evaluate_infrastructure_impact(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
    ) -> float:
        """Calculate infrastructure impact contribution (0–100) for this issue."""
        pass

    @abstractmethod
    def evaluate_public_impact(
        self,
        damage_extent_score: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> float:
        """Calculate public impact contribution (0–100) for this issue."""
        pass

    @abstractmethod
    def generate_factors(
        self,
        damage_extent_score: float,
        detection_confidence: float,
        count: int = 1,
        text_urgency: float = 0.0,
    ) -> List[str]:
        """Generate human-readable factual observations for this issue."""
        pass

    def get_disclaimer(self) -> str:
        """Return category-specific limitation or disclaimer."""
        return self.config.disclaimer
