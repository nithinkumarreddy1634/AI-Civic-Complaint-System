"""
Unit tests for PriorityService (Section 9).

Covers:
- Range invariant: 0 <= priority_score <= 100
- Urgency tiers: LOW, MEDIUM, HIGH, URGENT boundary consistency
- Risk factor contribution monotonicity (higher severity / safety / impact yields higher or equal priority)
- Arterial road and school zone boosts
"""
import pytest
import uuid
from sqlalchemy.orm import Session
from app.ai.priority.priority_service import PriorityService
from app.models.complaint import Complaint, ComplaintStatus
from app.models.severity import SeverityAnalysis
from app.models.ai_analysis import AIAnalysis
from app.models.user import User


@pytest.fixture
def priority_service():
    return PriorityService()


def test_priority_score_range_and_levels(db: Session, test_user: User, priority_service):
    """Test priority score always stays strictly within [0, 100]."""
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Hazardous pothole",
        image_path="/fake/p.jpg",
        image_original_name="p.jpg",
        latitude=12.97,
        longitude=77.59,
        status=ComplaintStatus.VERIFIED,
    )
    ai_record = AIAnalysis(
        complaint_id=complaint.id,
        detected_class="pothole",
        confidence=0.9,
        verification_status="VERIFIED",
        is_civic_issue=True,
    )
    sev_record = SeverityAnalysis(
        complaint_id=complaint.id,
        severity_score=60.0,
        severity_level="MEDIUM",
        safety_risk_score=50.0,
        infrastructure_impact_score=60.0,
        public_impact_score=55.0,
        explanation="Medium severity defect",
    )
    db.add_all([complaint, ai_record, sev_record])
    db.commit()

    analysis = priority_service.evaluate_complaint_priority(
        complaint_id=complaint.id,
        db=db,
    )

    assert 0.0 <= analysis.priority_score <= 100.0
    assert analysis.priority_level in ("LOW", "MEDIUM", "HIGH", "URGENT")
    assert analysis.explanation != ""
    assert "_metadata" in analysis.contributing_factors or len(analysis.contributing_factors) > 0


def test_safety_risk_factor_scaling(db: Session, test_user: User, priority_service):
    """Higher safety risk in severity analysis should result in higher or equal priority score."""
    # Complaint 1: Low safety risk
    c_low = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Small defect",
        image_path="/fake/p1.jpg",
        image_original_name="p1.jpg",
        latitude=12.97,
        longitude=77.59,
        status=ComplaintStatus.VERIFIED,
    )
    sev_low = SeverityAnalysis(
        complaint_id=c_low.id,
        severity_score=20.0,
        severity_level="LOW",
        safety_risk_score=15.0,
        infrastructure_impact_score=20.0,
        public_impact_score=20.0,
        explanation="Low severity",
    )
    ai_low = AIAnalysis(
        complaint_id=c_low.id,
        detected_class="pothole",
        confidence=0.85,
        verification_status="VERIFIED",
        is_civic_issue=True,
    )
    db.add_all([c_low, sev_low, ai_low])

    # Complaint 2: High safety risk
    c_high = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Dangerous deep defect",
        image_path="/fake/p2.jpg",
        image_original_name="p2.jpg",
        latitude=12.97,
        longitude=77.59,
        status=ComplaintStatus.VERIFIED,
    )
    sev_high = SeverityAnalysis(
        complaint_id=c_high.id,
        severity_score=85.0,
        severity_level="CRITICAL",
        safety_risk_score=90.0,
        infrastructure_impact_score=85.0,
        public_impact_score=80.0,
        explanation="High severity",
    )
    ai_high = AIAnalysis(
        complaint_id=c_high.id,
        detected_class="pothole",
        confidence=0.95,
        verification_status="VERIFIED",
        is_civic_issue=True,
    )
    db.add_all([c_high, sev_high, ai_high])
    db.commit()

    p_low = priority_service.evaluate_complaint_priority(c_low.id, db=db)
    p_high = priority_service.evaluate_complaint_priority(c_high.id, db=db)

    assert p_high.priority_score > p_low.priority_score


def test_zone_boosts(db: Session, test_user: User, priority_service):
    """Complaints in arterial roads or school zones should receive priority boost."""
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="damaged_road",
        description="Cracked road surface",
        image_path="/fake/road.jpg",
        image_original_name="road.jpg",
        latitude=12.97,
        longitude=77.59,
        status=ComplaintStatus.VERIFIED,
    )
    ai_rec = AIAnalysis(
        complaint_id=complaint.id,
        detected_class="damaged_road",
        confidence=0.9,
        verification_status="VERIFIED",
        is_civic_issue=True,
    )
    sev_rec = SeverityAnalysis(
        complaint_id=complaint.id,
        severity_score=50.0,
        severity_level="MEDIUM",
        safety_risk_score=45.0,
        infrastructure_impact_score=50.0,
        public_impact_score=50.0,
        explanation="Medium road damage",
    )
    db.add_all([complaint, ai_rec, sev_rec])
    db.commit()

    p_normal = priority_service.evaluate_complaint_priority(
        complaint_id=complaint.id,
        db=db,
        is_arterial_road=False,
        is_school_zone=False,
    )
    p_boosted = priority_service.evaluate_complaint_priority(
        complaint_id=complaint.id,
        db=db,
        is_arterial_road=True,
        is_school_zone=True,
    )

    assert p_boosted.priority_score >= p_normal.priority_score
