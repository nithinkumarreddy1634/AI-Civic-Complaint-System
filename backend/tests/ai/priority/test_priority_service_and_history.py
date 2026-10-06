"""Integration tests for PriorityService and PriorityHistory audit tracking."""
import uuid
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from app.models.duplicate import DuplicateGroup, ComplaintDuplicateLink
from app.models.priority import PriorityAnalysis, PriorityHistory
from app.ai.priority.priority_service import priority_service


def create_verified_complaint_with_severity(
    db: Session,
    user: User,
    severity_score: float = 75.0,
    safety_risk: float = 70.0,
    infra_impact: float = 65.0,
    pub_impact: float = 60.0,
    verification_score: float = 88.0,
    verification_status: str = "VERIFIED",
    lat: float = 12.9716,
    lon: float = 77.5946,
) -> Complaint:
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=user.id,
        category="pothole",
        description="Hazardous pothole on roadway",
        image_path="/tmp/test.jpg",
        image_original_name="test.jpg",
        latitude=lat,
        longitude=lon,
        status=ComplaintStatus.VERIFIED if verification_status == "VERIFIED" else ComplaintStatus.REJECTED,
    )
    db.add(complaint)
    db.commit()

    ai_analysis = AIAnalysis(
        complaint_id=complaint.id,
        detected_class="pothole",
        confidence=0.88,
        is_civic_issue=True,
        detection_status="COMPLETED",
        verification_score=verification_score,
        verification_status=verification_status,
    )
    db.add(ai_analysis)

    severity_analysis = SeverityAnalysis(
        complaint_id=complaint.id,
        severity_score=severity_score,
        severity_level="HIGH" if severity_score >= 70 else "MEDIUM",
        safety_risk_score=safety_risk,
        infrastructure_impact_score=infra_impact,
        public_impact_score=pub_impact,
        explanation="Assessment completed",
    )
    db.add(severity_analysis)
    db.commit()
    db.refresh(complaint)
    return complaint


def test_evaluate_priority_initial_analysis(db: Session, test_user: User):
    complaint = create_verified_complaint_with_severity(db, test_user)

    analysis = priority_service.evaluate_complaint_priority(
        complaint_id=complaint.id,
        db=db,
        reason="INITIAL_ANALYSIS",
    )

    assert analysis is not None
    assert analysis.priority_score > 0.0
    assert analysis.priority_level in ["LOW", "MEDIUM", "HIGH", "URGENT"]
    assert "severity" in analysis.contributing_factors

    # Verify history entry created
    history = db.query(PriorityHistory).filter(PriorityHistory.complaint_id == complaint.id).all()
    assert len(history) == 1
    assert history[0].reason == "INITIAL_ANALYSIS"
    assert history[0].priority_score == analysis.priority_score


def test_rejected_complaint_raises_error(db: Session, test_user: User):
    complaint = create_verified_complaint_with_severity(
        db, test_user, verification_status="REJECTED"
    )

    with pytest.raises(ValueError, match="verification status is REJECTED"):
        priority_service.evaluate_complaint_priority(complaint.id, db)


def test_missing_phase4_or_phase5_raises_error(db: Session, test_user: User):
    # Complaint with no AI analysis
    bare_complaint = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Pothole with no AI run yet",
        image_path="/tmp/bare.jpg",
        image_original_name="bare.jpg",
    )
    db.add(bare_complaint)
    db.commit()

    with pytest.raises(ValueError, match="Phase 4 verification"):
        priority_service.evaluate_complaint_priority(bare_complaint.id, db)


def test_duplicate_cluster_recalculation(db: Session, test_user: User):
    complaint = create_verified_complaint_with_severity(db, test_user)

    # Initial priority
    pa1 = priority_service.evaluate_complaint_priority(complaint.id, db)
    initial_score = pa1.priority_score

    # Now simulate duplicate reports clustering (e.g. 5 reports)
    group = DuplicateGroup(
        id=uuid.uuid4(),
        representative_complaint_id=complaint.id,
        report_count=5,
    )
    db.add(group)
    link = ComplaintDuplicateLink(
        id=uuid.uuid4(),
        group_id=group.id,
        complaint_id=complaint.id,
        similarity_score=88.5,
    )
    db.add(link)
    db.commit()

    # Recalculate for cluster
    updated_list = priority_service.recalculate_cluster_priorities(group.id, db)
    assert len(updated_list) >= 1

    pa2 = db.query(PriorityAnalysis).filter(PriorityAnalysis.complaint_id == complaint.id).first()
    # Priority should increase because report_count increased from 1 to 5
    assert pa2.priority_score > initial_score

    # Audit history must have 2 entries
    history = (
        db.query(PriorityHistory)
        .filter(PriorityHistory.complaint_id == complaint.id)
        .order_by(PriorityHistory.created_at.asc())
        .all()
    )
    assert len(history) == 2
    assert history[0].reason == "INITIAL_ANALYSIS"
    assert history[1].reason == "DUPLICATE_REPORT_ADDED"
