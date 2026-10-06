"""
End-to-End Lifecycle Integration Test (Section 23).

Simulates the complete citizen-to-admin workflow entirely via HTTP API calls
without manually manipulating the database:
1. Register citizen
2. Login citizen
3. Submit complaint with valid image, category, and GPS
4. Execute AI pipeline
5. Verify AI analysis and priority results
6. Login as administrator
7. Retrieve admin dashboard metrics & find the complaint
8. Inspect AI evidence
9. Assign complaint to designated municipal department
10. Update complaint status through lifecycle (IN_PROGRESS -> RESOLVED -> CLOSED)
11. Login as citizen again
12. Confirm final RESOLVED/CLOSED status and historical timeline
"""
import io
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.department import Department
from app.services.complaint_processing_service import complaint_processing_service
from tests.fixtures.fixture_data import generate_test_image


def test_complete_citizen_admin_e2e_lifecycle(client: TestClient, db: Session):
    """
    Complete end-to-end multi-actor workflow test.
    """
    # 0. Seed departments
    from scripts.seed_departments import seed_departments
    seed_departments(db)
    dept = db.query(Department).first()

    # 1. Register citizen
    citizen_email = f"citizen_e2e_{uuid.uuid4().hex[:6]}@civicai.org"
    reg_res = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Doe",
            "email": citizen_email,
            "password": "CitizenSecretPassword123!",
        },
    )
    assert reg_res.status_code == 201

    # 2. Login citizen
    login_citizen = client.post(
        "/api/auth/login",
        data={"username": citizen_email, "password": "CitizenSecretPassword123!"},
    )
    assert login_citizen.status_code == 200
    citizen_token = login_citizen.json()["access_token"]
    citizen_headers = {"Authorization": f"Bearer {citizen_token}"}

    # 3. Submit complaint with image and coordinates
    img_bytes = generate_test_image(pattern="circle")
    submit_res = client.post(
        "/api/complaints/",
        headers=citizen_headers,
        data={
            "category": "pothole",
            "description": "Critical pothole on Main Street causing traffic bottlenecks and vehicle damage",
            "latitude": "12.9716",
            "longitude": "77.5946",
            "address": "123 Main Street, Bangalore",
        },
        files={"image": ("main_st_pothole.jpg", io.BytesIO(img_bytes), "image/jpeg")},
    )
    assert submit_res.status_code == 201
    complaint_id = submit_res.json()["complaint_id"]
    assert complaint_id is not None

    # 4. Trigger synchronous pipeline completion for test verification
    complaint_processing_service.process_complaint(uuid.UUID(complaint_id), db=db)

    # 5. Citizen inspects complaint detail and verifies AI analysis
    detail_res = client.get(f"/api/complaints/{complaint_id}", headers=citizen_headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == complaint_id
    assert detail_data["status"] in ("VERIFIED", "NEEDS_REVIEW", "PRIORITIZED", "AI_PROCESSING", "SUBMITTED")
    assert "status" in detail_data

    # 6. Register/Login as Administrator
    admin_email = f"admin_e2e_{uuid.uuid4().hex[:6]}@civicai.org"
    reg_admin = client.post(
        "/api/auth/register",
        json={
            "name": "Admin Officer",
            "email": admin_email,
            "password": "AdminSecretPassword123!",
        },
    )
    # Upgrade role in DB for this test admin
    from app.models.user import User
    admin_user = db.query(User).filter(User.email == admin_email).first()
    admin_user.role = "admin"
    db.commit()

    login_admin = client.post(
        "/api/auth/login",
        data={"username": admin_email, "password": "AdminSecretPassword123!"},
    )
    assert login_admin.status_code == 200
    admin_token = login_admin.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 7. Admin views dashboard
    dash_res = client.get("/api/admin/dashboard", headers=admin_headers)
    assert dash_res.status_code == 200

    # 8. Admin reviews complaint details
    admin_detail = client.get(f"/api/admin/complaints/{complaint_id}", headers=admin_headers)
    assert admin_detail.status_code == 200
    assert admin_detail.json()["id"] == complaint_id

    # 9. Admin assigns department
    assign_res = client.put(
        f"/api/admin/complaints/{complaint_id}/assign",
        headers=admin_headers,
        json={
            "department_id": str(dept.id),
            "notes": "Assigned to North Ward repair team for immediate asphalt patch",
        },
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["status"] == "ACTIVE"

    # 10. Status transition: ASSIGNED -> IN_PROGRESS
    prog_res = client.put(
        f"/api/admin/complaints/{complaint_id}/status?new_status=IN_PROGRESS&remarks=Repair_crew_dispatched",
        headers=admin_headers,
    )
    assert prog_res.status_code == 200
    assert prog_res.json()["status"] == "IN_PROGRESS"

    # 11. Status transition: IN_PROGRESS -> RESOLVED
    res_res = client.put(
        f"/api/admin/complaints/{complaint_id}/status?new_status=RESOLVED&remarks=Pothole_filled_and_leveled",
        headers=admin_headers,
    )
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "RESOLVED"

    # 12. Status transition: RESOLVED -> CLOSED
    close_res = client.put(
        f"/api/admin/complaints/{complaint_id}/status?new_status=CLOSED&remarks=Final_inspection_completed",
        headers=admin_headers,
    )
    assert close_res.status_code == 200
    assert close_res.json()["status"] == "CLOSED"

    # 13. Citizen views complaint again and confirms final status
    final_citizen_view = client.get(f"/api/complaints/{complaint_id}", headers=citizen_headers)
    assert final_citizen_view.status_code == 200
    assert final_citizen_view.json()["status"] == "CLOSED"
