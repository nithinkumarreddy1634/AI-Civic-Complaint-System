"""
Complaint service — handles complaint CRUD, lifecycle management, and response serialization.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.schemas.complaint import ComplaintCreate
from app.models.complaint import Complaint, ComplaintStatus, ProcessingState
from app.models.status_history import ComplaintStatusHistory
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from app.models.priority import PriorityAnalysis
from app.models.department import ComplaintAssignment, Department
from app.models.duplicate import DuplicateGroup, ComplaintDuplicateLink
from app.core.exceptions import NotFoundException
import uuid
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime


def create_complaint(
    db: Session,
    user_id: uuid.UUID,
    complaint_data: ComplaintCreate,
    image_path: str,
    image_original_name: str,
) -> Complaint:
    """
    Create a new complaint with initial status AI_PROCESSING and PENDING state.
    """
    cat_val = complaint_data.category.value if hasattr(complaint_data.category, "value") else str(complaint_data.category)
    new_complaint = Complaint(
        user_id=user_id,
        category=cat_val,
        description=complaint_data.description,
        latitude=complaint_data.latitude,
        longitude=complaint_data.longitude,
        address=complaint_data.address,
        image_path=image_path,
        image_original_name=image_original_name,
        status=ComplaintStatus.AI_PROCESSING,
        processing_state=ProcessingState.PENDING,
        processing_progress=0,
        processing_message="Complaint submitted. Enqueued for AI processing.",
    )
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    return new_complaint


def get_complaint(db: Session, complaint_id: uuid.UUID) -> Optional[Complaint]:
    """Fetch a single complaint by its UUID."""
    return db.query(Complaint).filter(Complaint.id == complaint_id).first()


def build_complaint_dict(complaint: Complaint, db: Session, is_admin: bool = False) -> Dict[str, Any]:
    """Assemble complete unified complaint dictionary containing all phase artifacts."""
    ai = db.query(AIAnalysis).filter(AIAnalysis.complaint_id == complaint.id).first()
    sev = db.query(SeverityAnalysis).filter(SeverityAnalysis.complaint_id == complaint.id).first()
    prio = db.query(PriorityAnalysis).filter(PriorityAnalysis.complaint_id == complaint.id).first()
    dup_link = db.query(ComplaintDuplicateLink).filter(ComplaintDuplicateLink.complaint_id == complaint.id).first()

    dup_group = None
    if dup_link:
        dup_group = db.query(DuplicateGroup).filter(DuplicateGroup.id == dup_link.group_id).first()
    else:
        dup_group = db.query(DuplicateGroup).filter(DuplicateGroup.representative_complaint_id == complaint.id).first()

    data: Dict[str, Any] = {
        "id": complaint.id,
        "user_id": complaint.user_id,
        "category": complaint.category,
        "description": complaint.description,
        "status": complaint.status,
        "image_path": complaint.image_path,
        "image_original_name": complaint.image_original_name,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "address": complaint.address,
        "is_duplicate": complaint.is_duplicate or (dup_link is not None),
        "duplicate_of": complaint.duplicate_of,
        "processing_state": complaint.processing_state,
        "processing_progress": complaint.processing_progress,
        "processing_message": complaint.processing_message,
        "created_at": complaint.created_at,
        "updated_at": complaint.updated_at,
        "priority_level": prio.priority_level if prio else None,
        "verification": None,
        "severity": None,
        "duplicates": None,
        "priority": None,
        "department": complaint.department_recommendation,
    }

    if ai:
        data["verification"] = {
            "status": ai.verification_status,
            "score": ai.verification_score,
            "confidence": ai.confidence,
            "detected_class": ai.detected_class,
            "image_quality_score": ai.image_quality_score,
            "text_consistency_score": ai.text_consistency_score,
            "explanation": ai.explanation,
            "bounding_box": ai.bounding_box,
            "image_width": ai.image_width,
            "image_height": ai.image_height,
        }

    if sev:
        data["severity"] = {
            "score": sev.severity_score,
            "level": sev.severity_level,
            "safety_risk_score": sev.safety_risk_score,
            "infrastructure_impact_score": sev.infrastructure_impact_score,
            "public_impact_score": sev.public_impact_score,
            "evidence": sev.evidence,
        }

    if dup_group or dup_link:
        data["duplicates"] = {
            "group_id": str(dup_group.id) if dup_group else None,
            "report_count": dup_group.report_count if dup_group else 1,
            "similarity_score": dup_link.similarity_score if dup_link else None,
        }

    if prio:
        data["priority"] = {
            "score": prio.priority_score,
            "level": prio.priority_level,
            "base_score": prio.base_score,
            "escalation_boost": prio.escalation_boost,
            "explanation": prio.explanation,
            "contributing_factors": prio.contributing_factors,
        }

    if is_admin:
        assignments = (
            db.query(ComplaintAssignment, Department)
            .join(Department, Department.id == ComplaintAssignment.department_id)
            .filter(ComplaintAssignment.complaint_id == complaint.id)
            .all()
        )
        data["assignments"] = [
            {
                "id": str(asg.id),
                "department_id": str(asg.department_id),
                "department_name": dept.name,
                "assigned_by": str(asg.assigned_by),
                "notes": asg.notes,
                "status": asg.status,
                "assigned_at": asg.assigned_at,
            }
            for asg, dept in assignments
        ]

        history = (
            db.query(ComplaintStatusHistory)
            .filter(ComplaintStatusHistory.complaint_id == complaint.id)
            .order_by(ComplaintStatusHistory.changed_at.desc())
            .all()
        )
        data["status_history"] = [
            {
                "id": str(h.id),
                "old_status": h.old_status,
                "new_status": h.new_status,
                "changed_by": str(h.changed_by),
                "remarks": h.remarks,
                "changed_at": h.changed_at,
            }
            for h in history
        ]

    return data


def get_user_complaints(
    db: Session,
    user_id: uuid.UUID,
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> list[Complaint]:
    """List complaints submitted by a specific citizen with optional filters."""
    query = db.query(Complaint).filter(Complaint.user_id == user_id)
    if status:
        query = query.filter(Complaint.status == status)
    if category:
        query = query.filter(Complaint.category == category)
    query = query.order_by(Complaint.created_at.desc())
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit).all()


def get_admin_complaints(
    db: Session,
    status: Optional[str] = None,
    priority_level: Optional[str] = None,
    category: Optional[str] = None,
    department: Optional[str] = None,
    severity_level: Optional[str] = None,
    verification_status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    sort_by: str = "created_desc",
    page: int = 1,
    limit: int = 20,
) -> Tuple[List[Dict[str, Any]], int]:
    """Admin query with multi-criteria filtering, multi-model sorting, and pagination."""
    query = (
        db.query(
            Complaint,
            PriorityAnalysis,
            SeverityAnalysis,
            AIAnalysis,
        )
        .outerjoin(PriorityAnalysis, PriorityAnalysis.complaint_id == Complaint.id)
        .outerjoin(SeverityAnalysis, SeverityAnalysis.complaint_id == Complaint.id)
        .outerjoin(AIAnalysis, AIAnalysis.complaint_id == Complaint.id)
    )

    if status:
        query = query.filter(Complaint.status == status)
    if category:
        query = query.filter(Complaint.category == category)
    if priority_level:
        query = query.filter(PriorityAnalysis.priority_level == priority_level.upper())
    if severity_level:
        query = query.filter(SeverityAnalysis.severity_level == severity_level.upper())
    if verification_status:
        query = query.filter(AIAnalysis.verification_status == verification_status.upper())
    if date_from:
        query = query.filter(Complaint.created_at >= date_from)
    if date_to:
        query = query.filter(Complaint.created_at <= date_to)

    total = query.count()

    # Sorting
    if sort_by == "priority_desc":
        query = query.order_by(desc(PriorityAnalysis.priority_score))
    elif sort_by == "priority_asc":
        query = query.order_by(asc(PriorityAnalysis.priority_score))
    elif sort_by == "severity_desc":
        query = query.order_by(desc(SeverityAnalysis.severity_score))
    elif sort_by == "created_asc":
        query = query.order_by(asc(Complaint.created_at))
    else:  # created_desc
        query = query.order_by(desc(Complaint.created_at))

    offset = (page - 1) * limit
    rows = query.offset(offset).limit(limit).all()

    results = []
    for c, _p, _s, _ai in rows:
        results.append(build_complaint_dict(c, db, is_admin=True))

    return results, total
