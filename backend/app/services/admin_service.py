"""
Admin service — handles dashboard stats, analytics, hotspots, and complaint assignment.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.complaint import Complaint, ComplaintStatus
from app.models.department import ComplaintAssignment, Department
from app.models.status_history import ComplaintStatusHistory
from app.models.priority import PriorityAnalysis
from app.schemas.dashboard import DashboardStats, AnalyticsData, HotspotData
from app.core.exceptions import NotFoundException, BadRequestException
import uuid
from typing import Optional
from datetime import datetime, timezone


def get_dashboard_stats(db: Session) -> DashboardStats:
    """Get aggregate dashboard statistics across complaints, priorities, and statuses."""
    total = db.query(func.count(Complaint.id)).scalar() or 0
    verified = db.query(func.count(Complaint.id)).filter(Complaint.status == ComplaintStatus.VERIFIED).scalar() or 0
    pending = db.query(func.count(Complaint.id)).filter(Complaint.status.in_([ComplaintStatus.SUBMITTED, ComplaintStatus.AI_PROCESSING])).scalar() or 0
    rejected = db.query(func.count(Complaint.id)).filter(Complaint.status == ComplaintStatus.REJECTED).scalar() or 0
    resolved = db.query(func.count(Complaint.id)).filter(Complaint.status == ComplaintStatus.RESOLVED).scalar() or 0

    high_priority = db.query(func.count(PriorityAnalysis.id)).filter(PriorityAnalysis.priority_level == "HIGH").scalar() or 0
    urgent = db.query(func.count(PriorityAnalysis.id)).filter(PriorityAnalysis.priority_level == "URGENT").scalar() or 0

    # Counts by status
    status_counts = db.query(Complaint.status, func.count(Complaint.id)).group_by(Complaint.status).all()
    by_status = {s: c for s, c in status_counts}

    # Counts by category
    cat_counts = db.query(Complaint.category, func.count(Complaint.id)).group_by(Complaint.category).all()
    by_category = {cat: c for cat, c in cat_counts}

    return DashboardStats(
        total_complaints=total,
        verified=verified,
        pending=pending,
        rejected=rejected,
        high_priority=high_priority,
        urgent=urgent,
        resolved=resolved,
        by_category=by_category,
        by_department={},
        by_status=by_status,
        recent_complaints=[],
    )


def get_analytics(db: Session) -> AnalyticsData:
    """Get analytics metrics for charts and administrative reporting."""
    cat_counts = db.query(Complaint.category, func.count(Complaint.id)).group_by(Complaint.category).all()
    by_category = {cat: c for cat, c in cat_counts}

    total = db.query(func.count(Complaint.id)).scalar() or 0
    resolved = db.query(func.count(Complaint.id)).filter(Complaint.status.in_([ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED])).scalar() or 0
    resolution_rate = round((resolved / total * 100.0), 1) if total > 0 else 0.0

    return AnalyticsData(
        complaints_over_time=[],
        category_distribution=by_category,
        resolution_rate=resolution_rate,
    )


def get_hotspots(db: Session) -> list[HotspotData]:
    """Get geographic complaint coordinates for density map visualization."""
    coords = (
        db.query(Complaint.latitude, Complaint.longitude, Complaint.category)
        .filter(Complaint.latitude.isnot(None), Complaint.longitude.isnot(None))
        .limit(200)
        .all()
    )
    return [
        HotspotData(
            latitude=lat,
            longitude=lon,
            complaint_count=1,
            top_category=cat,
        )
        for lat, lon, cat in coords
    ]


def assign_complaint(
    db: Session,
    complaint_id: uuid.UUID,
    department_id: uuid.UUID,
    assigned_by: uuid.UUID,
    notes: Optional[str] = None,
) -> ComplaintAssignment:
    """Assign a complaint to a department, set status to ASSIGNED, and log status history."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException(detail=f"Complaint {complaint_id} not found")

    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise NotFoundException(detail=f"Department {department_id} not found")

    old_status = complaint.status

    assignment = ComplaintAssignment(
        complaint_id=complaint_id,
        department_id=department_id,
        assigned_by=assigned_by,
        notes=notes,
        status="ACTIVE",
    )
    db.add(assignment)

    complaint.status = ComplaintStatus.ASSIGNED
    complaint.updated_at = datetime.now(timezone.utc)

    # Record status history
    history = ComplaintStatusHistory(
        complaint_id=complaint_id,
        old_status=old_status,
        new_status=ComplaintStatus.ASSIGNED,
        changed_by=assigned_by,
        remarks=f"Assigned to {dept.name}. Notes: {notes or 'None'}",
        changed_at=datetime.now(timezone.utc),
    )
    db.add(history)

    db.commit()
    db.refresh(assignment)
    return assignment
