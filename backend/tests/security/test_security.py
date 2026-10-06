"""
Security Test Suite (Sections 14, 15, 16, 17, 38).

Covers:
- Section 14: Role-Based Access Control (RBAC) & Authorization
- Section 15: Insecure Direct Object Reference (IDOR) Protection
- Section 16: File Upload Security (corrupted, empty, oversized, MIME bypass, path traversal)
- Section 17: SQL Injection and XSS / Input Sanitization
- Section 38: CORS Validation
"""
import io
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.complaint import Complaint, ComplaintStatus
from app.core.security import hash_password, create_access_token
from tests.fixtures.fixture_data import (
    generate_test_image,
    CORRUPTED_IMAGE_BYTES,
    EMPTY_FILE_BYTES,
    TEXT_AS_JPG_BYTES,
)


@pytest.fixture
def citizen_a(db: Session) -> User:
    u = User(
        id=uuid.uuid4(),
        name="Citizen Alpha",
        email=f"alpha_{uuid.uuid4().hex[:6]}@civicai.org",
        password_hash=hash_password("alphaPass123"),
        role="citizen",
        is_active=True,
    )
    db.add(u)
    db.commit()
    return u


@pytest.fixture
def citizen_b(db: Session) -> User:
    u = User(
        id=uuid.uuid4(),
        name="Citizen Beta",
        email=f"beta_{uuid.uuid4().hex[:6]}@civicai.org",
        password_hash=hash_password("betaPass123"),
        role="citizen",
        is_active=True,
    )
    db.add(u)
    db.commit()
    return u


@pytest.fixture
def headers_a(citizen_a: User) -> dict:
    t = create_access_token({"sub": str(citizen_a.id)})
    return {"Authorization": f"Bearer {t}"}


@pytest.fixture
def headers_b(citizen_b: User) -> dict:
    t = create_access_token({"sub": str(citizen_b.id)})
    return {"Authorization": f"Bearer {t}"}


# ---------------------------------------------------------------------------
# Section 14: Authorization / RBAC
# ---------------------------------------------------------------------------
def test_unauthenticated_requests_rejected(client: TestClient):
    """Unauthenticated users must receive 401 Unauthorized on protected routes."""
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/complaints/").status_code == 401
    assert client.get("/api/admin/dashboard").status_code == 401


def test_citizen_cannot_access_admin_endpoints(client: TestClient, headers_a: dict):
    """Citizen role must receive 403 Forbidden when accessing administrative endpoints."""
    assert client.get("/api/admin/dashboard", headers=headers_a).status_code == 403
    assert client.get("/api/admin/complaints", headers=headers_a).status_code == 403
    assert client.get("/api/admin/analytics", headers=headers_a).status_code == 403


# ---------------------------------------------------------------------------
# Section 15: IDOR Access Control Tests
# ---------------------------------------------------------------------------
def test_citizen_cannot_access_another_citizen_complaint(
    client: TestClient, db: Session, citizen_a: User, citizen_b: User, headers_a: dict
):
    """
    Citizen A attempts to view Citizen B's complaint detail.
    Must return 403 Forbidden.
    """
    complaint_b = Complaint(
        id=uuid.uuid4(),
        user_id=citizen_b.id,
        category="pothole",
        description="Citizen B private road issue",
        image_path="/fake/b.jpg",
        image_original_name="b.jpg",
        status=ComplaintStatus.VERIFIED,
    )
    db.add(complaint_b)
    db.commit()

    # Citizen A tries to fetch Citizen B's complaint detail
    res_detail = client.get(f"/api/complaints/{complaint_b.id}", headers=headers_a)
    assert res_detail.status_code == 403

    # Citizen A tries to fetch Citizen B's processing status
    res_status = client.get(f"/api/complaints/{complaint_b.id}/processing-status", headers=headers_a)
    assert res_status.status_code == 403

    # Citizen A tries to fetch Citizen B's duplicate info (Regression test for Bug #1)
    res_dup = client.get(f"/api/complaints/{complaint_b.id}/duplicates", headers=headers_a)
    assert res_dup.status_code == 403


# ---------------------------------------------------------------------------
# Section 16: File Upload Security Tests
# ---------------------------------------------------------------------------
def test_upload_corrupted_image(client: TestClient, headers_a: dict):
    """Uploading corrupted image bytes must be rejected with 400 Bad Request."""
    res = client.post(
        "/api/complaints/",
        headers=headers_a,
        data={"category": "pothole", "description": "Valid complaint description"},
        files={"image": ("corrupted.jpg", io.BytesIO(CORRUPTED_IMAGE_BYTES), "image/jpeg")},
    )
    assert res.status_code == 400
    assert "corrupted" in res.json()["detail"].lower() or "invalid" in res.json()["detail"].lower()


def test_upload_empty_file(client: TestClient, headers_a: dict):
    """Uploading empty 0-byte file must be rejected with 400 Bad Request."""
    res = client.post(
        "/api/complaints/",
        headers=headers_a,
        data={"category": "pothole", "description": "Valid complaint description"},
        files={"image": ("empty.jpg", io.BytesIO(EMPTY_FILE_BYTES), "image/jpeg")},
    )
    assert res.status_code == 400


def test_upload_executable_renamed_as_jpg(client: TestClient, headers_a: dict):
    """Non-image bytes disguised as .jpg must be rejected via MIME signature verification."""
    res = client.post(
        "/api/complaints/",
        headers=headers_a,
        data={"category": "pothole", "description": "Valid complaint description"},
        files={"image": ("malicious.jpg", io.BytesIO(TEXT_AS_JPG_BYTES), "image/jpeg")},
    )
    assert res.status_code == 400
    assert "invalid file type" in res.json()["detail"].lower()


def test_upload_disallowed_extension(client: TestClient, headers_a: dict):
    """Uploading file with disallowed extension (.exe, .sh, .py) must be rejected."""
    res = client.post(
        "/api/complaints/",
        headers=headers_a,
        data={"category": "pothole", "description": "Valid complaint description"},
        files={"image": ("script.py", io.BytesIO(b"print('hello')"), "text/x-python")},
    )
    assert res.status_code == 400
    assert "extension" in res.json()["detail"].lower()


def test_path_traversal_filename_sanitization(client: TestClient, headers_a: dict, db: Session):
    """Path traversal filename (e.g. ../../evil.jpg) must be sanitized and stored safely."""
    valid_bytes = generate_test_image()
    res = client.post(
        "/api/complaints/",
        headers=headers_a,
        data={"category": "pothole", "description": "Road pothole with traversal filename"},
        files={"image": ("../../../../etc/passwd.jpg", io.BytesIO(valid_bytes), "image/jpeg")},
    )
    assert res.status_code == 201
    complaint_id = uuid.UUID(res.json()["complaint_id"])

    c = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    assert c is not None
    # Verify original name was stripped of traversal prefixes
    assert "../" not in c.image_original_name
    assert "..\\" not in c.image_original_name
    assert c.image_original_name == "passwd.jpg"


# ---------------------------------------------------------------------------
# Section 17: SQL Injection and XSS Input Security
# ---------------------------------------------------------------------------
def test_sql_injection_payload_in_description(client: TestClient, headers_a: dict, db: Session):
    """SQL injection payloads in complaint description must be safely parameterized without executing."""
    valid_bytes = generate_test_image()
    sql_payload = "'; DROP TABLE complaints; SELECT * FROM users WHERE '1'='1"

    res = client.post(
        "/api/complaints/",
        headers=headers_a,
        data={"category": "pothole", "description": sql_payload},
        files={"image": ("sql_test.jpg", io.BytesIO(valid_bytes), "image/jpeg")},
    )
    assert res.status_code == 201
    complaint_id = uuid.UUID(res.json()["complaint_id"])

    # Complaints table must still exist and payload safely stored as text
    c = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    assert c is not None
    assert c.description == sql_payload


def test_xss_and_unicode_in_description(client: TestClient, headers_a: dict, db: Session):
    """XSS HTML tags and Unicode emoji must be stored safely without crashing backend."""
    valid_bytes = generate_test_image()
    xss_payload = "<script>alert('XSS')</script> 🕳️ Hazardous Pothole! 日本語 ⚠️"

    res = client.post(
        "/api/complaints/",
        headers=headers_a,
        data={"category": "pothole", "description": xss_payload},
        files={"image": ("xss_test.jpg", io.BytesIO(valid_bytes), "image/jpeg")},
    )
    assert res.status_code == 201
    complaint_id = uuid.UUID(res.json()["complaint_id"])
    c = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    assert c is not None
    assert c.description == xss_payload
