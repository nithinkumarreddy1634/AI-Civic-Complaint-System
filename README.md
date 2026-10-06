# 🏙️ AI Civic Complaint System

> **An AI-powered intelligent platform for reporting, classifying, prioritizing, and tracking civic complaints — designed to bridge the gap between citizens and civic authorities.**

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-Frontend-61DAFB?logo=react)](https://react.dev/)
[![Machine Learning](https://img.shields.io/badge/AI%2FML-Machine%20Learning-orange)]()
[![REST API](https://img.shields.io/badge/API-REST-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

---

## 📌 Overview

The **AI Civic Complaint System** is a smart civic issue management platform that allows citizens to report problems in their local communities and enables authorities to efficiently analyze, prioritize, assign, and track those complaints.

Traditional complaint management systems often depend heavily on manual classification and processing. This project introduces **Artificial Intelligence and Machine Learning** to automate important parts of the workflow.

Citizens can submit complaints related to:

- 🛣️ Road damage and potholes
- 🗑️ Garbage and waste accumulation
- 💡 Streetlight failures
- 🚰 Water leakage and supply issues
- 🚧 Damaged public infrastructure
- 🌳 Public cleanliness and environmental issues
- 🏢 Other municipal problems

The system processes the complaint, identifies its category and severity, and provides structured information that can help authorities take appropriate action.

---

# 🎯 Objectives

The primary objectives of the project are:

1. **Simplify civic complaint submission**
2. **Automatically categorize complaints using AI**
3. **Identify complaint severity and priority**
4. **Reduce manual complaint processing**
5. **Improve complaint tracking and transparency**
6. **Help authorities prioritize critical issues**
7. **Provide useful analytics for civic administration**
8. **Create a scalable architecture for smart-city applications**

---

# ✨ Key Features

## 👤 Citizen Module

Citizens can:

- Register and access the platform
- Submit civic complaints
- Provide complaint descriptions
- Add location information
- Upload supporting images
- View submitted complaints
- Track complaint status
- Monitor resolution progress

---

## 🤖 AI Complaint Classification

The AI module analyzes complaint information and automatically determines:

```text
Complaint
    ↓
Text Processing
    ↓
AI/ML Analysis
    ↓
Category Detection
    ↓
Severity Detection
    ↓
Priority Assignment
```

Example:

```text
Input:
"Large pothole near the main road causing accidents."

AI Classification:

Category  : Road Damage
Severity  : High
Priority  : Urgent
```

---

## 🚨 Priority Management

Complaints can be prioritized based on factors such as:

- Severity
- Type of civic issue
- Potential public impact
- Location
- Number of affected citizens
- Urgency

Example priority levels:

| Priority | Description |
|---|---|
| 🔴 Critical | Immediate public safety concern |
| 🟠 High | Requires quick attention |
| 🟡 Medium | Should be addressed soon |
| 🟢 Low | Can be handled through normal workflow |

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      Citizen        │
                    │   Web Application   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    React Frontend   │
                    └──────────┬───────────┘
                               │
                         REST API
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI        │
                    │      Backend        │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       ┌────────────┐   ┌─────────────┐   ┌─────────────┐
       │ AI / ML    │   │ Complaint   │   │ User/Auth   │
       │ Engine     │   │ Management  │   │ Module      │
       └─────┬──────┘   └──────┬──────┘   └─────────────┘
             │                 │
             └────────┬────────┘
                      ▼
              ┌───────────────┐
              │   Database    │
              └───────────────┘
```

---

# 🔄 Complaint Processing Workflow

```text
Citizen submits complaint
          │
          ▼
Complaint validation
          │
          ▼
Text / Image processing
          │
          ▼
AI classification
          │
          ▼
Category identification
          │
          ▼
Severity estimation
          │
          ▼
Priority assignment
          │
          ▼
Complaint stored in database
          │
          ▼
Assigned to responsible authority
          │
          ▼
Status updates
          │
          ▼
Complaint resolved
```

---

# 🧠 AI/ML Component

The AI component is responsible for transforming unstructured citizen complaints into structured information.

### Example

Input:

```text
"The street light has not been working for the last
two weeks and the area becomes completely dark at night."
```

Output:

```json
{
  "category": "Streetlight",
  "severity": "High",
  "priority": "High"
}
```

### AI Pipeline

```text
Raw Complaint
      ↓
Text Cleaning
      ↓
Tokenization / Feature Extraction
      ↓
Model Processing
      ↓
Classification
      ↓
Severity Analysis
      ↓
Priority Generation
```

The architecture can be extended to support advanced NLP models, LLMs, image classification, sentiment analysis, and multimodal complaint analysis.

---

# 🧩 Main Modules

### 1. Authentication Module

Handles:

- User registration
- Login
- Authentication
- Role-based access

Possible roles:

```text
Citizen
Admin
Authority
```

---

### 2. Complaint Management Module

Responsible for:

- Creating complaints
- Updating complaints
- Retrieving complaints
- Deleting complaints where permitted
- Tracking complaint status

---

### 3. AI Analysis Module

Responsible for:

- Complaint classification
- Severity detection
- Priority prediction
- Text analysis
- Future AI-powered recommendations

---

### 4. Location Module

Complaints can be associated with geographic information.

Example:

```text
Latitude  : 17.xxxxx
Longitude : 78.xxxxx
Area      : Local Area
```

This enables future development of:

- Complaint heatmaps
- Area-wise analytics
- Geographic prioritization
- Hotspot detection

---

### 5. Admin Dashboard

Authorities can:

- View complaints
- Filter complaints
- Search complaints
- Check priority
- Assign complaints
- Update status
- Monitor resolution progress
- Analyze complaint trends

---

# 📊 Complaint Lifecycle

```text
SUBMITTED
    ↓
AI ANALYZED
    ↓
CLASSIFIED
    ↓
ASSIGNED
    ↓
IN PROGRESS
    ↓
RESOLVED
    ↓
CLOSED
```

Example status values:

```text
Pending
Analyzing
Assigned
In Progress
Resolved
Closed
Rejected
```

---

# 🗂️ Project Structure

```text
AI-Civic-Complaint-System/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── ai/
│   │   └── database/
│   │
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── App.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── ml/
│   ├── datasets/
│   ├── notebooks/
│   ├── preprocessing/
│   ├── training/
│   └── models/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   └── screenshots/
│
├── tests/
│
├── .gitignore
├── README.md
└── LICENSE
```

> The exact folder structure may vary depending on the implementation.

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Backend & AI development |
| **FastAPI** | REST API development |
| **React** | Frontend application |
| **Machine Learning** | Complaint classification |
| **NLP** | Text analysis |
| **SQL/Database** | Data persistence |
| **REST API** | Frontend-backend communication |
| **Git & GitHub** | Version control |

---

# 🔌 API Design

Example API structure:

```text
POST   /api/auth/register
POST   /api/auth/login

POST   /api/complaints
GET    /api/complaints
GET    /api/complaints/{id}
PUT    /api/complaints/{id}
DELETE /api/complaints/{id}

POST   /api/complaints/{id}/analyze

GET    /api/admin/dashboard
GET    /api/admin/analytics

PUT    /api/complaints/{id}/status
```

---

# 📡 Example Complaint Request

```json
{
  "title": "Road Pothole",
  "description": "Large pothole near the main road",
  "location": "Main Road",
  "latitude": 17.385,
  "longitude": 78.486
}
```

### Example AI Response

```json
{
  "category": "Road Damage",
  "severity": "High",
  "priority": "High",
  "status": "Pending"
}
```

---

# 🗄️ Database Design

A simplified complaint record can contain:

| Field | Description |
|---|---|
| `complaint_id` | Unique complaint identifier |
| `user_id` | Citizen identifier |
| `title` | Complaint title |
| `description` | Complaint description |
| `category` | AI-generated category |
| `severity` | Severity level |
| `priority` | Priority level |
| `latitude` | Geographic latitude |
| `longitude` | Geographic longitude |
| `status` | Current complaint status |
| `created_at` | Submission time |
| `updated_at` | Last update |

---

# 🚀 Installation & Setup

## 1. Clone Repository

```bash
git clone https://github.com/YOUR-USERNAME/AI-Civic-Complaint-System.git

cd AI-Civic-Complaint-System
```

---

## 2. Backend Setup

```bash
cd backend

python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start FastAPI

```bash
uvicorn app.main:app --reload
```

Backend will be available at:

```text
http://127
