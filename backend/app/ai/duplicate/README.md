# AI Duplicate Complaint Detection Subsystem

## Overview

The **AI Duplicate Complaint Detection** subsystem identifies whether a newly reported civic infrastructure complaint references an existing, previously reported problem.

It combines multi-modal evidence across four independent dimensions:
1. **Geographic Proximity**: Great-circle separation calculated using the **Haversine formula**.
2. **Visual Resemblance**: Cosine similarity of 512-dimensional convolutional feature embeddings.
3. **Semantic Text Overlap**: Cosine similarity of 384-dimensional subword & category semantic embeddings.
4. **Issue Category Compatibility**: Exact and affinity match evaluation (e.g. pothole $\leftrightarrow$ damaged road).

> [!NOTE]
> **Non-Destructive Incident Management**: Duplicate complaints are never discarded or deleted. Instead, they are aggregated under a **`DuplicateGroup`** with an elected **representative complaint** (chosen by highest verification/severity and report timestamp).

---

## 1. End-to-End Pipeline

```text
New Complaint (Image, GPS, Description, Category)
       ↓
Check Candidate Search Radius (e.g. 500m Bounding Box)
       ↓
Retrieve Active Candidate Complaints
       ↓
Compute Pairwise Multi-Modal Similarities:
├── Haversine Distance & Location Similarity (0.0–1.0)
├── Visual Image Cosine Similarity (0.0–1.0)
├── Text Description Semantic Cosine Similarity (0.0–1.0)
└── Category Compatibility Score (0.0–1.0)
       ↓
Compute Composite Duplicate Score (0–100) & Apply Safety Vetoes
       ↓
Decision: NEW (< 60) | POSSIBLE_DUPLICATE (60–79) | LIKELY_DUPLICATE (>= 80)
       ↓
Group Management:
├── If LIKELY_DUPLICATE: Link to DuplicateGroup & Update Representative
└── If NEW: Track as Independent Incident
```

---

## 2. Mathematical Formulations

### Haversine Distance Formula
For coordinates $(\phi_1, \lambda_1)$ and $(\phi_2, \lambda_2)$ on Earth ($R \approx 6,371,000\text{m}$):
$$\Delta\phi = \phi_2 - \phi_1, \quad \Delta\lambda = \lambda_2 - \lambda_1$$
$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$
$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$
$$d = R \cdot c$$

### Composite Duplicate Score
When geographic coordinates are present:
$$\text{Score} = 100 \times \left(0.30 \cdot S_{\text{loc}} + 0.35 \cdot S_{\text{img}} + 0.20 \cdot S_{\text{txt}} + 0.15 \cdot S_{\text{cat}}\right)$$

When coordinates are missing:
$$\text{Score} = 100 \times \left(0.50 \cdot S_{\text{img}} + 0.30 \cdot S_{\text{txt}} + 0.20 \cdot S_{\text{cat}}\right)$$

### Safety Overrides
* **Distant Separation Override**: If $d > 1,000\text{m}$, the score is capped at $30$ and classified as `NEW` regardless of visual resemblance.
* **Category Conflict Override**: If category similarity is $0.0$ (e.g. streetlight vs garbage), score is capped at $45$ and classified as `NEW`.

---

## 3. Database Schema

* `complaint_embeddings`: Stores versioned 512-dim visual embeddings and 384-dim text semantic embeddings.
* `duplicate_groups`: Tracks cluster metadata, total reports, unique user counts, and representative complaint ID.
* `complaint_duplicate_links`: Many-to-one links associating individual complaints with their parent duplicate cluster.

---

## 4. REST API Endpoints

### `POST /api/ai/duplicates/check`
Evaluates a complaint for duplicates and updates database groups:
* **Request**: `{"complaint_id": "<uuid>", "force_recompute": false}`
* **Response**:
  ```json
  {
    "complaint_id": "c61309f8-45d2-441d-91df-c0bce902cb01",
    "decision": "LIKELY_DUPLICATE",
    "duplicate_score": 88.4,
    "is_duplicate": true,
    "best_match": {
      "complaint_id": "101a09f8-...",
      "distance_meters": 18.5,
      "image_similarity": 0.91,
      "text_similarity": 0.84,
      "category_similarity": 1.0
    },
    "duplicate_group_id": "grp-12-...",
    "representative_complaint_id": "101a09f8-..."
  }
  ```

### `GET /api/complaints/{id}/duplicates`
Retrieves sibling complaints belonging to the same cluster.

---

## 5. Testing

Run all duplicate unit and integration tests:
```powershell
.\venv\Scripts\python.exe -m pytest tests/ai/duplicate -v
```
All tests execute on CPU with zero network dependency.
