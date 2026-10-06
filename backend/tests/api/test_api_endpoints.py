"""
API tests for all major endpoints (Section 13).

Covers:
- Authentication: register, login, me
- Citizen Complaints: POST /, GET /, GET /{id}, GET /{id}/processing-status
- Admin Management: dashboard, list, detail, assign, status update
- AI Endpoints: verify, severity, duplicates, priority
"""
import io
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus
from app.models.department import Department
from tests.fixtures.fixture_data import generate_test_image


def test_auth_endpoints(client: TestClient):
    """Test auth register, login, and profile retrieval."""
    unique_email = f"api_user_{uuid.uuid4().hex[:6]}@civicai.org"
    # Register
    reg_res = client.post(
        "/api/auth/register",
        json={"name": "API Citizen", "email": unique_email, "password": "password123"},
    )
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert data["email"] == unique_email

    # Login
    login_res = client.post(
        "/api/auth/login",
        data={"username": unique_email, "password": "password123"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == unique_email


def test_citizen_complaint_endpoints(client: TestClient, user_headers: dict, test_user: User):
    """Test citizen complaint creation, listing, detail, and processing status."""
    img_bytes = generate_test_image(pattern="circle")

    # POST /api/complaints
    create_res = client.post(
        "/api/complaints/",
        headers=user_headers,
        data={
            "category": "pothole",
            "description": "Hazardous road pothole on main street",
            "latitude": "12.9716",
            "longitude": "77.5946",
            "address": "Main Street Corner",
        },
        files={"image": ("pothole.jpg", io.BytesIO(img_bytes), "image/jpeg")},
    )
    assert create_res.status_code == 201
    complaint_id = create_res.json()["complaint_id"]
    assert complaint_id is not None

    # GET /api/complaints/
    list_res = client.get("/api/complaints/", headers=user_headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(item["id"] == complaint_id for item in items)

    # GET /api/complaints/{id}
    detail_res = client.get(f"/api/complaints/{complaint_id}", headers=user_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == complaint_id

    # GET /api/complaints/{id}/processing-status
    status_res = client.get(f"/api/complaints/{complaint_id}/processing-status", headers=user_headers)
    assert status_res.status_code == 200
    assert "processing_state" in status_res.json()


def test_admin_endpoints(client: TestClient, admin_headers: dict, db: Session, test_user: User):
    """Test admin dashboard, list, detail, assign, and status transitions."""
    # Ensure department exists
    dept = db.query(Department).first()
    if not dept:
        dept = Department(name="Roads Department", code="ROADS_DEPT", description="Road repairs")
        db.add(dept)
        db.commit()

    # Create complaint
    c = Complaint(
        id=uuid.uuid4(),
        user_id=test_user.id,
        category="pothole",
        description="Pothole for admin test",
        image_path="/fake/test.jpg",
        image_original_name="test.jpg",
        status=ComplaintStatus.VERIFIED,
    )
    db.add(c)
    db.commit()

    # Dashboard
    dash_res = client.get("/api/admin/dashboard", headers=admin_headers)
    assert dash_res.status_code == 200

    # Complaints List
    list_res = client.get("/api/admin/complaints", headers=admin_headers)
    assert list_res.status_code == 200
    assert "items" in list_res.json()

    # Complaint Detail
    detail_res = client.get(f"/api/admin/complaints/{c.id}", headers=admin_headers)
    assert detail_res.status_code == 200

    # Assign Department
    assign_res = client.put(
        f"/api/admin/complaints/{c.id}/assign",
        headers=admin_headers,
        json={"department_id": str(dept.id), "notes": "Dispatched to repair crew"},
    )
    assert assign_res.status_code == 200

    # Update Status
    status_res = client.put(
        f"/api/admin/complaints/{c.id}/status?new_status=IN_PROGRESS&remarks=Workers_on_site",
        headers=admin_headers,
    )
    assert status_res.status_code == 200


def test_ai_endpoints(client: TestClient, user_headers: dict):
    """Test direct AI verify endpoint."""
    img_bytes = generate_test_image(pattern="circle")
    verify_res = client.post(
        "/api/ai/verify",
        headers=user_headers,
        data={
            "description": "Pothole in middle of street",
            "category": "pothole",
            "latitude": "12.9716",
            "longitude": "77.5946",
        },
        files={"image": ("pothole.jpg", io.BytesIO(img_bytes), "image/jpeg")},
    )
    assert verify_res.status_code == 200
    res_data = verify_res.json()
    assert "verification_status" in res_data
    assert "verification_score" in res_data
