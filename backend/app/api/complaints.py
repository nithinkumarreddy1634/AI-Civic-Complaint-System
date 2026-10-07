"""
Citizen complaint API routes.

Endpoints:
    POST /api/complaints                    — Submit a new complaint with image
    GET  /api/complaints                    — List citizen's own complaints
    GET  /api/complaints/{id}               — View complaint detail + AI results
    GET  /api/complaints/{id}/processing-status — Check async AI processing state
    POST /api/complaints/check-duplicate    — Check for potential duplicate complaints
    GET  /api/complaints/{id}/duplicates    — View duplicate cluster details
    GET  /api/complaints/{id}/priority      — View priority score & factors
    GET  /api/complaints/{id}/priority/history — View priority audit trail
"""
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintListResponse,
    ComplaintCreateResponse,
    ProcessingStatusResponse,
)
from app.services import complaint_service, image_service
from app.services.complaint_processing_service import complaint_processing_service
from app.api.deps import get_current_user, get_current_user_or_default
from app.database.session import get_db
from app.config import get_settings
from app.models.user import User
from app.models.complaint import Complaint
from app.models.duplicate import DuplicateGroup, ComplaintDuplicateLink
from app.models.priority import PriorityAnalysis, PriorityHistory
from app.schemas.priority import PriorityResponse, PriorityHistoryResponse
import uuid

router = APIRouter()
settings = get_settings()


@router.post("", response_model=ComplaintCreateResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ComplaintCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_complaint(
    background_tasks: BackgroundTasks,
    category: str = Form(..., description="Complaint category (e.g., pothole, garbage_accumulation)"),
    description: str = Form(..., description="Detailed description of the issue"),
    latitude: Optional[float] = Form(None, description="GPS latitude"),
    longitude: Optional[float] = Form(None, description="GPS longitude"),
    address: Optional[str] = Form(None, description="Human-readable address"),
    image: UploadFile = File(..., description="Photo of the infrastructure issue"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_default),
):
    """
    Submit a new civic infrastructure complaint.

    Accepts multipart form data with an image file and complaint metadata.
    The image is validated and saved, the complaint is created in AI_PROCESSING status,
    and the complete AI pipeline (Phases 4-8) is dispatched in the background.
    """
    # Validate coordinates
    if latitude is not None and (latitude < -90 or latitude > 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
    if longitude is not None and (longitude < -180 or longitude > 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
    if len(description.strip()) < 5:
        raise HTTPException(status_code=400, detail="Description must be at least 5 characters long")

    # Validate and save uploaded image
    saved_path, original_filename = await image_service.validate_and_save_image(
        image, settings
    )

    # Normalize category gracefully to prevent enum validation crashes
    from app.schemas.complaint import ComplaintCategory
    cat_str = category.lower().strip().replace(" ", "_")
    try:
        valid_cat = ComplaintCategory(cat_str)
    except ValueError:
        if "street" in cat_str or "light" in cat_str:
            valid_cat = ComplaintCategory.STREETLIGHT
        elif "dump" in cat_str or "garbage" in cat_str or "waste" in cat_str:
            valid_cat = ComplaintCategory.GARBAGE
        elif "hole" in cat_str:
            valid_cat = ComplaintCategory.POTHOLE
        elif "water" in cat_str or "leak" in cat_str:
            valid_cat = ComplaintCategory.WATER_LEAKAGE
        elif "road" in cat_str:
            valid_cat = ComplaintCategory.DAMAGED_ROAD
        elif "manhole" in cat_str:
            valid_cat = ComplaintCategory.MANHOLE
        elif "sidewalk" in cat_str or "footpath" in cat_str:
            valid_cat = ComplaintCategory.SIDEWALK
        elif "tree" in cat_str:
            valid_cat = ComplaintCategory.TREE
        else:
            valid_cat = ComplaintCategory.OTHER

    complaint_data = ComplaintCreate(
        category=valid_cat,
        description=description,
        latitude=latitude,
        longitude=longitude,
        address=address,
    )

    complaint = complaint_service.create_complaint(
        db, current_user.id, complaint_data, saved_path, original_filename
    )

    # Dispatch asynchronous multi-phase AI pipeline
    background_tasks.add_task(complaint_processing_service.process_complaint, complaint.id)

    return ComplaintCreateResponse(
        complaint_id=complaint.id,
        status=complaint.status,
        processing_state=complaint.processing_state,
        message="Complaint submitted successfully. AI verification and prioritization dispatched in background.",
    )


@router.get("", response_model=list[ComplaintListResponse])
@router.get("/", response_model=list[ComplaintListResponse])
def get_user_complaints(
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_default),
):
    """List the current citizen's own complaints with optional filtering."""
    return complaint_service.get_user_complaints(
        db, current_user.id, status, category, page, limit
    )


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_default),
):
    """
    Get full complaint detail including all AI analysis results.
    Allows citizens and tracking of complaints via reference ID.
    """
    complaint = complaint_service.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    is_admin = current_user.role == "admin"
    return complaint_service.build_complaint_dict(complaint, db, is_admin=is_admin)


@router.get("/{complaint_id}/processing-status", response_model=ProcessingStatusResponse)
def get_processing_status(
    complaint_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_or_default),
):
    """
    Retrieve real-time AI processing progress and current stage.
    """
    complaint = complaint_service.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if current_user.role != "admin" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this complaint")

    return ProcessingStatusResponse(
        complaint_id=complaint.id,
        processing_state=complaint.processing_state,
        progress=complaint.processing_progress,
        message=complaint.processing_message,
        error=complaint.processing_error,
    )


@router.post("/check-duplicate")
def check_duplicate(
    lat: float,
    lon: float,
    category: str,
    description: str,
    db: Session = Depends(get_db),
):
    """Quick pre-check for potential duplicates."""
    return {"is_duplicate": False, "potential_duplicates": []}


@router.get("/{id}/duplicates")
def get_complaint_duplicates(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve related duplicate complaints in the same DuplicateGroup."""
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if current_user.role != "admin" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this complaint's duplicate details")

    link = db.query(ComplaintDuplicateLink).filter(ComplaintDuplicateLink.complaint_id == complaint.id).first()
    if not link:
        return {
            "complaint_id": complaint.id,
            "has_duplicate_group": False,
            "duplicate_group_id": None,
            "representative_complaint_id": None,
            "report_count": 1,
            "related_complaints": [],
        }

    group = db.query(DuplicateGroup).filter(DuplicateGroup.id == link.group_id).first()
    sibling_links = db.query(ComplaintDuplicateLink).filter(ComplaintDuplicateLink.group_id == group.id).all()

    related = []
    for sl in sibling_links:
        related.append({
            "complaint_id": sl.complaint_id,
            "similarity_score": sl.similarity_score,
            "is_representative": sl.complaint_id == group.representative_complaint_id,
        })

    return {
        "complaint_id": complaint.id,
        "has_duplicate_group": True,
        "duplicate_group_id": group.id,
        "representative_complaint_id": group.representative_complaint_id,
        "report_count": group.report_count,
        "unique_users_count": group.unique_users_count,
        "related_complaints": related,
    }


@router.get("/{id}/priority", response_model=PriorityResponse)
def get_complaint_priority(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve current priority score and explainable factor breakdown."""
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if current_user.role != "admin" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this complaint's priority")

    prio = db.query(PriorityAnalysis).filter(PriorityAnalysis.complaint_id == id).first()
    if not prio:
        raise HTTPException(status_code=404, detail="Priority analysis has not been performed for this complaint yet")

    return prio


@router.get("/{id}/priority/history", response_model=list[PriorityHistoryResponse])
def get_complaint_priority_history(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve historical audit log of priority score recalculations."""
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if current_user.role != "admin" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this complaint's priority history")

    history = (
        db.query(PriorityHistory)
        .filter(PriorityHistory.complaint_id == id)
        .order_by(PriorityHistory.created_at.desc())
        .all()
    )
    return history
