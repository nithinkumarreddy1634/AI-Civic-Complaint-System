"""Integration tests for severity assessment API endpoints."""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintStatus, ComplaintCategory
from app.models.ai_analysis import AIAnalysis
from app.models.user import User


@pytest.fixture
def verified_complaint(db: Session, test_user: User):
    comp = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category=ComplaintCategory.POTHOLE,
        status=ComplaintStatus.VERIFIED,
        description="Large hazardous pothole in the road near the market.",
        image_path="dummy/path.jpg",
        image_original_name="path.jpg",
        latitude=12.9716,
        longitude=77.5946,
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)

    # Attach AI analysis record
    ai_rec = AIAnalysis(
        complaint_id=comp.id,
        detected_class="pothole",
        confidence=0.92,
        bounding_box={"bbox": [50, 50, 250, 250]},
        verification_status="VERIFIED",
    )
    db.add(ai_rec)
    db.commit()
    return comp


@pytest.fixture
def rejected_complaint(db: Session, test_user: User):
    comp = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category=ComplaintCategory.GARBAGE,
        status=ComplaintStatus.REJECTED,
        description="Non-civic photo rejected",
        image_path="dummy/rejected.jpg",
        image_original_name="rejected.jpg",
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp


def test_assess_severity_verified_complaint_success(client: TestClient, user_headers: dict, verified_complaint: Complaint):
    response = client.post(
        "/api/ai/severity",
        headers=user_headers,
        json={"complaint_id": str(verified_complaint.id)}
    )
    assert response.status_code == 200
    data = response.json()
    assert "severity_score" in data
    assert 0.0 <= data["severity_score"] <= 100.0
    assert data["severity_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert "safety_risk_score" in data
    assert "infrastructure_impact_score" in data
    assert "public_impact_score" in data
    assert data["cached"] is False


def test_assess_severity_caching_behavior(client: TestClient, user_headers: dict, verified_complaint: Complaint):
    # First call: computes and stores
    res1 = client.post(
        "/api/ai/severity",
        headers=user_headers,
        json={"complaint_id": str(verified_complaint.id)}
    )
    assert res1.status_code == 200
    assert res1.json()["cached"] is False

    # Second call without force_recompute: returns cached result
    res2 = client.post(
        "/api/ai/severity",
        headers=user_headers,
        json={"complaint_id": str(verified_complaint.id), "force_recompute": False}
    )
    assert res2.status_code == 200
    assert res2.json()["cached"] is True
    assert res2.json()["severity_score"] == res1.json()["severity_score"]

    # Third call with force_recompute=True
    res3 = client.post(
        "/api/ai/severity",
        headers=user_headers,
        json={"complaint_id": str(verified_complaint.id), "force_recompute": True}
    )
    assert res3.status_code == 200
    assert res3.json()["cached"] is False


def test_assess_severity_rejected_complaint_fails(client: TestClient, user_headers: dict, rejected_complaint: Complaint):
    response = client.post(
        "/api/ai/severity",
        headers=user_headers,
        json={"complaint_id": str(rejected_complaint.id)}
    )
    assert response.status_code == 400
    assert "rejected" in response.json()["detail"].lower()


def test_get_severity_endpoint(client: TestClient, user_headers: dict, verified_complaint: Complaint):
    # Calculate first
    client.post(
        "/api/ai/severity",
        headers=user_headers,
        json={"complaint_id": str(verified_complaint.id)}
    )

    # Fetch via GET
    res = client.get(
        f"/api/ai/severity/{verified_complaint.id}",
        headers=user_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["complaint_id"] == str(verified_complaint.id)
    assert "severity_score" in data
    assert data["cached"] is True
