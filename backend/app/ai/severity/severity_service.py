"""Orchestrator for AI Severity Assessment & Damage Impact Analysis."""
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from .config import severity_config
from .damage_extent import calculate_damage_extent
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
from .explainer import generate_severity_explanation
from .rules.registry import get_severity_rule

logger = logging.getLogger(__name__)

MODEL_VERSION = "civic_yolo_v1"


class SeverityAssessmentService:
    """Master service for computing damage impact, risk dimensions, and severity scores."""

    def __init__(self):
        self.config = severity_config
        self.location_service = LocationContextService()
        self.model_version = MODEL_VERSION

    def assess(
        self,
        detections: List[Dict[str, Any]],
        image_metadata: Dict[str, Any],
        description: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute full severity and damage impact analysis.

        Args:
            detections: List of detection dicts (class_name, confidence, bbox [x1, y1, x2, y2]).
            image_metadata: Dict with width and height in pixels (e.g. {"width": 640, "height": 480}).
            description: Optional citizen description text.
            location: Optional dict with latitude and longitude.

        Returns:
            Structured severity analysis dictionary.
        """
        start_time = time.perf_counter()

        img_width = image_metadata.get("width", 640) if image_metadata else 640
        img_height = image_metadata.get("height", 480) if image_metadata else 480

        # Step 1: Text analysis
        text_info = extract_text_severity_signal(description)
        text_urgency = text_info["text_severity_score"]
        text_cues = text_info["high_severity_cues"]

        # Step 2: Location context
        loc_lat = location.get("latitude") if location else None
        loc_lon = location.get("longitude") if location else None
        loc_info = self.location_service.analyze(loc_lat, loc_lon)

        # Handle zero detections
        if not detections:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "severity_score": 10.0,
                "severity_level": "LOW",
                "safety_risk_score": 10.0,
                "infrastructure_impact_score": 10.0,
                "public_impact_score": 10.0,
                "detection_analysis": [],
                "evidence": {
                    "damage_extent": 0.0,
                    "safety_risk": 10.0,
                    "infrastructure_impact": 10.0,
                    "public_impact": 10.0,
                    "detection_confidence": 0.0,
                    "text_signal": text_urgency,
                },
                "factors": ["No civic infrastructure defect detected in the image."],
                "explanation": [
                    "No problematic infrastructure defects were identified in the visual analysis.",
                    "Severity assessed as minimal (LOW).",
                ],
                "model_version": self.model_version,
                "severity_config_version": self.config.version,
                "processing_time_ms": duration_ms,
            }

        # Step 3: Analyze each individual detection
        detection_analyses = []
        detection_scores = []
        category_counts: Dict[str, int] = {}
        for d in detections:
            cat = d.get("class_name") or d.get("category") or "other"
            cat = str(cat).lower()
            category_counts[cat] = category_counts.get(cat, 0) + 1

        all_factors: List[str] = []
        primary_disclaimer = ""

        for idx, d in enumerate(detections):
            category = d.get("class_name") or d.get("category") or "other"
            category = str(category).lower()
            conf = float(d.get("confidence", 0.70))
            bbox = d.get("bbox", [])

            # Geometry extent
            extent_info = calculate_damage_extent(bbox, img_width, img_height)
            damage_score = extent_info["damage_extent_score"]

            # Count of this category across whole image
            cat_count = category_counts.get(category, 1)

            # Dimension scores
            safety_res = calculate_safety_risk(
                category=category,
                damage_extent_score=damage_score,
                detection_confidence=conf,
                count=cat_count,
                text_urgency=text_urgency,
            )

            infra_res = calculate_infrastructure_impact(
                category=category,
                damage_extent_score=damage_score,
                detection_confidence=conf,
                count=cat_count,
            )

            public_res = calculate_public_impact(
                category=category,
                damage_extent_score=damage_score,
                count=cat_count,
                text_urgency=text_urgency,
            )

            # Composite score for this single detection
            det_severity = calculate_single_severity_score(
                damage_extent_score=damage_score,
                detection_confidence=conf,
                safety_risk_score=safety_res["safety_risk_score"],
                infrastructure_impact_score=infra_res["infrastructure_impact_score"],
                public_impact_score=public_res["public_impact_score"],
            )

            detection_scores.append(det_severity)

            # Record analysis item
            analysis_item = {
                "category": category,
                "confidence": round(conf, 4),
                "damage_extent_score": damage_score,
                "damage_area_ratio": extent_info["damage_area_ratio"],
                "safety_risk_score": safety_res["safety_risk_score"],
                "infrastructure_impact_score": infra_res["infrastructure_impact_score"],
                "public_impact_score": public_res["public_impact_score"],
                "severity_contribution": det_severity,
                "bbox": bbox,
            }
            detection_analyses.append(analysis_item)

            rule = get_severity_rule(category)
            if idx == 0:
                primary_disclaimer = rule.get_disclaimer()
            rule_factors = rule.generate_factors(
                damage_extent_score=damage_score,
                detection_confidence=conf,
                count=cat_count,
                text_urgency=text_urgency,
            )
            all_factors.extend(rule_factors)
            all_factors.extend(safety_res["factors"])
            all_factors.extend(infra_res["factors"])

        # Step 4: Multi-detection aggregation
        final_severity_score = aggregate_multi_detection_severities(detection_scores)
        final_level = map_score_to_severity_level(final_severity_score)

        # Primary detection metrics for top-level presentation
        primary_det = detection_analyses[0]
        max_safety = max(d["safety_risk_score"] for d in detection_analyses)
        max_infra = max(d["infrastructure_impact_score"] for d in detection_analyses)
        max_public = max(d["public_impact_score"] for d in detection_analyses)
        max_damage = max(d["damage_extent_score"] for d in detection_analyses)

        # Unique factors list
        unique_factors = list(dict.fromkeys(all_factors))
        if loc_info["has_location"] and not loc_info["is_valid_coordinates"]:
            unique_factors.append("Supplied geographic coordinates were invalid.")

        # Step 5: Explanations
        explanation = generate_severity_explanation(
            category=primary_det["category"],
            severity_level=final_level,
            severity_score=final_severity_score,
            damage_extent_score=max_damage,
            detection_confidence=primary_det["confidence"],
            safety_risk_score=max_safety,
            infrastructure_impact_score=max_infra,
            public_impact_score=max_public,
            detection_count=len(detections),
            text_cues=text_cues,
            disclaimer=primary_disclaimer,
        )

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "severity_score": final_severity_score,
            "severity_level": final_level,
            "safety_risk_score": max_safety,
            "infrastructure_impact_score": max_infra,
            "public_impact_score": max_public,
            "detection_analysis": detection_analyses,
            "evidence": {
                "damage_extent": max_damage,
                "safety_risk": max_safety,
                "infrastructure_impact": max_infra,
                "public_impact": max_public,
                "detection_confidence": round(primary_det["confidence"] * 100.0, 1),
                "text_signal": text_urgency,
            },
            "factors": unique_factors,
            "explanation": explanation,
            "model_version": self.model_version,
            "severity_config_version": self.config.version,
            "processing_time_ms": duration_ms,
        }
