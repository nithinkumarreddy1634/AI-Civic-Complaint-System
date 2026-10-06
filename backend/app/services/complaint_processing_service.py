"""Complaint Processing Orchestrator connecting all AI modules into one workflow."""
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.complaint import Complaint, ComplaintStatus, ProcessingState
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from app.models.priority import PriorityAnalysis
from app.models.duplicate import DuplicateGroup, ComplaintDuplicateLink
from app.ai.verification.verification_service import ComplaintVerificationService
from app.ai.severity.severity_service import SeverityAssessmentService
from app.ai.duplicate.duplicate_service import DuplicateDetectionService
from app.ai.priority.priority_service import PriorityService
from app.ai.department.department_service import DepartmentRecommendationService

logger = logging.getLogger(__name__)


class ComplaintProcessingService:
    """Master orchestrator executing the full civic complaint AI pipeline.

    Coordinates:
    1. Image Validation & Vision Inference & Phase 4 Verification
    2. Phase 5 Severity Assessment
    3. Phase 6 Duplicate Detection & Clustering
    4. Phase 7 Intelligent Priority Calculation
    5. Phase 8 Department Recommendation
    """

    def __init__(
        self,
        verification_service: Optional[ComplaintVerificationService] = None,
        severity_service: Optional[SeverityAssessmentService] = None,
        duplicate_service: Optional[DuplicateDetectionService] = None,
        priority_service_instance: Optional[PriorityService] = None,
        department_service: Optional[DepartmentRecommendationService] = None,
    ):
        self.verification_service = verification_service or ComplaintVerificationService()
        self.severity_service = severity_service or SeverityAssessmentService()
        self.duplicate_service = duplicate_service or DuplicateDetectionService()
        self.priority_service = priority_service_instance or PriorityService()
        self.department_service = department_service or DepartmentRecommendationService()

    def process_complaint(
        self,
        complaint_id: uuid.UUID,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Execute the full AI processing workflow for a complaint."""
        should_close_db = False
        if db is None:
            db = SessionLocal()
            should_close_db = True

        try:
            return self._execute_pipeline(complaint_id, db)
        finally:
            if should_close_db:
                db.close()

    def _execute_pipeline(self, complaint_id: uuid.UUID, db: Session) -> Dict[str, Any]:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            logger.error(f"Cannot process complaint: {complaint_id} not found.")
            return {"status": "error", "message": f"Complaint {complaint_id} not found."}

        # Step 0: Initialize processing
        complaint.processing_state = ProcessingState.PROCESSING
        complaint.processing_progress = 10
        complaint.processing_message = "Starting AI vision inspection and verification..."
        complaint.status = ComplaintStatus.AI_PROCESSING
        db.commit()

        try:
            # -------------------------------------------------------------
            # STEP 1: Computer Vision & Complaint Verification (Phase 4)
            # -------------------------------------------------------------
            cat_str = complaint.category.value if hasattr(complaint.category, "value") else str(complaint.category)
            v_result = self.verification_service.verify_complaint(
                image_input=complaint.image_path,
                description=complaint.description,
                selected_category=cat_str,
                latitude=complaint.latitude,
                longitude=complaint.longitude,
            )

            # Persist AI Analysis
            ai_record = db.query(AIAnalysis).filter(AIAnalysis.complaint_id == complaint.id).first()
            if not ai_record:
                ai_record = AIAnalysis(complaint_id=complaint.id)
                db.add(ai_record)

            primary_det = v_result["detections"][0] if v_result.get("detections") else {}
            ai_record.detected_class = v_result.get("detected_category")
            ai_record.confidence = v_result.get("detection_confidence", 0.0)
            ai_record.bounding_box = {"bbox": primary_det.get("bbox", [])} if primary_det else {}
            ai_record.image_width = v_result.get("image_quality", {}).get("metrics", {}).get("width")
            ai_record.image_height = v_result.get("image_quality", {}).get("metrics", {}).get("height")
            ai_record.is_civic_issue = v_result.get("relevance", {}).get("is_relevant", False)
            ai_record.detection_status = "COMPLETED"
            ai_record.verification_score = v_result.get("verification_score", 0.0)
            ai_record.verification_status = v_result.get("verification_status", "NEEDS_REVIEW")
            ai_record.image_quality_score = float(v_result.get("image_quality", {}).get("score", 0))
            ai_record.text_consistency_score = float(v_result.get("consistency", {}).get("score", 0))
            ai_record.explanation = v_result.get("explanation", [])
            ai_record.audit_metadata = v_result.get("audit_trail", {})
            ai_record.model_version = v_result.get("audit_trail", {}).get("model_version", "civic_yolo_v1")
            ai_record.config_version = v_result.get("audit_trail", {}).get("config_version", "v1.0.0")

            # Update lifecycle status from verification outcome
            v_status = v_result.get("verification_status", "NEEDS_REVIEW")
            if v_status == "VERIFIED":
                complaint.status = ComplaintStatus.VERIFIED
            elif v_status == "NEEDS_REVIEW":
                complaint.status = ComplaintStatus.NEEDS_REVIEW
            elif v_status == "REJECTED":
                complaint.status = ComplaintStatus.REJECTED

            complaint.processing_state = ProcessingState.VERIFICATION_COMPLETE
            complaint.processing_progress = 30
            complaint.processing_message = f"Complaint verification outcome: {v_status}."
            db.commit()

            # If rejected by verification, stop further processing safely
            if v_status == "REJECTED":
                complaint.processing_state = ProcessingState.COMPLETE
                complaint.processing_progress = 100
                complaint.processing_message = "Verification failed: issue rejected as non-civic or invalid."
                db.commit()
                return {
                    "complaint_id": str(complaint.id),
                    "status": complaint.status,
                    "processing_state": complaint.processing_state,
                    "verification": v_result,
                }

            # -------------------------------------------------------------
            # STEP 2: Severity Assessment & Damage Impact (Phase 5)
            # -------------------------------------------------------------
            detections = []
            if ai_record.detected_class:
                bbox = ai_record.bounding_box.get("bbox", []) if isinstance(ai_record.bounding_box, dict) else []
                detections.append({
                    "class_name": ai_record.detected_class,
                    "confidence": ai_record.confidence or 0.85,
                    "bbox": bbox,
                })
            else:
                detections.append({
                    "class_name": cat_str,
                    "confidence": 0.85,
                    "bbox": [100, 100, 300, 300],
                })

            sev_result = self.severity_service.assess(
                detections=detections,
                image_metadata={"width": ai_record.image_width or 640, "height": ai_record.image_height or 480},
                description=complaint.description,
                location={"latitude": complaint.latitude, "longitude": complaint.longitude} if complaint.latitude else None,
            )

            sev_record = db.query(SeverityAnalysis).filter(SeverityAnalysis.complaint_id == complaint.id).first()
            if not sev_record:
                sev_record = SeverityAnalysis(complaint_id=complaint.id)
                db.add(sev_record)

            sev_record.severity_score = sev_result["severity_score"]
            sev_record.severity_level = sev_result["severity_level"]
            sev_record.safety_risk_score = sev_result["safety_risk_score"]
            sev_record.infrastructure_impact_score = sev_result["infrastructure_impact_score"]
            sev_record.public_impact_score = sev_result["public_impact_score"]
            sev_record.severity_factors = {"factors": sev_result["factors"]}
            sev_record.detection_analysis = sev_result["detection_analysis"]
            sev_record.evidence = sev_result["evidence"]
            sev_record.explanation = "\n".join(sev_result["explanation"])
            sev_record.model_version = sev_result["model_version"]
            sev_record.configuration_version = sev_result["severity_config_version"]

            complaint.processing_state = ProcessingState.SEVERITY_COMPLETE
            complaint.processing_progress = 50
            complaint.processing_message = f"Severity assessed: {sev_result['severity_level']} ({sev_result['severity_score']:.1f}/100)."
            db.commit()

            # -------------------------------------------------------------
            # STEP 3: Duplicate Complaint Detection (Phase 6)
            # -------------------------------------------------------------
            dup_result = self.duplicate_service.detect_duplicates(
                complaint_id=complaint.id,
                db=db,
                force_recompute=True,
            )

            complaint.processing_state = ProcessingState.DUPLICATE_CHECK_COMPLETE
            complaint.processing_progress = 70
            complaint.processing_message = f"Duplicate check complete (Decision: {dup_result.get('decision', 'NEW')})."
            db.commit()

            # -------------------------------------------------------------
            # STEP 4: Intelligent Priority Engine (Phase 7)
            # -------------------------------------------------------------
            priority_record = self.priority_service.evaluate_complaint_priority(
                complaint_id=complaint.id,
                db=db,
                reason="PIPELINE_ORCHESTRATION",
            )

            complaint.processing_state = ProcessingState.PRIORITY_COMPLETE
            complaint.processing_progress = 85
            complaint.processing_message = f"Priority calculated: {priority_record.priority_level} ({priority_record.priority_score:.1f}/100)."
            db.commit()

            # -------------------------------------------------------------
            # STEP 5: Department Recommendation (Phase 8)
            # -------------------------------------------------------------
            dept_rec = self.department_service.recommend(
                category=ai_record.detected_class or cat_str,
                description=complaint.description,
                location={"latitude": complaint.latitude, "longitude": complaint.longitude} if complaint.latitude else None,
                detections=detections,
                detection_confidence=ai_record.confidence or 0.85,
                verification_status=ai_record.verification_status,
                db=db,
            )

            complaint.department_recommendation = dept_rec
            complaint.processing_state = ProcessingState.DEPARTMENT_RECOMMENDED
            complaint.processing_progress = 95
            complaint.processing_message = f"Department recommended: {dept_rec['department_name']}."
            db.commit()

            # -------------------------------------------------------------
            # STEP 6: Complete
            # -------------------------------------------------------------
            complaint.processing_state = ProcessingState.COMPLETE
            complaint.processing_progress = 100
            complaint.processing_message = "All AI analysis and department routing complete."
            db.commit()
            db.refresh(complaint)

            return {
                "complaint_id": str(complaint.id),
                "status": complaint.status,
                "processing_state": complaint.processing_state,
                "verification": v_result,
                "severity": sev_result,
                "duplicate": dup_result,
                "priority": {
                    "priority_score": priority_record.priority_score,
                    "priority_level": priority_record.priority_level,
                    "explanation": priority_record.explanation,
                },
                "department": dept_rec,
            }

        except Exception as e:
            logger.exception(f"Error during AI pipeline execution for complaint {complaint_id}: {e}")
            complaint.processing_state = ProcessingState.FAILED
            complaint.processing_error = str(e)
            complaint.processing_message = f"AI processing error: {str(e)}"
            db.commit()
            return {
                "complaint_id": str(complaint.id),
                "status": complaint.status,
                "processing_state": ProcessingState.FAILED,
                "error": str(e),
            }


complaint_processing_service = ComplaintProcessingService()
