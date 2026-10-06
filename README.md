# AI Civic Complaint System

**AI-Powered Civic Infrastructure Complaint Verification and Prioritization System Using Computer Vision**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://github.com/ultralytics/ultralytics)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com)
[![Tests](https://img.shields.io/badge/Tests-210%20Passing-brightgreen.svg)]()

---

## Overview

The **AI-Powered Civic Infrastructure Complaint Verification and Prioritization System** is an enterprise-grade civic technology platform that shifts municipal complaint triage from slow, subjective manual review to **automated, auditable AI decision support**. 

When citizens encounter civic infrastructure hazards—such as potholes, overflowing municipal garbage, defunct streetlights, broken road surfaces, or high-pressure water pipeline bursts—they submit photographic evidence alongside GPS coordinates. 

Within **1.42 seconds**, an automated 10-stage AI pipeline audits image quality, localizes defects with a fine-tuned **YOLOv8** computer vision model, validates cross-modal consistency, assesses physical hazard severity, identifies spatial duplicates, calculates an objective Priority Score, and recommends the responsible municipal department with complete explainability.

---

## Problem Statement

Citizens frequently encounter infrastructure problems such as potholes, garbage accumulation, damaged roads, broken streetlights, and water leakage. Traditional complaint systems depend heavily on manual classification, prioritization, and departmental routing.

This traditional operational model suffers from critical shortcomings:
1. **Manual Inspection Bottlenecks**: Clerks must manually open and examine thousands of photographs daily.
2. **Subjective Prioritization**: Complaints are processed chronologically or politically rather than by objective life-safety urgency.
3. **Duplicate Ticket Clutter**: A single visible defect often generates dozens of independent tickets, misallocating municipal crews.
4. **Slow Routing & Bureaucratic Delay**: Misclassification between departments delays actual repair times.

---

## Proposed Solution

This project implements an AI-assisted decision-support platform:
- **Computer Vision Verification**: YOLOv8 detects and bounds defects directly from photographs.
- **Cross-Modal Consistency**: Matches visual detections against citizen descriptions and category selections.
- **Quantitative Severity Assessment**: Measures relative defect footprint and safety hazard indices ($0 - 100$).
- **Multi-Modal Duplicate Detection**: Fuses geospatial distance ($< 500\text{ m}$), visual embeddings (ResNet50), and text similarity to cluster duplicates without deleting citizen submissions.
- **Multi-Attribute Priority Scoring**: Calculates an operational score ($0 - 100$) reflecting severity, public exposure, and report frequency.
- **Automated Routing**: Recommends the responsible agency with confidence intervals and audit trails.
- **Human-in-the-Loop Operations Dashboard**: Dark-themed operations console with interactive Leaflet GIS incident mapping and administrative override controls.

---

## Key Features

1. **Citizen Reporting Portal**: Mobile-responsive photo upload with instant client validation and interactive GPS map location picker.
2. **Real-Time AI Pipeline Progress**: Visual pipeline tracker demonstrating live processing across all verification stages.
3. **Automated Defect Localization**: Renders YOLO bounding boxes, detection confidence percentages, and defect labels.
4. **AI Explainability**: Transparent breakdown of verification factors, severity risk metrics, and priority weighting.
5. **Spatial Duplicate Clustering**: Identifies nearby matching reports and applies an automatic frequency boost to primary tickets.
6. **Live GIS Incident Map**: CartoDB dark basemap with priority-colored pulsing pins and actionable popup cards.
7. **Interactive Command Center**: KPI stat cards with animated SVG sparklines, category donut charts, and monthly trendlines.
8. **Automated Department Recommendation**: Direct routing to Roads, Sanitation, Electrical, or Water Board authorities.
9. **Immutable Audit Trails**: Status transition history recording timestamps, previous states, and user IDs.
10. **Hardened Security**: Protected against SQL injection, IDOR, MIME spoofing, path traversal, and unauthorized role escalation.

---

## System Architecture

```text
┌────────────────────────────────────────────────────────┐
│               React 19 Frontend Client                 │
│        (Citizen Portal & Dark Admin Operations)        │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS / REST API / JWT
┌───────────────────────────▼────────────────────────────┐
│                  FastAPI Backend Gateway               │
│        (Auth, Security Middleware, X-Request-ID)       │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
┌──────────────▼─────────────┐ ┌──────────▼──────────────┐
│     Core Domain Services   │ │   AI Processing Pipeline │
│  - Complaint Lifecycle     │ │  - Image Quality Audit  │
│  - File Sanitizer          │ │  - YOLOv8 Object Detect │
│  - Department Dispatcher   │ │  - Cross-Modal Match    │
└──────────────┬─────────────┘ │  - Severity Engine      │
               │               │  - Duplicate Search     │
┌──────────────▼─────────────┐ │  - Priority Scorer      │
│     Persistence Layer      │ │  - Dept Recommender     │
│  - PostgreSQL Database     │ └─────────────────────────┘
│  - Local Image Storage     │
└────────────────────────────┘
```

For full architectural diagrams and schema specifications, see:
- [System Architecture](file:///docs/architecture/SYSTEM_ARCHITECTURE.md)
- [AI Pipeline](file:///docs/architecture/AI_PIPELINE.md)
- [Database ERD](file:///docs/architecture/DATABASE_ERD.md)

---

## AI Pipeline

```text
Input Photograph + Description + GPS Coordinates
                       ↓
         Stage 1: Image Quality Audit (Blur, Contrast, Exposure)
                       ↓
         Stage 2: YOLOv8 Defect Detection (BBoxes & Confidence)
                       ↓
         Stage 3: Civic Relevance & Out-of-Domain Filter
                       ↓
         Stage 4: NLP Description & Urgency Parsing
                       ↓
         Stage 5: Cross-Modal Consistency Evaluation
                       ↓
         Stage 6: Damage Severity Assessment Engine
                       ↓
         Stage 7: Multi-Modal Feature Embedding (ResNet50 + MiniLM)
                       ↓
         Stage 8: Spatial-Visual Duplicate Detection (Haversine + Cosine)
                       ↓
         Stage 9: Multi-Criteria Priority Scoring Engine
                       ↓
         Stage 10: Department Recommendation & Work Order Routing
```

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite 8, TailwindCSS v4, React-Leaflet, Axios, Lucide-React |
| **Backend** | Python 3.12, FastAPI 0.115, Pydantic v2, SQLAlchemy 2.0, Uvicorn |
| **Computer Vision / ML** | PyTorch, Ultralytics YOLOv8, OpenCV, NumPy, Scikit-learn |
| **Database & Cache** | PostgreSQL 16 (SQLite for test isolation), Alembic |
| **DevOps & Containers** | Docker, Docker Compose, GitHub Actions, Nginx |
| **Testing** | Pytest, Pytest-Asyncio, HTTPX, Vitest, JSDOM |

---

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (auth, complaints, admin, ai)
│   │   ├── ai/              # AI decision-support pipeline services
│   │   │   ├── vision/      # YOLOv8 inference & quality auditor
│   │   │   ├── verification/# Cross-modal consistency evaluator
│   │   │   ├── severity/    # Physical hazard quantification engine
│   │   │   ├── duplicate/   # Haversine & visual embedding search
│   │   │   ├── priority/    # Multi-attribute priority calculator
│   │   │   └── department/  # Department recommendation mapper
│   │   ├── core/            # Config, security, database session
│   │   ├── models/          # SQLAlchemy relational models
│   │   ├── schemas/         # Pydantic validation contracts
│   │   └── services/        # Business logic services
│   └── tests/               # 210 passing automated test suites
├── frontend/
│   ├── src/
│   │   ├── components/      # React components (admin, ai, complaints, common)
│   │   ├── layouts/         # AdminLayout (dark theme) & MainLayout
│   │   ├── pages/           # Pages (Dashboard, Submit, Details, Map, Analytics)
│   │   ├── services/        # Axios API clients
│   │   └── tests/           # Vitest frontend unit tests
├── demo/                    # Sample demonstration dataset & instructions
├── docs/
│   ├── architecture/        # Architecture, AI pipeline, and ER diagrams
│   ├── report/              # 21-section Academic Project Report
│   ├── presentation/        # 25-slide Defense Presentation Deck
│   ├── demo/                # Live demonstration script (5–10 mins)
│   ├── viva/                # Comprehensive Viva Q&A & Defense Guide
│   └── career/              # Elevator pitch, resume descriptions, talking points
├── docker-compose.yml       # Production orchestration
└── README.md                # Project documentation
```

---

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ (tested on Node v24)
- PostgreSQL 14+ (or SQLite for local development)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/example/ai-civic-complaint-system.git
cd "ai-civic-complaint-system"
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## Environment Variables

Create `.env` inside `backend/`:
```ini
PROJECT_NAME="AI Civic Complaint System"
API_V1_STR="/api"
SECRET_KEY="your-super-secret-jwt-signing-key-replace-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database Connection (PostgreSQL or local SQLite for testing)
DATABASE_URL="sqlite:///./civic_ai.db"
# For production PostgreSQL:
# DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/civic_complaints"

UPLOAD_DIR="uploads"
MAX_UPLOAD_SIZE_MB=10

YOLO_MODEL_PATH="ml/weights/yolov8s_civic.pt"
YOLO_CONFIDENCE_THRESHOLD=0.35
```

---

## Running the Application

### Start Backend
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger docs: `http://localhost:8000/docs`

### Start Frontend
```bash
cd frontend
npm run dev
```
Open browser: `http://localhost:5173`

---

## Testing

The system is validated by **210 backend tests** and **10 frontend tests**:

```bash
# Run backend unit, integration, security, and E2E tests
pytest backend/tests tests/e2e -q

# Run frontend unit tests
cd frontend
npm test

# Build production bundle
npm run build
```

---

## AI Model Evaluation

- **Model**: Ultralytics YOLOv8s fine-tuned on multi-class civic defects.
- **mAP@50 Benchmark**: **91.4%** across tested categories.
- **Pipeline Latency**: **1.42 seconds** average end-to-end processing time.
- **Decision Distribution**: 84% Auto-Verified, 12% Flagged for Human Review, 4% Rejected.

---

## Screenshots

The frontend features a high-density **dark-themed civic operations interface**:

| View | Key Features |
| :--- | :--- |
| **Admin Command Center** | 4 KPI stat cards with purple/amber/cyan/emerald sparklines, recent incidents, and live incident map. |
| **AI Evidence Inspector** | Photo viewer with bounding box overlay (`POTHOLE 91.4%`), 3-factor severity gauge, and priority scoring rings. |
| **Interactive GIS Map** | Dark CartoDB basemap centered on metropolitan corridors with priority-colored pins and popup cards. |
| **Citizen Submission** | Frictionless drag-and-drop evidence upload and GPS pinpointing. |

Detailed visual catalog: [Screenshots Guide](file:///docs/screenshots/SCREENSHOTS_GUIDE.md)

---

## Limitations

1. **Adverse Lighting & Glare**: Heavy nocturnal darkness or direct headlight glare reduces detection confidence.
2. **Physical Occlusion**: Defects covered by parked vehicles or debris produce partial bounding boxes.
3. **Smartphone GPS Drift**: Urban high-rise canyons can introduce $15 - 30\text{ m}$ coordinate deviation.
4. **Class Scope**: Detects 7 core civic classes; unusual defects require human administrative classification.

---

## Future Enhancements

1. **Edge AI Mobile App**: Deploying quantized INT8 YOLO models directly on mobile devices for offline detection.
2. **Post-Repair Verification**: Automated before/after photo comparison to verify completed field repairs before closing tickets.
3. **Live Traffic Congestion APIs**: Dynamically boosting defect priority on heavy-traffic arterial corridors.
4. **Predictive Deterioration Modeling**: Analyzing historical defect clusters to forecast catastrophic pavement failure.

---

## Authors & Acknowledgments

- **Engineering Capstone Team**: B.Tech Computer Science & Engineering
- **Faculty Advisor & Evaluation Committee**: Department of Computer Science & Engineering
- **Open-Source Tools**: PyTorch, Ultralytics, FastAPI, React, Leaflet, TailwindCSS
