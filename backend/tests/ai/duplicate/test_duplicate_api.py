"""Integration tests for duplicate detection REST APIs."""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintStatus
from app.models.user import User


@pytest.fixture
def test_complaints_pair(db: Session, test_user: User):
    # Base complaint
    c1 = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Hazardous pothole in road",
        image_path="test_a.jpg",
        image_original_name="test_a.jpg",
        latitude=12.9716,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    # Duplicate complaint right next to it
    c2 = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Dangerous road pothole near same spot",
        image_path="test_b.jpg",
        image_original_name="test_b.jpg",
        latitude=12.9717,
        longitude=77.5946,
        status=ComplaintStatus.VERIFIED,
    )
    db.add_all([c1, c2])
    db.commit()
    return c1, c2


def test_post_duplicates_check_api(client: TestClient, user_headers: dict, test_complaints_pair):
    c1, c2 = test_complaints_pair

    # Run duplicate check for c2
    res = client.post(
        "/api/ai/duplicates/check",
        headers=user_headers,
        json={"complaint_id": str(c2.id)}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["complaint_id"] == str(c2.id)
    assert "decision" in data
    assert data["decision"] in ["NEW", "POSSIBLE_DUPLICATE", "LIKELY_DUPLICATE"]
    assert "duplicate_score" in data
    assert "explanation" in data


def test_get_complaint_duplicates_api(client: TestClient, user_headers: dict, test_complaints_pair):
    c1, c2 = test_complaints_pair

    res = client.get(
        f"/api/complaints/{c1.id}/duplicates",
        headers=user_headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["complaint_id"] == str(c1.id)
    assert "has_duplicate_group" in data


def test_duplicates_check_unauthorized_user(client: TestClient, admin_headers: dict, test_complaints_pair, db: Session):
    c1, _ = test_complaints_pair
    # Create another citizen user
    other_user = User(
        id=uuid.uuid4(),
        name="Other Citizen",
        email=f"other_{uuid.uuid4().hex[:6]}@civicai.com",
        password_hash="hash",
        role="citizen",
        is_active=True,
    )
    db.add(other_user)
    db.commit()

    from app.core.security import create_access_token
    token = create_access_token({"sub": str(other_user.id)})
    other_headers = {"Authorization": f"Bearer {token}"}

    # Other citizen trying to check c1
    res = client.post(
        "/api/ai/duplicates/check",
        headers=other_headers,
        json={"complaint_id": str(c1.id)}
    )
    assert res.status_code == 403
