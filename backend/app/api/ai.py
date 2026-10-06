"""AI analysis and verification API routes.

Endpoints:
    POST /api/ai/verify                  — Real-time complaint verification
    POST /api/ai/analyze/{complaint_id}  — Run verification on an existing complaint (Admin)
    GET  /api/ai/results/{complaint_id}  — Get stored AI verification results (Citizen/Admin)
    POST /api/ai/review/{complaint_id}   — Human review action for NEEDS_REVIEW complaints (Admin)
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_admin
from app.database.session import get_db
from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from app.schemas.ai_analysis import (
    VerificationResponse,
    AIAnalysisResponse,
    ReviewActionRequest,
    ReviewActionResponse,
)
from app.schemas.severity import (
    SeverityAssessmentRequest,
    SeverityAssessmentResponse,
)
from app.schemas.duplicate import (
    DuplicateCheckRequest,
    DuplicateCheckResponse,
)
from app.schemas.priority import (
    PriorityEvaluateRequest,
    PriorityResponse,
    PriorityQueueItemResponse,
)
from app.ai.verification.verification_service import ComplaintVerificationService
from app.ai.verification.review_service import HumanReviewService
from app.ai.severity.severity_service import SeverityAssessmentService
from app.ai.duplicate.duplicate_service import DuplicateDetectionService
from app.ai.priority.priority_service import priority_service
from app.services.priority_queue_service import priority_queue_service

router = APIRouter()
verification_service = ComplaintVerificationService()
severity_service = SeverityAssessmentService()
duplicate_service = DuplicateDetectionService()


@router.post("/verify", response_model=VerificationResponse, status_code=status.HTTP_200_OK)
async def verify_complaint_endpoint(
    image: UploadFile = File(..., description="Uploaded photograph of the issue"),
    description: Optional[str] = Form(None, description="Citizen's problem description"),
    category: Optional[str] = Form(None, description="Optional user-selected category"),
    latitude: Optional[float] = Form(None, description="Optional GPS latitude"),
    longitude: Optional[float] = Form(None, description="Optional GPS longitude"),
    current_user: User = Depends(get_current_user),
):
    """
    Real-time AI Verification Endpoint.

    Evaluates image quality, runs Computer Vision detection, checks civic relevance,
    analyzes textual description, evaluates image-text consistency, and returns
    VERIFIED, NEEDS_REVIEW, or REJECTED with transparent explanation.
    """
    # Read image bytes safely
    contents = await image.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded image file is empty.")

    # Execute complete verification pipeline
    result = verification_service.verify_complaint(
        image_input=contents,
        description=description,
        selected_category=category,
        latitude=latitude,
        longitude=longitude
    )

    return result


@router.post("/analyze/{complaint_id}", response_model=AIAnalysisResponse)
async def analyze_complaint(
    complaint_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    Run AI verification on an existing stored complaint and record results to the database.

    Requires admin authentication.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint not found: {complaint_id}")

    if not complaint.image_path:
        raise HTTPException(status_code=400, detail="Complaint has no associated image.")

    # Execute verification using stored image file
    result = verification_service.verify_complaint(
        image_input=complaint.image_path,
        description=complaint.description,
        selected_category=complaint.category.value if hasattr(complaint.category, "value") else str(complaint.category),
        latitude=complaint.latitude,
        longitude=complaint.longitude
    )

    # Map verification status to ComplaintStatus enum
    new_status_str = result["verification_status"]
    if new_status_str == "VERIFIED":
        complaint.status = ComplaintStatus.VERIFIED
    elif new_status_str == "NEEDS_REVIEW":
        complaint.status = ComplaintStatus.NEEDS_REVIEW
    elif new_status_str == "REJECTED":
        complaint.status = ComplaintStatus.REJECTED

    # Create or update AIAnalysis record
    ai_record = db.query(AIAnalysis).filter(AIAnalysis.complaint_id == complaint.id).first()
    if not ai_record:
        ai_record = AIAnalysis(complaint_id=complaint.id)
        db.add(ai_record)

    primary_det = result["detections"][0] if result["detections"] else {}
    ai_record.detected_class = result.get("detected_category")
    ai_record.confidence = result.get("detection_confidence", 0.0)
    ai_record.bounding_box = {"bbox": primary_det.get("bbox", [])} if primary_det else {}
    ai_record.image_width = result["image_quality"].get("metrics", {}).get("width")
    ai_record.image_height = result["image_quality"].get("metrics", {}).get("height")
    ai_record.is_civic_issue = result["relevance"].get("is_relevant", False)
    ai_record.detection_status = "COMPLETED"
    ai_record.verification_score = result["verification_score"]
    ai_record.verification_status = result["verification_status"]
    ai_record.image_quality_score = float(result["image_quality"].get("score", 0))
    ai_record.text_consistency_score = float(result["consistency"].get("score", 0))
    ai_record.explanation = result.get("explanation", [])
    ai_record.audit_metadata = result.get("audit_trail", {})
    ai_record.model_version = result.get("audit_trail", {}).get("model_version")
    ai_record.config_version = result.get("audit_trail", {}).get("config_version")

    db.commit()
    db.refresh(ai_record)

    return ai_record


@router.get("/results/{complaint_id}", response_model=AIAnalysisResponse)
def get_analysis_results(
    complaint_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get AI analysis results for a complaint.

    Citizens can view results for their own complaints; admins can view any.
    """
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if user.role != "admin" and complaint.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this complaint's analysis")

    ai_record = db.query(AIAnalysis).filter(AIAnalysis.complaint_id == complaint_id).first()
    if not ai_record:
        raise HTTPException(status_code=404, detail="AI analysis has not been performed for this complaint yet")

    return ai_record


@router.post("/review/{complaint_id}", response_model=ReviewActionResponse)
def review_complaint_action(
    complaint_id: uuid.UUID,
    body: ReviewActionRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    Administrator Human Review Action.

    Allows an admin to approve, reject, or request additional information
    for a complaint that was flagged as NEEDS_REVIEW by the AI pipeline.
    """
    return HumanReviewService.process_review_action(
        db=db,
        complaint_id=complaint_id,
        reviewer_id=admin.id,
        action=body.action,
        remarks=body.remarks
    )


@router.post("/severity", response_model=SeverityAssessmentResponse, status_code=status.HTTP_200_OK)
def assess_complaint_severity(
    body: SeverityAssessmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    AI-Based Severity Assessment and Damage Impact Analysis.

    Evaluates damage extent, safety risk, infrastructure impact, and public impact
    for a VERIFIED complaint. Rejects unverified or rejected complaints.
    """
    if not body.complaint_id:
        raise HTTPException(status_code=400, detail="complaint_id is required for severity analysis.")

    complaint = db.query(Complaint).filter(Complaint.id == body.complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint not found: {body.complaint_id}")

    # Gating check: Must be VERIFIED or admin-approved
    if complaint.status == ComplaintStatus.REJECTED:
        raise HTTPException(
            status_code=400,
            detail="Cannot calculate severity for rejected complaints."
        )

    if complaint.status != ComplaintStatus.VERIFIED and current_user.role != "admin":
        raise HTTPException(
            status_code=400,
            detail=f"Complaint is in '{complaint.status}' status. Only VERIFIED complaints can be assessed for severity."
        )

    # Authorization check
    if current_user.role != "admin" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this complaint.")

    # Caching check
    existing_severity = db.query(SeverityAnalysis).filter(SeverityAnalysis.complaint_id == complaint.id).first()
    if existing_severity and not body.force_recompute:
        if (
            existing_severity.model_version == severity_service.model_version
            and existing_severity.configuration_version == severity_service.config.version
        ):
            return SeverityAssessmentResponse(
                complaint_id=complaint.id,
                severity_score=existing_severity.severity_score,
                severity_level=existing_severity.severity_level,
                safety_risk_score=existing_severity.safety_risk_score,
                infrastructure_impact_score=existing_severity.infrastructure_impact_score,
                public_impact_score=existing_severity.public_impact_score,
                detection_analysis=existing_severity.detection_analysis or [],
                evidence=existing_severity.evidence or {
                    "damage_extent": 50.0,
                    "safety_risk": existing_severity.safety_risk_score,
                    "infrastructure_impact": existing_severity.infrastructure_impact_score,
                    "public_impact": existing_severity.public_impact_score,
                    "detection_confidence": 85.0,
                    "text_signal": 50.0,
                },
                factors=existing_severity.severity_factors.get("factors", []) if isinstance(existing_severity.severity_factors, dict) else [],
                explanation=existing_severity.explanation.split("\n") if existing_severity.explanation else [],
                model_version=existing_severity.model_version,
                severity_config_version=existing_severity.configuration_version,
                cached=True,
            )

    # Fetch AI analysis detections if available, otherwise construct from category
    ai_record = db.query(AIAnalysis).filter(AIAnalysis.complaint_id == complaint.id).first()
    detections = []
    if ai_record and ai_record.detected_class:
        bbox = []
        if ai_record.bounding_box and isinstance(ai_record.bounding_box, dict):
            bbox = ai_record.bounding_box.get("bbox", [])
        detections.append({
            "class_name": ai_record.detected_class,
            "confidence": ai_record.confidence or 0.85,
            "bbox": bbox,
        })
    else:
        cat_str = complaint.category.value if hasattr(complaint.category, "value") else str(complaint.category)
        detections.append({
            "class_name": cat_str,
            "confidence": 0.85,
            "bbox": [100, 100, 300, 300],
        })

    image_meta = {"width": 640, "height": 480}
    location = {"latitude": complaint.latitude, "longitude": complaint.longitude} if complaint.latitude else None

    result = severity_service.assess(
        detections=detections,
        image_metadata=image_meta,
        description=complaint.description,
        location=location,
    )

    # Persist or update in database
    if not existing_severity:
        existing_severity = SeverityAnalysis(complaint_id=complaint.id)
        db.add(existing_severity)

    existing_severity.severity_score = result["severity_score"]
    existing_severity.severity_level = result["severity_level"]
    existing_severity.safety_risk_score = result["safety_risk_score"]
    existing_severity.infrastructure_impact_score = result["infrastructure_impact_score"]
    existing_severity.public_impact_score = result["public_impact_score"]
    existing_severity.severity_factors = {"factors": result["factors"]}
    existing_severity.detection_analysis = result["detection_analysis"]
    existing_severity.evidence = result["evidence"]
    existing_severity.explanation = "\n".join(result["explanation"])
    existing_severity.model_version = result["model_version"]
    existing_severity.configuration_version = result["severity_config_version"]

    db.commit()
    db.refresh(existing_severity)

    return SeverityAssessmentResponse(
        complaint_id=complaint.id,
        severity_score=result["severity_score"],
        severity_level=result["severity_level"],
        safety_risk_score=result["safety_risk_score"],
        infrastructure_impact_score=result["infrastructure_impact_score"],
        public_impact_score=result["public_impact_score"],
        detection_analysis=result["detection_analysis"],
        evidence=result["evidence"],
        factors=result["factors"],
        explanation=result["explanation"],
        model_version=result["model_version"],
        severity_config_version=result["severity_config_version"],
        processing_time_ms=result["processing_time_ms"],
        cached=False,
    )


@router.get("/severity/{complaint_id}", response_model=SeverityAssessmentResponse)
def get_complaint_severity(
    complaint_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve existing severity assessment for a complaint."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if current_user.role != "admin" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this complaint's severity")

    severity_rec = db.query(SeverityAnalysis).filter(SeverityAnalysis.complaint_id == complaint_id).first()
    if not severity_rec:
        raise HTTPException(status_code=404, detail="Severity analysis has not been performed for this complaint yet")

    factors = []
    if isinstance(severity_rec.severity_factors, dict):
        factors = severity_rec.severity_factors.get("factors", [])

    return SeverityAssessmentResponse(
        complaint_id=complaint.id,
        severity_score=severity_rec.severity_score,
        severity_level=severity_rec.severity_level,
        safety_risk_score=severity_rec.safety_risk_score,
        infrastructure_impact_score=severity_rec.infrastructure_impact_score,
        public_impact_score=severity_rec.public_impact_score,
        detection_analysis=severity_rec.detection_analysis or [],
        evidence=severity_rec.evidence or {
            "damage_extent": 50.0,
            "safety_risk": severity_rec.safety_risk_score,
            "infrastructure_impact": severity_rec.infrastructure_impact_score,
            "public_impact": severity_rec.public_impact_score,
            "detection_confidence": 85.0,
            "text_signal": 50.0,
        },
        factors=factors,
        explanation=severity_rec.explanation.split("\n") if severity_rec.explanation else [],
        model_version=severity_rec.model_version,
        severity_config_version=severity_rec.configuration_version,
        cached=True,
    )


@router.post("/duplicates/check", response_model=DuplicateCheckResponse, status_code=status.HTTP_200_OK)
def check_duplicate_complaint(
    body: DuplicateCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    AI-Powered Duplicate Complaint Detection.

    Compares the complaint against candidate complaints using geographic distance,
    visual image similarity, text description semantics, and category compatibility.
    """
    complaint = db.query(Complaint).filter(Complaint.id == body.complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint not found: {body.complaint_id}")

    if current_user.role != "admin" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to run duplicate check on this complaint.")

    result = duplicate_service.detect_duplicates(
        complaint_id=complaint.id,
        db=db,
        force_recompute=body.force_recompute,
    )

    return result


@router.post("/priority", response_model=PriorityResponse, status_code=status.HTTP_200_OK)
def evaluate_priority_endpoint(
    body: PriorityEvaluateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Intelligent Complaint Prioritization Engine Endpoint.

    Evaluates verified AI evidence (Phase 4 verification, Phase 5 multi-factor severity,
    Phase 6 duplicate clusters, location impact, and escalation) into an explainable 0-100 score.
    """
    complaint = db.query(Complaint).filter(Complaint.id == body.complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint not found: {body.complaint_id}")

    if current_user.role != "admin" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to evaluate priority for this complaint.")

    try:
        analysis = priority_service.evaluate_complaint_priority(
            complaint_id=body.complaint_id,
            db=db,
            unresolved_days=body.unresolved_days,
            is_arterial_road=body.is_arterial_road,
            is_school_zone=body.is_school_zone,
            is_hospital_zone=body.is_hospital_zone,
            reason="API_REQUEST",
        )
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Priority evaluation failed: {str(e)}")


@router.get("/priority/queue")
def get_priority_queue_endpoint(
    priority_level: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    sort_by: str = "priority_score",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    Administrative Priority Queue.

    Retrieves sorted, filtered list of prioritized complaints for municipal triage dispatch.
    Requires administrator authentication.
    """
    items, total = priority_queue_service.get_priority_queue(
        db=db,
        priority_level=priority_level,
        category=category,
        status=status,
        min_score=min_score,
        max_score=max_score,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
    )
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
