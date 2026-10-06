"""Tests for Prioritization Engine REST API endpoints."""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from app.models.priority import PriorityAnalysis


def create_verified_complaint_bundle(db: Session, user: User) -> Complaint:
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=user.id,
        category="damaged_road",
        description="Cracked road surface with potholes",
        image_path="/tmp/road.jpg",
        image_original_name="road.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    db.add(complaint)
    db.commit()

    ai = AIAnalysis(
        complaint_id=complaint.id,
        detected_class="damaged_road",
        confidence=0.91,
        is_civic_issue=True,
        detection_status="COMPLETED",
        verification_score=85.0,
        verification_status="VERIFIED",
    )
    db.add(ai)

    sev = SeverityAnalysis(
        complaint_id=complaint.id,
        severity_score=78.0,
        severity_level="HIGH",
        safety_risk_score=75.0,
        infrastructure_impact_score=80.0,
        public_impact_score=72.0,
        explanation="High severity road damage",
    )
    db.add(sev)
    db.commit()
    db.refresh(complaint)
    return complaint


def test_post_priority_evaluate_api(
    client: TestClient,
    db: Session,
    test_user: User,
    user_headers: dict,
):
    complaint = create_verified_complaint_bundle(db, test_user)

    response = client.post(
        "/api/ai/priority",
        json={"complaint_id": str(complaint.id)},
        headers=user_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["complaint_id"] == str(complaint.id)
    assert "priority_score" in data
    assert "priority_level" in data
    assert "contributing_factors" in data
    assert "explanation" in data


def test_get_complaint_priority_api(
    client: TestClient,
    db: Session,
    test_user: User,
    user_headers: dict,
):
    complaint = create_verified_complaint_bundle(db, test_user)

    # First evaluate priority
    client.post(
        "/api/ai/priority",
        json={"complaint_id": str(complaint.id)},
        headers=user_headers,
    )

    # Now retrieve priority
    response = client.get(
        f"/api/complaints/{complaint.id}/priority",
        headers=user_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["complaint_id"] == str(complaint.id)


def test_get_complaint_priority_history_api(
    client: TestClient,
    db: Session,
    test_user: User,
    user_headers: dict,
):
    complaint = create_verified_complaint_bundle(db, test_user)

    # Evaluate priority twice to produce 2 history records
    client.post(
        "/api/ai/priority",
        json={"complaint_id": str(complaint.id)},
        headers=user_headers,
    )
    client.post(
        "/api/ai/priority",
        json={"complaint_id": str(complaint.id), "force_recalculate": True},
        headers=user_headers,
    )

    response = client.get(
        f"/api/complaints/{complaint.id}/priority/history",
        headers=user_headers,
    )
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 2


def test_admin_priority_queue_api(
    client: TestClient,
    db: Session,
    test_user: User,
    test_admin: User,
    user_headers: dict,
    admin_headers: dict,
):
    complaint = create_verified_complaint_bundle(db, test_user)
    client.post(
        "/api/ai/priority",
        json={"complaint_id": str(complaint.id)},
        headers=user_headers,
    )

    # Regular citizen should get 403 Forbidden
    resp_user = client.get("/api/ai/priority/queue", headers=user_headers)
    assert resp_user.status_code == 403

    # Admin should get 200 OK
    resp_admin = client.get("/api/ai/priority/queue", headers=admin_headers)
    assert resp_admin.status_code == 200
    data = resp_admin.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
