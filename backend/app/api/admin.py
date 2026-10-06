"""
Admin management API routes.

Endpoints:
    GET  /api/admin/dashboard                   — Dashboard metrics
    GET  /api/admin/complaints                  — All complaints (filterable, sortable)
    GET  /api/admin/complaints/{id}             — Detailed complaint view with full AI audit
    PUT  /api/admin/complaints/{id}/assign      — Assign department
    PUT  /api/admin/complaints/{id}/status      — Update complaint status with transition validation
    GET  /api/admin/analytics                   — Analytics data
    GET  /api/admin/hotspots                    — Geographic hotspot data
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from app.api.deps import get_current_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.complaint import ComplaintResponse
from app.schemas.department import AssignmentCreate, AssignmentResponse
from app.schemas.dashboard import DashboardStats, AnalyticsData, HotspotData
from app.services import admin_service, complaint_service
from app.services.status_service import status_service
import uuid

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get dashboard metrics: complaint counts by status, category, department."""
    return admin_service.get_dashboard_stats(db)


@router.get("/complaints")
def get_all_complaints(
    status: Optional[str] = Query(None, description="Filter by complaint lifecycle status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority_level: Optional[str] = Query(None, description="Filter by priority tier (LOW, MEDIUM, HIGH, URGENT)"),
    department: Optional[str] = Query(None, description="Filter by recommended department"),
    severity_level: Optional[str] = Query(None, description="Filter by severity level (LOW, MEDIUM, HIGH, CRITICAL)"),
    verification_status: Optional[str] = Query(None, description="Filter by verification outcome (VERIFIED, NEEDS_REVIEW, REJECTED)"),
    date_from: Optional[datetime] = Query(None, description="Created from timestamp"),
    date_to: Optional[datetime] = Query(None, description="Created to timestamp"),
    sort_by: str = Query("created_desc", description="Sorting: priority_desc, priority_asc, severity_desc, created_desc, created_asc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """List all complaints with multi-criteria filtering, sorting, and pagination."""
    complaints, total = complaint_service.get_admin_complaints(
        db=db,
        status=status,
        priority_level=priority_level,
        category=category,
        department=department,
        severity_level=severity_level,
        verification_status=verification_status,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        page=page,
        limit=limit,
    )
    return {
        "items": complaints,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/complaints/{complaint_id}")
def get_complaint_detail(
    complaint_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get full complaint detail with complete AI analysis, assignments, and status history."""
    complaint = complaint_service.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint_service.build_complaint_dict(complaint, db, is_admin=True)


@router.put("/complaints/{complaint_id}/assign")
def assign_complaint(
    complaint_id: uuid.UUID,
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Assign a complaint to a department and update status to ASSIGNED."""
    return admin_service.assign_complaint(
        db, complaint_id, assignment_data.department_id, admin.id, assignment_data.notes
    )


@router.put("/complaints/{complaint_id}/status")
def update_status(
    complaint_id: uuid.UUID,
    new_status: str = Query(..., description="New status value"),
    remarks: Optional[str] = Query(None, description="Optional transition remarks"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update a complaint's status with state transition validation and audit logging."""
    return status_service.update_status(
        complaint_id=complaint_id,
        new_status=new_status,
        changed_by=admin.id,
        db=db,
        remarks=remarks,
    )


@router.get("/analytics", response_model=AnalyticsData)
def get_analytics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get analytics data for charts and reports."""
    return admin_service.get_analytics(db)


@router.get("/hotspots", response_model=list[HotspotData])
def get_hotspots(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Get geographic complaint hotspots for map visualization."""
    return admin_service.get_hotspots(db)
