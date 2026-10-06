"""Intelligent Complaint Prioritization Engine.

Combines verified AI evidence into an explainable priority score with dynamic missing-data
re-normalization, exact factor contribution tracking, and priority tier classification.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from app.ai.priority.config import PriorityConfig, priority_config
from app.schemas.priority import PriorityLevel


@dataclass
class FactorContribution:
    raw_value: Any
    normalized_score: float
    nominal_weight: float
    effective_weight: float
    contribution: float
    status: str = "included"  # "included" or "redistributed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "raw_value": self.raw_value,
            "normalized_score": round(self.normalized_score, 2),
            "nominal_weight": round(self.nominal_weight, 4),
            "effective_weight": round(self.effective_weight, 4),
            "contribution": round(self.contribution, 2),
            "status": self.status,
        }


@dataclass
class PriorityEngineResult:
    priority_score: float
    priority_level: PriorityLevel
    base_score: float
    escalation_boost: float
    factor_breakdown: Dict[str, FactorContribution]
    total_effective_weight: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "priority_score": self.priority_score,
            "priority_level": self.priority_level.value,
            "base_score": self.base_score,
            "escalation_boost": self.escalation_boost,
            "factor_breakdown": {k: v.to_dict() for k, v in self.factor_breakdown.items()},
            "total_effective_weight": round(self.total_effective_weight, 4),
            "metadata": self.metadata,
        }


class PriorityEngine:
    """Core mathematical engine for computing explainable civic complaint priority."""

    def __init__(self, config: PriorityConfig = None):
        self.config = config or priority_config

    def calculate(
        self,
        severity_score: float,
        safety_risk_score: float,
        infrastructure_impact_score: float,
        public_impact_score: float,
        frequency_score: float,
        verification_confidence_score: float,
        location_score: Optional[float] = None,
        unresolved_days: float = 0.0,
        raw_report_count: int = 1,
    ) -> PriorityEngineResult:
        """Compute the weighted priority score and exact factor contributions.

        All component scores must be normalized between 0.0 and 100.0.
        If location_score is None, the engine redistributes location's nominal weight
        proportionately across the remaining 6 factors so that effective weights sum to 1.0.
        """
        nominal_weights = self.config.weights.to_dict()

        # Build raw components table
        components: Dict[str, Dict[str, Any]] = {
            "severity": {
                "raw": severity_score,
                "score": max(0.0, min(100.0, float(severity_score))),
                "available": True,
            },
            "safety_risk": {
                "raw": safety_risk_score,
                "score": max(0.0, min(100.0, float(safety_risk_score))),
                "available": True,
            },
            "infrastructure_impact": {
                "raw": infrastructure_impact_score,
                "score": max(0.0, min(100.0, float(infrastructure_impact_score))),
                "available": True,
            },
            "public_impact": {
                "raw": public_impact_score,
                "score": max(0.0, min(100.0, float(public_impact_score))),
                "available": True,
            },
            "complaint_frequency": {
                "raw": raw_report_count,
                "score": max(0.0, min(100.0, float(frequency_score))),
                "available": True,
            },
            "verification_confidence": {
                "raw": verification_confidence_score,
                "score": max(0.0, min(100.0, float(verification_confidence_score))),
                "available": True,
            },
            "location_impact": {
                "raw": location_score,
                "score": max(0.0, min(100.0, float(location_score))) if location_score is not None else 0.0,
                "available": location_score is not None,
            },
        }

        # Calculate sum of nominal weights for available factors
        available_nominal_sum = sum(
            nominal_weights[k] for k, comp in components.items() if comp["available"]
        )

        factor_breakdown: Dict[str, FactorContribution] = {}
        base_score = 0.0

        for factor_name, comp in components.items():
            nominal_w = nominal_weights[factor_name]
            if comp["available"]:
                # Renormalize weight so available factors sum to 1.0
                effective_w = nominal_w / available_nominal_sum
                contribution = effective_w * comp["score"]
                base_score += contribution
                factor_breakdown[factor_name] = FactorContribution(
                    raw_value=comp["raw"],
                    normalized_score=comp["score"],
                    nominal_weight=nominal_w,
                    effective_weight=effective_w,
                    contribution=contribution,
                    status="included",
                )
            else:
                factor_breakdown[factor_name] = FactorContribution(
                    raw_value=comp["raw"],
                    normalized_score=0.0,
                    nominal_weight=nominal_w,
                    effective_weight=0.0,
                    contribution=0.0,
                    status="redistributed",
                )

        # Escalation aging boost
        escalation_boost = 0.0
        if unresolved_days > 0.0:
            raw_boost = unresolved_days * self.config.escalation.unresolved_days_boost_per_day
            escalation_boost = min(raw_boost, self.config.escalation.max_escalation_boost)

        final_score = min(100.0, max(0.0, base_score + escalation_boost))
        final_score_rounded = round(final_score, 2)

        # Map to priority tier
        priority_level = self.determine_level(final_score_rounded)

        total_effective = sum(fc.effective_weight for fc in factor_breakdown.values())

        return PriorityEngineResult(
            priority_score=final_score_rounded,
            priority_level=priority_level,
            base_score=base_score,
            escalation_boost=escalation_boost,
            factor_breakdown=factor_breakdown,
            total_effective_weight=total_effective,
            metadata={
                "missing_gps_redistributed": location_score is None,
                "unresolved_days": unresolved_days,
            },
        )

    def determine_level(self, score: float) -> PriorityLevel:
        """Map score to PriorityLevel enum using configured thresholds."""
        thresholds = self.config.thresholds
        if score >= thresholds.urgent:
            return PriorityLevel.URGENT
        if score >= thresholds.high:
            return PriorityLevel.HIGH
        if score >= thresholds.medium:
            return PriorityLevel.MEDIUM
        return PriorityLevel.LOW


priority_engine = PriorityEngine()
