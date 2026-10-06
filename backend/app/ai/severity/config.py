"""Configuration management for AI Severity Assessment and Damage Impact Analysis."""
import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class SeverityThresholds:
    low: float = 0.0
    medium: float = 40.0
    high: float = 70.0
    critical: float = 90.0


@dataclass
class SeverityWeights:
    damage_extent: float = 0.20
    detection_confidence: float = 0.10
    safety_risk: float = 0.30
    infrastructure_impact: float = 0.20
    public_impact: float = 0.20


@dataclass
class DamageExtentConfig:
    max_reference_ratio: float = 0.15
    min_score: float = 5.0
    max_score: float = 100.0


@dataclass
class CategorySeverityConfig:
    safety_hazard_base: float = 50.0
    infrastructure_base: float = 50.0
    public_impact_base: float = 50.0
    obstruction_multiplier: float = 1.0
    disclaimer: str = ""


@dataclass
class SeverityConfig:
    version: str = "v1.0.0"
    thresholds: SeverityThresholds = field(default_factory=SeverityThresholds)
    weights: SeverityWeights = field(default_factory=SeverityWeights)
    damage_extent: DamageExtentConfig = field(default_factory=DamageExtentConfig)
    multi_detection_factor: float = 0.30
    categories: Dict[str, CategorySeverityConfig] = field(default_factory=dict)

    @classmethod
    def load(cls, config_path: str = None) -> "SeverityConfig":
        """Load configuration from YAML file or return robust default."""
        if config_path is None:
            # Default lookup relative to backend directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            config_path = os.path.join(base_dir, "config", "severity.yaml")

        if not os.path.exists(config_path):
            return cls._build_default()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            sev = data.get("severity", {})
            thresh_data = sev.get("thresholds", {})
            weights_data = sev.get("weights", {})
            extent_data = sev.get("damage_extent", {})
            multi_data = sev.get("multi_detection", {})
            cats_data = sev.get("categories", {})

            thresholds = SeverityThresholds(
                low=float(thresh_data.get("low", 0.0)),
                medium=float(thresh_data.get("medium", 40.0)),
                high=float(thresh_data.get("high", 70.0)),
                critical=float(thresh_data.get("critical", 90.0)),
            )

            weights = SeverityWeights(
                damage_extent=float(weights_data.get("damage_extent", 0.20)),
                detection_confidence=float(weights_data.get("detection_confidence", 0.10)),
                safety_risk=float(weights_data.get("safety_risk", 0.30)),
                infrastructure_impact=float(weights_data.get("infrastructure_impact", 0.20)),
                public_impact=float(weights_data.get("public_impact", 0.20)),
            )

            damage_extent = DamageExtentConfig(
                max_reference_ratio=float(extent_data.get("max_reference_ratio", 0.15)),
                min_score=float(extent_data.get("min_score", 5.0)),
                max_score=float(extent_data.get("max_score", 100.0)),
            )

            multi_factor = float(multi_data.get("subsequent_weight_factor", 0.30))

            categories = {}
            for cat_name, cat_vals in cats_data.items():
                categories[cat_name.lower()] = CategorySeverityConfig(
                    safety_hazard_base=float(cat_vals.get("safety_hazard_base", 50.0)),
                    infrastructure_base=float(cat_vals.get("infrastructure_base", 50.0)),
                    public_impact_base=float(cat_vals.get("public_impact_base", 50.0)),
                    obstruction_multiplier=float(cat_vals.get("obstruction_multiplier", 1.0)),
                    disclaimer=str(cat_vals.get("disclaimer", "")),
                )

            return cls(
                version=data.get("version", "v1.0.0"),
                thresholds=thresholds,
                weights=weights,
                damage_extent=damage_extent,
                multi_detection_factor=multi_factor,
                categories=categories,
            )
        except Exception:
            return cls._build_default()

    @classmethod
    def _build_default(cls) -> "SeverityConfig":
        default_cats = {
            "pothole": CategorySeverityConfig(65.0, 70.0, 60.0, 1.2, "Bounding box area approximates 2D surface disruption; physical depth is not estimated."),
            "garbage": CategorySeverityConfig(40.0, 50.0, 65.0, 1.1, "Assesses visible waste accumulation area; does not infer biochemical contamination."),
            "open_manhole": CategorySeverityConfig(90.0, 75.0, 80.0, 1.3, "Open manholes present immediate drop hazards in public access areas."),
            "damaged_road": CategorySeverityConfig(65.0, 80.0, 70.0, 1.25, "Assesses visible structural roadway fracturing and asphalt degradation."),
            "broken_streetlight": CategorySeverityConfig(50.0, 60.0, 55.0, 1.0, "Identifies loss of roadway illumination infrastructure; does not confirm crime incidence."),
            "water_leakage": CategorySeverityConfig(55.0, 75.0, 65.0, 1.15, "Assesses visible pooling scale; does not speculate on potable water contamination."),
            "damaged_sidewalk": CategorySeverityConfig(55.0, 65.0, 60.0, 1.1, "Evaluates pedestrian walkway surface discontinuity and tripping hazard proxies."),
            "fallen_tree": CategorySeverityConfig(85.0, 75.0, 85.0, 1.4, "Evaluates physical transit blocking scale and utility interference."),
            "illegal_dumping": CategorySeverityConfig(45.0, 55.0, 70.0, 1.15, "Identifies civic waste accumulation; makes no accusation regarding responsible parties."),
            "other": CategorySeverityConfig(50.0, 50.0, 50.0, 1.0, "General civic defect baseline."),
        }
        return cls(categories=default_cats)


# Global singleton instance
severity_config = SeverityConfig.load()
