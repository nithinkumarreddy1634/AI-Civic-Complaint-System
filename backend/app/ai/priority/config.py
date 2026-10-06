"""Configuration management and validation for the AI Complaint Prioritization Engine."""
import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class PriorityWeights:
    severity: float = 0.25
    safety_risk: float = 0.25
    infrastructure_impact: float = 0.15
    public_impact: float = 0.15
    complaint_frequency: float = 0.10
    location_impact: float = 0.05
    verification_confidence: float = 0.05

    def validate(self) -> None:
        """Validate that all weights are non-negative and sum to 1.0."""
        weight_values = [
            self.severity,
            self.safety_risk,
            self.infrastructure_impact,
            self.public_impact,
            self.complaint_frequency,
            self.location_impact,
            self.verification_confidence,
        ]
        for w in weight_values:
            if w < 0.0 or w > 1.0:
                raise ValueError(f"Weight value {w} must be between 0.0 and 1.0")

        total = sum(weight_values)
        if abs(total - 1.0) > 1e-4:
            raise ValueError(f"Priority weights must sum to 1.0, got {total:.4f}")

    def to_dict(self) -> Dict[str, float]:
        return {
            "severity": self.severity,
            "safety_risk": self.safety_risk,
            "infrastructure_impact": self.infrastructure_impact,
            "public_impact": self.public_impact,
            "complaint_frequency": self.complaint_frequency,
            "location_impact": self.location_impact,
            "verification_confidence": self.verification_confidence,
        }


@dataclass
class PriorityThresholds:
    urgent: float = 90.0
    high: float = 70.0
    medium: float = 40.0
    low: float = 0.0

    def validate(self) -> None:
        if not (self.low < self.medium < self.high < self.urgent):
            raise ValueError(
                f"Thresholds must be strictly ascending: low ({self.low}) < "
                f"medium ({self.medium}) < high ({self.high}) < urgent ({self.urgent})"
            )


@dataclass
class FrequencyScalingConfig:
    saturation_cap: int = 20
    breakpoints: Dict[int, float] = field(default_factory=lambda: {
        1: 15.0,
        2: 28.0,
        3: 40.0,
        5: 60.0,
        8: 75.0,
        10: 85.0,
        15: 95.0,
        20: 100.0,
    })


@dataclass
class LocationImpactConfig:
    default_score: float = 50.0
    missing_gps_behavior: str = "redistribute"  # "redistribute" or "zero"


@dataclass
class EscalationConfig:
    unresolved_days_boost_per_day: float = 1.5
    max_escalation_boost: float = 20.0


@dataclass
class PriorityConfig:
    version: str = "v1.0.0"
    weights: PriorityWeights = field(default_factory=PriorityWeights)
    thresholds: PriorityThresholds = field(default_factory=PriorityThresholds)
    frequency_scaling: FrequencyScalingConfig = field(default_factory=FrequencyScalingConfig)
    location_impact: LocationImpactConfig = field(default_factory=LocationImpactConfig)
    escalation: EscalationConfig = field(default_factory=EscalationConfig)

    def __post_init__(self):
        self.weights.validate()
        self.thresholds.validate()

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "PriorityConfig":
        """Load priority configuration from YAML file or return defaults."""
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            config_path = os.path.join(base_dir, "config", "priority.yaml")

        if not os.path.exists(config_path):
            cfg = cls()
            return cfg

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            prio = data.get("priority", {})
            w_data = prio.get("weights", {})
            t_data = prio.get("thresholds", {})
            f_data = prio.get("frequency_scaling", {})
            l_data = prio.get("location_impact", {})
            e_data = prio.get("escalation", {})

            # Convert breakpoint keys to int if necessary
            raw_bp = f_data.get("breakpoints", {})
            parsed_bp = {int(k): float(v) for k, v in raw_bp.items()} if raw_bp else {
                1: 15.0, 2: 28.0, 3: 40.0, 5: 60.0, 8: 75.0, 10: 85.0, 15: 95.0, 20: 100.0
            }

            weights = PriorityWeights(
                severity=float(w_data.get("severity", 0.25)),
                safety_risk=float(w_data.get("safety_risk", 0.25)),
                infrastructure_impact=float(w_data.get("infrastructure_impact", 0.15)),
                public_impact=float(w_data.get("public_impact", 0.15)),
                complaint_frequency=float(w_data.get("complaint_frequency", 0.10)),
                location_impact=float(w_data.get("location_impact", 0.05)),
                verification_confidence=float(w_data.get("verification_confidence", 0.05)),
            )

            thresholds = PriorityThresholds(
                urgent=float(t_data.get("urgent", 90.0)),
                high=float(t_data.get("high", 70.0)),
                medium=float(t_data.get("medium", 40.0)),
                low=float(t_data.get("low", 0.0)),
            )

            return cls(
                version=data.get("version", "v1.0.0"),
                weights=weights,
                thresholds=thresholds,
                frequency_scaling=FrequencyScalingConfig(
                    saturation_cap=int(f_data.get("saturation_cap", 20)),
                    breakpoints=parsed_bp,
                ),
                location_impact=LocationImpactConfig(
                    default_score=float(l_data.get("default_score", 50.0)),
                    missing_gps_behavior=str(l_data.get("missing_gps_behavior", "redistribute")),
                ),
                escalation=EscalationConfig(
                    unresolved_days_boost_per_day=float(e_data.get("unresolved_days_boost_per_day", 1.5)),
                    max_escalation_boost=float(e_data.get("max_escalation_boost", 20.0)),
                ),
            )
        except Exception as e:
            # Fallback to default if load fails
            return cls()


priority_config = PriorityConfig.load()
