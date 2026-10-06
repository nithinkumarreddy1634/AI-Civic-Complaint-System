# Interview Preparation & Resume Project Descriptions

---

## 1. 60–90 Second Interview Elevator Pitch

> *"My final-year capstone project is an **AI-Powered Civic Infrastructure Complaint Verification and Prioritization System** built to solve the operational bottleneck faced by municipal authorities.*
>
> *When citizens report infrastructure issues like potholes, open manholes, or water pipeline bursts, municipal backends are inundated with thousands of raw photos and duplicate complaints that currently require manual human inspection.*
>
> *I designed and developed an end-to-end multi-modal platform. When a citizen uploads an image and GPS coordinates, our 10-stage AI pipeline audits image quality with OpenCV, detects defects with a fine-tuned **YOLOv8** model, evaluates cross-modal consistency against citizen descriptions, estimates physical damage severity, detects spatial and visual duplicates within a 500-meter radius, calculates an objective multi-criteria Priority Score, and recommends the responsible municipal department.*
>
> *On the engineering side, I built the asynchronous backend using **FastAPI** and **PostgreSQL**, engineered a modern dark-themed operations dashboard with **React 19** and **Leaflet GIS**, containerized the stack with **Docker**, and authored an automated test suite of **210 passing tests** covering unit, integration, OWASP security, and end-to-end workflows. The system achieves a **91.4% mAP@50** detection benchmark with an average end-to-end pipeline latency of **1.42 seconds**."*

---

## 2. Professional Resume Descriptions

### Option A: Standard Bulleted Format (Software Engineer / Full Stack Focus)

**AI-Powered Civic Infrastructure Management Platform** | *FastAPI, React 19, YOLOv8, PostgreSQL, Docker*
- Engineered an end-to-end civic complaint triage platform featuring a 10-stage decision-support pipeline combining computer vision, NLP, and multi-criteria prioritization.
- Trained and integrated a fine-tuned YOLOv8 object detector achieving **91.4% mAP@50** across 7 municipal defect classes with sub-second CPU inference.
- Implemented multi-modal duplicate detection fusing geospatial Haversine distance, ResNet50 visual embeddings, and text cosine similarity to link redundant tickets within 500m.
- Built a high-concurrency asynchronous REST backend using FastAPI and SQLAlchemy, securing endpoints with JWT auth, RBAC, path traversal sanitization, and structured tracing.
- Developed a dark-themed operations dashboard with React 19 and Leaflet GIS mapping, complete with animated SVG telemetry and 210 passing automated test suites.

---

### Option B: Concise 3-Line Format (High-Density Resume)

**AI Civic Infrastructure Complaint Verification & Prioritization System** *(Python, FastAPI, YOLOv8, React, PostgreSQL)*
- Architected an automated 10-stage civic grievance verification pipeline utilizing YOLOv8 object detection (91.4% mAP@50) and OpenCV image quality auditing.
- Formulated an algorithmic multi-attribute priority scoring engine and multi-modal duplicate clustering system to eliminate redundant municipal dispatches.
- Delivered an enterprise React 19 / Leaflet GIS command console backed by containerized FastAPI microservices and 210 automated unit, security, and E2E tests.

---

## 3. Key Technical Interview Talking Points

### 1. Handling Imbalanced or Low-Quality Data
- **Point**: "Citizen photos in the wild vary wildly in lighting and blur. We built an automated OpenCV audit gate that checks Laplacian blur variance ($\sigma^2 \ge 100$) and grayscale histogram distribution before invoking the neural network, rejecting unusable uploads without wasting GPU inference cycles."

### 2. Multi-Modal Verification Strategy
- **Point**: "Rather than trusting visual detection alone, we evaluate cross-modal consistency by comparing YOLO bounding box labels with NLP extracted keywords and user form selections. This prevents prank submissions (e.g., submitting a living room photo under 'Pothole')."

### 3. Duplicate Detection vs Silent Deletion
- **Point**: "A common mistake in complaint systems is automatically deleting duplicates. If 50 citizens report the same open manhole, deleting 49 reports hides community urgency. Our system links duplicate tickets to a primary incident cluster and applies a **Frequency Boost** that increases the parent ticket's priority score."

### 4. Human-in-the-Loop AI Governance
- **Point**: "We explicitly designed this as a decision-support tool rather than an autonomous decision-maker. The administrator console presents raw bounding boxes, confidence intervals, and explainable feature weightings, allowing municipal engineers to override AI decisions when necessary."

---

## 4. LinkedIn / Portfolio Blurb

🚀 **Excited to share my final-year project: AI-Powered Civic Infrastructure Complaint Verification and Prioritization System!**

Municipal bodies receive thousands of infrastructure complaints daily, but manual triage creates severe backlogs. I built a full-stack, AI-powered operations platform that automates incident verification, severity assessment, duplicate detection, and departmental routing within 1.5 seconds.

**Core Highlights:**
- 🔍 **Computer Vision**: Fine-tuned YOLOv8 model localizing 7 civic defect classes (91.4% mAP@50).
- 📍 **Spatial-Visual Duplicates**: Fuses Haversine geospatial proximity, ResNet50 feature embeddings, and text similarity.
- ⚡ **Backend**: Asynchronous FastAPI service with PostgreSQL and JWT RBAC.
- 🗺️ **Frontend**: High-density dark operations dashboard with React 19 and Leaflet GIS maps.
- 🛡️ **Quality & Security**: 210 passing automated test suites (unit, integration, OWASP security, and E2E).

Check out the architecture and demo script on GitHub! #ComputerVision #FastAPI #React #DeepLearning #SmartCities #SoftwareEngineering
