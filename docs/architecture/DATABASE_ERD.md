# Database Entity-Relationship (ER) Architecture

## Overview

The database uses a normalized relational architecture designed in PostgreSQL (with SQLite compatibility for local test isolation). Foreign key relationships maintain referential integrity, while cascading rules ensure consistent audit records across all complaints and automated AI analytical records.

```mermaid
erDiagram
    USERS ||--o{ COMPLAINTS : "submits"
    USERS ||--o{ STATUS_HISTORIES : "triggers_change"
    USERS ||--o{ DEPARTMENT_ASSIGNMENTS : "assigned_by"
    
    COMPLAINTS ||--o| AI_ANALYSES : "evaluated_by"
    COMPLAINTS ||--o| SEVERITY_ASSESSMENTS : "evaluated_by"
    COMPLAINTS ||--o| PRIORITY_ASSESSMENTS : "scored_by"
    COMPLAINTS ||--o{ STATUS_HISTORIES : "has_history"
    COMPLAINTS ||--o{ DEPARTMENT_ASSIGNMENTS : "routed_to"
    COMPLAINTS ||--o{ DUPLICATE_LINKS : "primary_complaint"
    COMPLAINTS ||--o{ DUPLICATE_LINKS : "duplicate_complaint"
    
    DEPARTMENTS ||--o{ DEPARTMENT_ASSIGNMENTS : "receives_work_order"
    DUPLICATE_CLUSTERS ||--o{ DUPLICATE_LINKS : "groups"

    USERS {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        string role "citizen | admin"
        boolean is_active
        timestamp created_at
    }

    COMPLAINTS {
        uuid id PK
        uuid user_id FK
        string title
        string category
        text description
        string image_url
        float latitude
        float longitude
        string address
        string status "SUBMITTED | VERIFIED | NEEDS_REVIEW | ASSIGNED | IN_PROGRESS | RESOLVED | REJECTED"
        string priority_level "LOW | MEDIUM | HIGH | URGENT"
        timestamp created_at
        timestamp updated_at
    }

    AI_ANALYSES {
        uuid id PK
        uuid complaint_id FK,UK
        string status "VERIFIED | NEEDS_REVIEW | REJECTED"
        float confidence_score
        string detected_class
        json detections
        json image_quality
        json text_analysis
        json explanations
        timestamp created_at
    }

    SEVERITY_ASSESSMENTS {
        uuid id PK
        uuid complaint_id FK,UK
        float severity_score
        string severity_level "LOW | MEDIUM | HIGH | CRITICAL"
        float safety_risk_score
        float infrastructure_impact_score
        float public_impact_score
        json evidence_factors
        timestamp created_at
    }

    PRIORITY_ASSESSMENTS {
        uuid id PK
        uuid complaint_id FK,UK
        float priority_score
        string priority_level "LOW | MEDIUM | HIGH | URGENT"
        float base_score
        float frequency_boost
        float time_decay_boost
        json contributing_factors
        timestamp created_at
    }

    DEPARTMENTS {
        uuid id PK
        string name UK
        string code UK
        string contact_email
        text description
        boolean is_active
    }

    DEPARTMENT_ASSIGNMENTS {
        uuid id PK
        uuid complaint_id FK
        uuid department_id FK
        uuid assigned_by_user_id FK
        text notes
        timestamp assigned_at
    }

    STATUS_HISTORIES {
        uuid id PK
        uuid complaint_id FK
        string old_status
        string new_status
        uuid changed_by_user_id FK
        text comment
        timestamp changed_at
    }

    DUPLICATE_CLUSTERS {
        uuid id PK
        string primary_category
        float centroid_latitude
        float centroid_longitude
        timestamp created_at
    }

    DUPLICATE_LINKS {
        uuid id PK
        uuid cluster_id FK
        uuid primary_complaint_id FK
        uuid duplicate_complaint_id FK
        float similarity_score
        float spatial_distance_meters
        string duplicate_status "NEW | POSSIBLE_DUPLICATE | LIKELY_DUPLICATE"
        timestamp linked_at
    }
```

---

## Schema Highlights & Indexes

1. **High-Performance Query Indexing**:
   - `complaints (user_id)`: Accelerates citizen portal personal complaint queries.
   - `complaints (status, priority_level)`: Optimizes admin dashboard filtering and sorting.
   - `complaints (latitude, longitude)`: Spatial indexing for radius candidate search.
2. **Auditability**:
   - Every status transition from creation to closure writes an immutable record to `status_histories`.
3. **Multi-Modal Evidence JSON**:
   - `ai_analyses.detections` preserves complete YOLO bounding box arrays `[x1, y1, x2, y2, confidence, class]`, ensuring forensic verifiability.
