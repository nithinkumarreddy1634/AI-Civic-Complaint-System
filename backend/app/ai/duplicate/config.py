"""Configuration management for AI Duplicate Complaint Detection."""
import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class GeographicConfig:
    candidate_radius_meters: float = 500.0
    high_similarity_radius_meters: float = 50.0
    max_duplicate_distance_meters: float = 1000.0


@dataclass
class DuplicateWeights:
    location: float = 0.30
    image: float = 0.35
    text: float = 0.20
    category: float = 0.15


@dataclass
class NoLocationWeights:
    image: float = 0.50
    text: float = 0.30
    category: float = 0.20


@dataclass
class DuplicateThresholds:
    possible_duplicate: float = 60.0
    likely_duplicate: float = 80.0


@dataclass
class ModelMeta:
    name: str = "mobilenet_v3_feature_extractor"
    version: str = "v1.0.0"
    dimension: int = 512


@dataclass
class DuplicateConfig:
    version: str = "v1.0.0"
    geographic: GeographicConfig = field(default_factory=GeographicConfig)
    weights: DuplicateWeights = field(default_factory=DuplicateWeights)
    no_location_weights: NoLocationWeights = field(default_factory=NoLocationWeights)
    thresholds: DuplicateThresholds = field(default_factory=DuplicateThresholds)
    max_candidates_to_compare: int = 15
    max_candidates_to_return: int = 5
    image_model: ModelMeta = field(default_factory=lambda: ModelMeta("mobilenet_v3_feature_extractor", "v1.0.0", 512))
    text_model: ModelMeta = field(default_factory=lambda: ModelMeta("semantic_civic_embedder", "v1.0.0", 384))

    @classmethod
    def load(cls, config_path: str = None) -> "DuplicateConfig":
        """Load duplicate configuration from YAML or fallback to default."""
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            config_path = os.path.join(base_dir, "config", "duplicate.yaml")

        if not os.path.exists(config_path):
            return cls()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            dup = data.get("duplicate", {})
            geo = dup.get("geographic", {})
            weights_data = dup.get("weights", {})
            no_loc_data = dup.get("no_location_weights", {})
            thresh_data = dup.get("thresholds", {})
            limits_data = dup.get("limits", {})
            models_data = dup.get("models", {})
            img_m = models_data.get("image", {})
            txt_m = models_data.get("text", {})

            return cls(
                version=data.get("version", "v1.0.0"),
                geographic=GeographicConfig(
                    candidate_radius_meters=float(geo.get("candidate_radius_meters", 500.0)),
                    high_similarity_radius_meters=float(geo.get("high_similarity_radius_meters", 50.0)),
                    max_duplicate_distance_meters=float(geo.get("max_duplicate_distance_meters", 1000.0)),
                ),
                weights=DuplicateWeights(
                    location=float(weights_data.get("location", 0.30)),
                    image=float(weights_data.get("image", 0.35)),
                    text=float(weights_data.get("text", 0.20)),
                    category=float(weights_data.get("category", 0.15)),
                ),
                no_location_weights=NoLocationWeights(
                    image=float(no_loc_data.get("image", 0.50)),
                    text=float(no_loc_data.get("text", 0.30)),
                    category=float(no_loc_data.get("category", 0.20)),
                ),
                thresholds=DuplicateThresholds(
                    possible_duplicate=float(thresh_data.get("possible_duplicate", 60.0)),
                    likely_duplicate=float(thresh_data.get("likely_duplicate", 80.0)),
                ),
                max_candidates_to_compare=int(limits_data.get("max_candidates_to_compare", 15)),
                max_candidates_to_return=int(limits_data.get("max_candidates_to_return", 5)),
                image_model=ModelMeta(
                    name=str(img_m.get("name", "mobilenet_v3_feature_extractor")),
                    version=str(img_m.get("version", "v1.0.0")),
                    dimension=int(img_m.get("dimension", 512)),
                ),
                text_model=ModelMeta(
                    name=str(txt_m.get("name", "semantic_civic_embedder")),
                    version=str(txt_m.get("version", "v1.0.0")),
                    dimension=int(txt_m.get("dimension", 384)),
                ),
            )
        except Exception:
            return cls()


duplicate_config = DuplicateConfig.load()
