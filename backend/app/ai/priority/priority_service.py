"""Priority Orchestrator Service integrating Phase 4, Phase 5, and Phase 6 data."""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintStatus
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from app.models.duplicate import DuplicateGroup, ComplaintDuplicateLink
from app.models.priority import PriorityAnalysis, PriorityHistory
from app.ai.priority.config import PriorityConfig, priority_config
from app.ai.priority.frequency_scaling import frequency_scaler
from app.ai.priority.location_impact import location_impact_service
from app.ai.priority.priority_engine import priority_engine, PriorityEngineResult
from app.ai.priority.explainer import priority_explainer
from app.schemas.priority import PriorityResponse, PriorityLevel

logger = logging.getLogger(__name__)


class PriorityService:
    """Service to evaluate, re-evaluate, and track explainable civic complaint priority."""

    def __init__(self, config: PriorityConfig = None):
        self.config = config or priority_config
        self.engine = priority_engine
        self.scaler = frequency_scaler
        self.location_service = location_impact_service
        self.explainer = priority_explainer

    def evaluate_complaint_priority(
        self,
        complaint_id: uuid.UUID,
        db: Session,
        unresolved_days: Optional[float] = None,
        is_arterial_road: Optional[bool] = None,
        is_school_zone: Optional[bool] = None,
        is_hospital_zone: Optional[bool] = None,
        reason: str = "INITIAL_ANALYSIS",
    ) -> PriorityAnalysis:
        """Evaluate or recalculate priority for a single complaint using multi-phase AI inputs."""
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise ValueError(f"Complaint with ID {complaint_id} does not exist.")

        # Phase 4 Validation Check
        ai_analysis = db.query(AIAnalysis).filter(AIAnalysis.complaint_id == complaint_id).first()
        if not ai_analysis:
            raise ValueError(
                f"Complaint {complaint_id} has not completed Phase 4 verification analysis."
            )

        if ai_analysis.verification_status == "REJECTED":
            raise ValueError(
                f"Cannot prioritize complaint {complaint_id}: verification status is REJECTED."
            )

        # Phase 5 Severity Check
        severity_analysis = db.query(SeverityAnalysis).filter(SeverityAnalysis.complaint_id == complaint_id).first()
        if not severity_analysis:
            raise ValueError(
                f"Complaint {complaint_id} has not completed Phase 5 severity assessment."
            )

        # 1. Normalize Verification Confidence (0-100)
        # ai_analysis.verification_score is 0-100; if 0, check confidence
        v_score = ai_analysis.verification_score
        if v_score <= 1.0 and ai_analysis.confidence > 0.0:
            v_score = ai_analysis.confidence * 100.0

        # 2. Extract Phase 5 Scores (0-100)
        sev_score = severity_analysis.severity_score
        safety_score = severity_analysis.safety_risk_score
        infra_score = severity_analysis.infrastructure_impact_score
        pub_score = severity_analysis.public_impact_score

        # 3. Determine Duplicate Cluster Report Count (Phase 6)
        report_count = 1
        dup_link = db.query(ComplaintDuplicateLink).filter(ComplaintDuplicateLink.complaint_id == complaint_id).first()
        if dup_link:
            group = db.query(DuplicateGroup).filter(DuplicateGroup.id == dup_link.group_id).first()
            if group:
                report_count = max(1, group.report_count)
        else:
            # Check if this complaint is the representative complaint of a duplicate group
            group = db.query(DuplicateGroup).filter(DuplicateGroup.representative_complaint_id == complaint_id).first()
            if group:
                report_count = max(1, group.report_count)

        freq_score = self.scaler.scale(report_count)

        # 4. Assess Location Impact
        loc_assessment = self.location_service.assess_location(
            latitude=complaint.latitude,
            longitude=complaint.longitude,
            is_arterial_road=is_arterial_road,
            is_school_zone=is_school_zone,
            is_hospital_zone=is_hospital_zone,
        )
        loc_score = loc_assessment.score if loc_assessment.is_available else None

        # 5. Compute aging days if not explicitly passed
        if unresolved_days is None:
            now = datetime.now(timezone.utc)
            created_at = complaint.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            unresolved_days = max(0.0, (now - created_at).total_seconds() / 86400.0)

        # 6. Execute Mathematical Priority Engine
        engine_result: PriorityEngineResult = self.engine.calculate(
            severity_score=sev_score,
            safety_risk_score=safety_score,
            infrastructure_impact_score=infra_score,
            public_impact_score=pub_score,
            frequency_score=freq_score,
            verification_confidence_score=v_score,
            location_score=loc_score,
            unresolved_days=unresolved_days,
            raw_report_count=report_count,
        )

        # 7. Generate Explainable Narrative
        explanation = self.explainer.generate_explanation(engine_result)

        # 8. Persist Priority Analysis
        factors_dict = {
            k: v.to_dict() for k, v in engine_result.factor_breakdown.items()
        }
        # Add metadata on location and report count
        factors_dict["_metadata"] = {
            "report_count": report_count,
            "location_assessment": loc_assessment.metadata,
            "unresolved_days": round(unresolved_days, 2),
            "base_score": round(engine_result.base_score, 2),
            "escalation_boost": round(engine_result.escalation_boost, 2),
        }

        analysis = db.query(PriorityAnalysis).filter(PriorityAnalysis.complaint_id == complaint_id).first()
        now_dt = datetime.now(timezone.utc)

        if analysis:
            analysis.priority_score = engine_result.priority_score
            analysis.priority_level = engine_result.priority_level.value
            analysis.base_score = round(engine_result.base_score, 2)
            analysis.escalation_boost = round(engine_result.escalation_boost, 2)
            analysis.contributing_factors = factors_dict
            analysis.explanation = explanation
            analysis.updated_at = now_dt
        else:
            analysis = PriorityAnalysis(
                complaint_id=complaint_id,
                priority_score=engine_result.priority_score,
                priority_level=engine_result.priority_level.value,
                base_score=round(engine_result.base_score, 2),
                escalation_boost=round(engine_result.escalation_boost, 2),
                contributing_factors=factors_dict,
                explanation=explanation,
                algorithm_version=self.config.version,
                config_version=self.config.version,
                created_at=now_dt,
                updated_at=now_dt,
            )
            db.add(analysis)

        # 9. Record History Audit Trail
        history_entry = PriorityHistory(
            complaint_id=complaint_id,
            priority_score=engine_result.priority_score,
            priority_level=engine_result.priority_level.value,
            reason=reason,
            contributing_factors=factors_dict,
            explanation=explanation,
            created_at=now_dt,
        )
        db.add(history_entry)

        # Update complaint lifecycle status if currently VERIFIED
        if complaint.status == ComplaintStatus.VERIFIED:
            complaint.status = ComplaintStatus.PRIORITIZED

        db.commit()
        db.refresh(analysis)
        return analysis

    def recalculate_cluster_priorities(
        self,
        group_id: uuid.UUID,
        db: Session,
        reason: str = "DUPLICATE_REPORT_ADDED",
    ) -> List[PriorityAnalysis]:
        """Recalculate priorities for all complaints in a duplicate cluster upon frequency change."""
        links = db.query(ComplaintDuplicateLink).filter(ComplaintDuplicateLink.group_id == group_id).all()
        updated: List[PriorityAnalysis] = []
        for link in links:
            try:
                pa = self.evaluate_complaint_priority(link.complaint_id, db, reason=reason)
                updated.append(pa)
            except Exception as e:
                logger.warning(f"Could not recalculate priority for complaint {link.complaint_id}: {e}")

        # Also check representative complaint if not in links
        group = db.query(DuplicateGroup).filter(DuplicateGroup.id == group_id).first()
        if group and group.representative_complaint_id:
            rep_id = group.representative_complaint_id
            if not any(link.complaint_id == rep_id for link in links):
                try:
                    pa = self.evaluate_complaint_priority(rep_id, db, reason=reason)
                    updated.append(pa)
                except Exception as e:
                    logger.warning(f"Could not recalculate priority for rep complaint {rep_id}: {e}")

        return updated


priority_service = PriorityService()
