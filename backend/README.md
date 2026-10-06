# CivicAI — AI-Powered Civic Infrastructure Complaint Verification and Prioritization System (Backend)

## 1. System Overview

CivicAI is a production-grade FastAPI backend developed for an Artificial Intelligence & Data Science civic infrastructure complaint platform. The backend connects Computer Vision, NLP consistency analysis, geospatial clustering, and multi-criteria prioritization into an explainable, asynchronous pipeline.

### End-to-End Processing Workflow

```text
Complaint Submission (Image + Description + GPS)
        ↓
Image Validation & Storage (MIME, Dimensions, Traversal Protection)
        ↓
Vision Inference (YOLO Object Detection)
        ↓
Complaint Verification (Quality, Relevance, Consistency, Verification Score)
        ↓
Severity Assessment (Damage Extent, Safety Risk, Infra Impact, Public Disruption)
        ↓
Duplicate Detection (Haversine Geo-Distance, 512-dim CNN & 384-dim Text Embeddings)
        ↓
Intelligent Prioritization (Dynamic Weight Redistribution, Saturating Frequency Curve)
        ↓
Department Recommendation (Configurable Mappings, Multi-Issue Support, Manual Review Fallback)
        ↓
Administrative Dispatch (Department Assignment & Strict Lifecycle Transition Auditing)
```

---

## 2. Subsystem Architecture

| Subsystem | Phase | Core Modules | Key Features |
| :--- | :---: | :--- | :--- |
| **Foundation & Auth** | 1 | `app/api/auth.py`, `app/models/user.py` | JWT authentication, role-based access control (`CITIZEN`, `ADMIN`), password hashing. |
| **Dataset & YOLO** | 2-3 | `ml/`, `app/ai/detection.py` | Ultralytics YOLO inference, bounding-box geometry, normalized defect region metrics. |
| **Verification & Quality** | 4 | `app/ai/verification/` | Sharpness, brightness, blur filtering, text-image consistency, `VERIFIED`/`NEEDS_REVIEW`/`REJECTED`. |
| **Severity Assessment** | 5 | `app/ai/severity/` | Multi-factor damage extent, life-safety hazard, infrastructure criticality, 0–100 score. |
| **Duplicate Detection** | 6 | `app/ai/duplicate/` | Haversine proximity, MobileNetV3 visual embeddings, semantic text embeddings, `DuplicateGroup` clustering. |
| **Prioritization Engine** | 7 | `app/ai/priority/` | Explainable weighted score, dynamic missing-GPS weight redistribution, saturating sublinear frequency curve. |
| **Department Routing** | 8 | `app/ai/department/` | Configurable routing (`departments.yaml`), multi-issue recommendations, `MANUAL_REVIEW` fallback. |
| **Orchestration & Status** | 8 | `app/services/` | Asynchronous FastAPI background tasks, state machine validator, status history audit logging. |

---

## 3. Quickstart & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.11, 3.12, 3.14)
- SQLite (included) or PostgreSQL

### Setup Virtual Environment
```powershell
# From the backend directory
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Environment Configuration
```powershell
Copy-Item .env.example .env
```

### Database Migration & Department Seeding
```powershell
# Apply Alembic schema migrations
.\venv\Scripts\alembic upgrade head

# Seed municipal departments and category mappings
.\venv\Scripts\python .\scripts\seed_departments.py
```

### Run the FastAPI Server
```powershell
.\venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc UI: `http://localhost:8000/redoc`
- Health Probe: `http://localhost:8000/health`
- Readiness Probe: `http://localhost:8000/ready`

---

## 4. Key API Endpoints

### Citizen Complaints
- `POST /api/complaints/`: Multipart upload with photo, description, optional category, and GPS coordinates. Immediately dispatches the multi-phase AI pipeline asynchronously and returns HTTP 201 with `AI_PROCESSING` status.
- `GET /api/complaints/`: Lists the authenticated citizen's submitted complaints.
- `GET /api/complaints/{id}`: Returns the complete complaint record with populated verification, severity, duplicate group, priority, and department recommendations.
- `GET /api/complaints/{id}/processing-status`: Returns real-time AI progress (0% to 100%) and current processing state (`PENDING` $\rightarrow$ `PROCESSING` $\rightarrow$ `VERIFICATION_COMPLETE` $\dots$ $\rightarrow$ `COMPLETE`).

### Administrative Dispatch
- `GET /api/admin/complaints`: Multi-criteria filtered query (`status`, `priority_level`, `category`, `department`, `severity_level`, `verification_status`, date range), sorted by priority or severity, with pagination.
- `GET /api/admin/complaints/{id}`: Full audit view including assignments and status history.
- `PUT /api/admin/complaints/{id}/assign`: Assigns a verified complaint to a municipal department.
- `PUT /api/admin/complaints/{id}/status`: Updates complaint lifecycle status with strict transition validation (`SUBMITTED` $\rightarrow$ `AI_PROCESSING` $\rightarrow$ `VERIFIED` $\rightarrow$ `ASSIGNED` $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `RESOLVED` $\rightarrow$ `CLOSED`).

### Health & Monitoring
- `GET /health`: Liveness probe returning `{"status": "healthy"}`.
- `GET /ready`: Readiness probe verifying database connection, model availability, and configuration files.

---

## 5. Running Tests

Run the complete backend automated test suite:
```powershell
.\venv\Scripts\python.exe -m pytest -v
```

All 152+ unit and integration tests execute on CPU with zero external network dependencies.
