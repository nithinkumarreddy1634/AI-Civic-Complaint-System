"""Integration tests for complaint API endpoints."""
import io
import uuid
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus


def create_test_image_bytes() -> bytes:
    img = Image.new("RGB", (200, 200), color=(100, 100, 100))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_create_complaint(client: TestClient, db: Session, test_user: User, user_headers: dict):
    image_bytes = create_test_image_bytes()
    form_data = {
        "category": "pothole",
        "description": "Deep roadway pothole causing hazard to two-wheelers.",
        "latitude": "12.9716",
        "longitude": "77.5946",
    }
    files = {"image": ("pothole.jpg", image_bytes, "image/jpeg")}

    resp = client.post("/api/complaints/", data=form_data, files=files, headers=user_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "complaint_id" in data
    assert data["status"] == ComplaintStatus.AI_PROCESSING


def test_get_complaints(client: TestClient, db: Session, test_user: User, user_headers: dict):
    # Submit a complaint first
    image_bytes = create_test_image_bytes()
    client.post(
        "/api/complaints/",
        data={"category": "pothole", "description": "Another pothole on 5th main."},
        files={"image": ("p1.jpg", image_bytes, "image/jpeg")},
        headers=user_headers,
    )

    resp = client.get("/api/complaints/", headers=user_headers)
    assert resp.status_code == 200
    complaints = resp.json()
    assert len(complaints) >= 1
    assert complaints[0]["category"] == "pothole"


def test_get_complaint_detail(client: TestClient, db: Session, test_user: User, user_headers: dict):
    image_bytes = create_test_image_bytes()
    post_resp = client.post(
        "/api/complaints/",
        data={"category": "broken_streetlight", "description": "Streetlight unlit for 3 weeks."},
        files={"image": ("s1.jpg", image_bytes, "image/jpeg")},
        headers=user_headers,
    )
    cid = post_resp.json()["complaint_id"]

    resp = client.get(f"/api/complaints/{cid}", headers=user_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == cid
    assert data["category"] == "broken_streetlight"


def test_unauthorized_access(client: TestClient, db: Session, test_user: User):
    # Missing auth token
    resp = client.get("/api/complaints/")
    assert resp.status_code == 401
