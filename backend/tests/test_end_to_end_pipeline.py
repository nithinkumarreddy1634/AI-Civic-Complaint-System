"""Complete End-to-End Integration Test for CivicAI Backend.

Workflow:
1. Citizen registers and logs in (JWT).
2. Citizen submits complaint with image and GPS coordinates.
3. API returns 201 CREATED with AI_PROCESSING status.
4. AI Pipeline orchestrator runs full multi-phase analysis:
   - Vision detection & Phase 4 verification
   - Phase 5 severity assessment
   - Phase 6 duplicate detection & grouping
   - Phase 7 intelligent prioritization
   - Phase 8 department recommendation
5. Real-time processing status tracks progress from 0% to 100%.
6. Admin inspects complaint and views all AI evidence and recommendations.
7. Admin assigns complaint to recommended municipal department.
8. Admin transitions status through IN_PROGRESS to RESOLVED.
9. Audit trail verifies all status history entries are preserved.
"""
import io
import uuid
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus, ProcessingState
from app.models.department import Department
from app.models.status_history import ComplaintStatusHistory
from app.services.complaint_processing_service import complaint_processing_service


def create_sample_image_bytes() -> bytes:
    """Generate a clean synthetic JPEG image for testing."""
    img = Image.new("RGB", (320, 240), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_full_civic_complaint_lifecycle_pipeline(
    client: TestClient,
    db: Session,
    test_user: User,
    test_admin: User,
    user_headers: dict,
    admin_headers: dict,
):
    # Ensure departments are seeded in DB
    from scripts.seed_departments import seed_departments
    seed_departments(db)

    # -------------------------------------------------------------
    # 1. Citizen Submits Complaint with Image & Coordinates
    # -------------------------------------------------------------
    image_bytes = create_sample_image_bytes()
    form_data = {
        "category": "pothole",
        "description": "Hazardous road pothole damaging vehicular tires on main street.",
        "latitude": "12.9716",
        "longitude": "77.5946",
        "address": "100 Feet Road, Indiranagar, Bengaluru",
    }
    files = {
        "image": ("pothole.jpg", image_bytes, "image/jpeg"),
    }

    submit_resp = client.post(
        "/api/complaints/",
        data=form_data,
        files=files,
        headers=user_headers,
    )
    assert submit_resp.status_code == 201
    submit_data = submit_resp.json()
    assert "complaint_id" in submit_data
    complaint_id = uuid.UUID(submit_data["complaint_id"])
    assert submit_data["status"] == ComplaintStatus.AI_PROCESSING

    # -------------------------------------------------------------
    # 2. Execute Full Multi-Phase AI Processing Orchestrator
    # -------------------------------------------------------------
    pipeline_result = complaint_processing_service.process_complaint(complaint_id, db=db)
    assert pipeline_result["processing_state"] == ProcessingState.COMPLETE
    assert "verification" in pipeline_result
    assert "severity" in pipeline_result
    assert "priority" in pipeline_result
    assert "department" in pipeline_result

    # -------------------------------------------------------------
    # 3. Query Real-Time Processing Status
    # -------------------------------------------------------------
    status_resp = client.get(
        f"/api/complaints/{complaint_id}/processing-status",
        headers=user_headers,
    )
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["processing_state"] == ProcessingState.COMPLETE
    assert status_data["progress"] == 100
    assert status_data["error"] is None

    # -------------------------------------------------------------
    # 4. Citizen Retrieves Enriched Complaint Detail
    # -------------------------------------------------------------
    detail_resp = client.get(
        f"/api/complaints/{complaint_id}",
        headers=user_headers,
    )
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == str(complaint_id)
    assert detail_data["verification"] is not None
    assert detail_data["severity"] is not None
    assert detail_data["priority"] is not None
    assert detail_data["department"] is not None
    assert "roads" in detail_data["department"]["department_id"]

    # -------------------------------------------------------------
    # 5. Admin Inspects Full Complaint Detail
    # -------------------------------------------------------------
    admin_detail_resp = client.get(
        f"/api/admin/complaints/{complaint_id}",
        headers=admin_headers,
    )
    assert admin_detail_resp.status_code == 200
    admin_detail = admin_detail_resp.json()
    assert admin_detail["id"] == str(complaint_id)
    assert "assignments" in admin_detail
    assert "status_history" in admin_detail

    # -------------------------------------------------------------
    # 6. Admin Assigns Complaint to Recommended Roads Department
    # -------------------------------------------------------------
    roads_dept = db.query(Department).filter(Department.code == "roads").first()
    assert roads_dept is not None

    assign_resp = client.put(
        f"/api/admin/complaints/{complaint_id}/assign",
        json={
            "department_id": str(roads_dept.id),
            "notes": "Assigned to Roads rapid response crew for immediate pothole patch.",
        },
        headers=admin_headers,
    )
    assert assign_resp.status_code == 200

    # -------------------------------------------------------------
    # 7. Admin Updates Complaint Lifecycle Status: IN_PROGRESS -> RESOLVED
    # -------------------------------------------------------------
    in_prog_resp = client.put(
        f"/api/admin/complaints/{complaint_id}/status",
        params={"new_status": ComplaintStatus.IN_PROGRESS, "remarks": "Road crew is on site with asphalt patcher."},
        headers=admin_headers,
    )
    assert in_prog_resp.status_code == 200
    assert in_prog_resp.json()["status"] == ComplaintStatus.IN_PROGRESS

    resolved_resp = client.put(
        f"/api/admin/complaints/{complaint_id}/status",
        params={"new_status": ComplaintStatus.RESOLVED, "remarks": "Pothole filled and leveled. Road cleared for traffic."},
        headers=admin_headers,
    )
    assert resolved_resp.status_code == 200
    assert resolved_resp.json()["status"] == ComplaintStatus.RESOLVED

    # -------------------------------------------------------------
    # 8. Verify Status History Audit Trail
    # -------------------------------------------------------------
    history_entries = (
        db.query(ComplaintStatusHistory)
        .filter(ComplaintStatusHistory.complaint_id == complaint_id)
        .order_by(ComplaintStatusHistory.changed_at.asc())
        .all()
    )
    assert len(history_entries) >= 3
    statuses = [(h.old_status, h.new_status) for h in history_entries]
    # Check that ASSIGNED, IN_PROGRESS, and RESOLVED were recorded
    assert any(s[1] == ComplaintStatus.ASSIGNED for s in statuses)
    assert any(s[1] == ComplaintStatus.IN_PROGRESS for s in statuses)
    assert any(s[1] == ComplaintStatus.RESOLVED for s in statuses)
