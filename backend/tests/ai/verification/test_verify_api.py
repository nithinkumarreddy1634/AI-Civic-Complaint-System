"""Integration tests for verification API endpoints and human review actions."""
import io
import uuid
import pytest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintStatus, ComplaintCategory
from app.models.user import User


@pytest.fixture
def dummy_image_bytes():
    arr = np.zeros((300, 300, 3), dtype=np.uint8)
    arr[:, :] = 160
    arr[::20, :, :] = 40
    arr[:, ::20, :] = 220
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_verify_endpoint_success(client: TestClient, user_headers: dict, dummy_image_bytes: bytes):
    response = client.post(
        "/api/ai/verify",
        headers=user_headers,
        data={
            "description": "Large pothole in the road near the bus stand.",
            "category": "pothole"
        },
        files={
            "image": ("test_pothole.jpg", dummy_image_bytes, "image/jpeg")
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "verification_status" in data
    assert data["verification_status"] in ["VERIFIED", "NEEDS_REVIEW", "REJECTED"]
    assert "verification_score" in data
    assert "image_quality" in data
    assert "explanation" in data
    assert len(data["explanation"]) > 0


def test_verify_endpoint_empty_file_fails(client: TestClient, user_headers: dict):
    response = client.post(
        "/api/ai/verify",
        headers=user_headers,
        data={"description": "Test issue"},
        files={"image": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400


def test_admin_review_action(client: TestClient, admin_headers: dict, user_headers: dict, db: Session, test_user: User):
    # Create a dummy complaint in NEEDS_REVIEW status
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category=ComplaintCategory.POTHOLE,
        status=ComplaintStatus.NEEDS_REVIEW,
        description="Possible road issue needing review.",
        image_path="dummy/path.jpg",
        image_original_name="path.jpg"
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    # 1. Citizen cannot review (403)
    res_citizen = client.post(
        f"/api/ai/review/{complaint.id}",
        headers=user_headers,
        json={"action": "approve", "remarks": "Looks genuine"}
    )
    assert res_citizen.status_code == 403

    # 2. Admin approves (200)
    res_admin = client.post(
        f"/api/ai/review/{complaint.id}",
        headers=admin_headers,
        json={"action": "approve", "remarks": "Approved by municipal officer"}
    )
    assert res_admin.status_code == 200
    data = res_admin.json()
    assert data["new_status"] == "VERIFIED"
    assert data["review_action"] == "approve"

    # Verify status in database
    db.refresh(complaint)
    assert complaint.status == ComplaintStatus.VERIFIED


def test_admin_review_invalid_action(client: TestClient, admin_headers: dict, db: Session, test_user: User):
    complaint = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category=ComplaintCategory.GARBAGE,
        status=ComplaintStatus.NEEDS_REVIEW,
        description="Garbage issue",
        image_path="dummy.jpg",
        image_original_name="dummy.jpg"
    )
    db.add(complaint)
    db.commit()

    res = client.post(
        f"/api/ai/review/{complaint.id}",
        headers=admin_headers,
        json={"action": "unsupported_action"}
    )
    assert res.status_code == 400
