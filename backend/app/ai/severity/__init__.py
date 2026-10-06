"""AI Severity Assessment and Damage Impact Analysis package."""
from .config import severity_config, SeverityConfig
from .damage_extent import calculate_damage_extent, DISCLAIMER_DAMAGE_EXTENT
from .text_signals import extract_text_severity_signal
from .location_context import LocationContextService
from .safety_risk import calculate_safety_risk
from .infrastructure_impact import calculate_infrastructure_impact
from .public_impact import calculate_public_impact
from .scoring import (
    calculate_single_severity_score,
    aggregate_multi_detection_severities,
    map_score_to_severity_level,
)
from .explainer import generate_severity_explanation, AI_DECISION_SUPPORT_NOTICE
from .severity_service import SeverityAssessmentService

__all__ = [
    "severity_config",
    "SeverityConfig",
    "calculate_damage_extent",
    "DISCLAIMER_DAMAGE_EXTENT",
    "extract_text_severity_signal",
    "LocationContextService",
    "calculate_safety_risk",
    "calculate_infrastructure_impact",
    "calculate_public_impact",
    "calculate_single_severity_score",
    "aggregate_multi_detection_severities",
    "map_score_to_severity_level",
    "generate_severity_explanation",
    "AI_DECISION_SUPPORT_NOTICE",
    "SeverityAssessmentService",
]
