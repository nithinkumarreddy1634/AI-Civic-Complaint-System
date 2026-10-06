"""Complaint verification pipeline orchestrator service.

Connects image quality, YOLO detection, civic relevance, NLP text extraction,
cross-modal consistency, and explainable decision scoring into a single unified service.
"""
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import numpy as np

from .config import VerificationConfig, DEFAULT_VERIFICATION_CONFIG, CONFIG_VERSION
from .image_quality import verify_image_quality
from .relevance import check_civic_relevance
from .text_analysis import analyze_description
from .consistency import evaluate_consistency
from .scoring import make_verification_decision

logger = logging.getLogger("verification_service")


class ComplaintVerificationService:
    """Master service for validating citizen civic infrastructure complaints."""

    def __init__(
        self,
        vision_model=None,
        config: VerificationConfig = DEFAULT_VERIFICATION_CONFIG
    ):
        self.config = config
        self._vision_model = vision_model
        self.model_version = "civic_yolo_v1"

    def _get_vision_model(self):
        """Lazy load CivicVisionModel if not provided in constructor."""
        if self._vision_model is None:
            try:
                from ml.inference.civic_vision_model import CivicVisionModel
                self._vision_model = CivicVisionModel()
                logger.info("Initialized CivicVisionModel in verification service.")
            except Exception as e:
                logger.warning(f"Could not load CivicVisionModel: {e}. Running in standalone verification mode.")
        return self._vision_model

    def verify_complaint(
        self,
        image_input: Union[Path, str, bytes, np.ndarray],
        description: Optional[str] = None,
        selected_category: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        mock_detections: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Runs the complete 9-stage verification pipeline on a complaint.

        Args:
            image_input: Path, bytes, or numpy array of complaint photograph.
            description: Citizen's natural language problem description.
            selected_category: Form category chosen by citizen (optional).
            latitude: GPS latitude (optional).
            longitude: GPS longitude (optional).
            mock_detections: Optional pre-computed detections for deterministic testing.

        Returns:
            Standardized verification payload with status, score, breakdown, and explanations.
        """
        start_time = time.perf_counter()
        verified_at = datetime.now(timezone.utc).isoformat()

        # Step 1: Image Quality Audit
        t_qual_start = time.perf_counter()
        quality_result = verify_image_quality(image_input)
        t_qual_ms = (time.perf_counter() - t_qual_start) * 1000.0

        # Step 2: YOLO Defect Detection
        t_yolo_start = time.perf_counter()
        detections: List[Dict[str, Any]] = []

        if mock_detections is not None:
            detections = mock_detections
        elif quality_result["valid"]:
            model = self._get_vision_model()
            if model is not None:
                try:
                    vision_res = model.predict(image_input)
                    detections = vision_res.get("detections", [])
                except Exception as e:
                    logger.error(f"YOLO model inference error: {e}")
        t_yolo_ms = (time.perf_counter() - t_yolo_start) * 1000.0

        # Step 3: Civic Relevance Verification
        relevance_result = check_civic_relevance(detections)

        # Step 4: NLP Description Parsing
        t_nlp_start = time.perf_counter()
        text_result = analyze_description(description)
        t_nlp_ms = (time.perf_counter() - t_nlp_start) * 1000.0

        # Step 5 & 6: Cross-Modal Consistency & Category Matching
        consistency_result = evaluate_consistency(
            vision_detections=detections,
            text_categories=text_result.get("text_categories", []),
            user_selected_category=selected_category
        )

        # Step 7, 8 & 9: Verification Scoring, Decision & Explainability
        status, score, explanations = make_verification_decision(
            quality_result=quality_result,
            relevance_result=relevance_result,
            consistency_result=consistency_result,
            detections=detections,
            text_result=text_result,
            config=self.config
        )

        total_time_ms = (time.perf_counter() - start_time) * 1000.0

        # Assemble standardized Phase 4 output payload
        primary_detected_class = detections[0].get("class_name") if detections else None
        primary_confidence = detections[0].get("confidence", 0.0) if detections else 0.0

        return {
            "verification_status": status,
            "verification_score": score,
            "detected_category": primary_detected_class,
            "detection_confidence": round(float(primary_confidence), 4),
            "image_quality": {
                "status": quality_result.get("status", "INVALID"),
                "score": quality_result.get("quality_score", 0),
                "issues": quality_result.get("issues", []),
                "metrics": quality_result.get("metrics", {})
            },
            "detections": detections,
            "relevance": {
                "is_relevant": relevance_result.get("is_relevant", False),
                "score": relevance_result.get("relevance_score", 0.0),
                "detected_issues": relevance_result.get("detected_issues", [])
            },
            "text_analysis": {
                "has_description": text_result.get("has_description", False),
                "categories": text_result.get("text_categories", []),
                "keywords": text_result.get("keywords_found", []),
                "urgency_markers": text_result.get("urgency_markers", [])
            },
            "consistency": {
                "score": consistency_result.get("consistency_score", 0.0),
                "matched": consistency_result.get("matched", False),
                "explanation": consistency_result.get("explanation", "")
            },
            "category_match": consistency_result.get("category_match", True),
            "selected_category": selected_category,
            "explanation": explanations,
            "audit_trail": {
                "model_version": self.model_version,
                "config_version": CONFIG_VERSION,
                "verified_at": verified_at,
                "timing_ms": {
                    "image_quality": round(t_qual_ms, 2),
                    "yolo_inference": round(t_yolo_ms, 2),
                    "nlp_analysis": round(t_nlp_ms, 2),
                    "total": round(total_time_ms, 2)
                }
            }
        }
