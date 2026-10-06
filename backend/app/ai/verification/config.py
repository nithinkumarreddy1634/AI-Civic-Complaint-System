"""Configuration settings, scoring weights, and category ontology for complaint verification."""
from dataclasses import dataclass, field
from typing import Dict, List, Set

CONFIG_VERSION = "v1.0.0"

# Supported civic defect categories
SUPPORTED_CIVIC_CATEGORIES: Set[str] = {
    "pothole",
    "garbage",
    "open_manhole",
    "damaged_road",
    "broken_streetlight",
    "water_leakage",
    "damaged_sidewalk",
    "fallen_tree",
    "illegal_dumping",
}

# Domain affinity groups (classes that are conceptually related or frequently co-occur)
CATEGORY_AFFINITY_GROUPS: List[Set[str]] = [
    {"pothole", "damaged_road", "damaged_sidewalk"},
    {"garbage", "illegal_dumping"},
    {"open_manhole", "damaged_road", "water_leakage"},
    {"broken_streetlight", "damaged_sidewalk", "fallen_tree"},
    {"water_leakage", "damaged_road", "pothole"},
]


@dataclass
class ScoringWeights:
    """Configurable weights for the multi-factor verification formula (must sum to 1.0)."""
    detection_confidence: float = 0.35
    civic_relevance: float = 0.20
    text_consistency: float = 0.20
    category_agreement: float = 0.15
    image_quality: float = 0.10


@dataclass
class DecisionThresholds:
    """Configurable thresholds determining the final verification status."""
    verified: float = 75.0      # Score >= 75 -> VERIFIED (if no safety overrides trigger)
    needs_review: float = 50.0  # 50 <= Score < 75 -> NEEDS_REVIEW, Score < 50 -> REJECTED
    min_confidence_veto: float = 0.30  # Defect detections below this are treated as uncertain


@dataclass
class VerificationConfig:
    version: str = CONFIG_VERSION
    weights: ScoringWeights = field(default_factory=ScoringWeights)
    thresholds: DecisionThresholds = field(default_factory=DecisionThresholds)


DEFAULT_VERIFICATION_CONFIG = VerificationConfig()
