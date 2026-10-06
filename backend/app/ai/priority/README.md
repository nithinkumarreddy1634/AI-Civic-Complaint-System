# AI-Powered Civic Complaint Prioritization Engine (Phase 7)

## 1. System Overview

The **Intelligent Complaint Prioritization Engine** synthesizes verified multi-modal evidence from Computer Vision, NLP, and geospatial clustering into an explainable, deterministic priority score (0–100). The engine acts as an objective triage assistant for municipal public works dispatchers and emergency response teams.

Instead of recomputing raw inference, the engine ingests and fuses established artifacts from upstream modules:
- **Phase 4 (AI Verification)**: Verification status (`VERIFIED`, `NEEDS_REVIEW`, `REJECTED`) and detection confidence.
- **Phase 5 (AI Severity & Damage Analysis)**: Physical severity score, safety risk, infrastructure impact, and public disruption.
- **Phase 6 (Duplicate Clustering)**: Duplicate cluster group membership, cumulative citizen report frequency, and similarity metrics.
- **Geospatial Impact**: Arterial road proximity, school/hospital zone proximity, and graceful weight redistribution for missing coordinates.
- **Temporal Escalation**: Sublinear aging adjustment for prolonged unresolved civic hazards.

---

## 2. Mathematical Formulation

### 2.1 Multi-Criteria Weighted Fusion

Each available dimension $i \in \mathcal{A}$ has a nominal weight $w_i$ configured in `backend/config/priority.yaml`. The default nominal weights are:

| Factor | Key | Nominal Weight ($w_i$) | Normalization |
| :--- | :--- | :--- | :--- |
| **Physical Severity** | `severity` | 0.25 | 0.0 – 100.0 (Phase 5) |
| **Public Safety Risk** | `safety_risk` | 0.25 | 0.0 – 100.0 (Phase 5) |
| **Infrastructure Impact** | `infrastructure_impact` | 0.15 | 0.0 – 100.0 (Phase 5) |
| **Public Disruption Impact** | `public_impact` | 0.15 | 0.0 – 100.0 (Phase 5) |
| **Complaint Frequency** | `complaint_frequency` | 0.10 | 0.0 – 100.0 (Sublinear scaling) |
| **Location Impact** | `location_impact` | 0.05 | 0.0 – 100.0 (GIS / baseline) |
| **Verification Confidence**| `verification_confidence`| 0.05 | 0.0 – 100.0 (Phase 4) |
| **Total** | | **1.00** | |

### 2.2 Dynamic Missing-Data Redistribution

When GPS coordinates are absent, location data cannot be reliably estimated without fabricating unverified POIs. Rather than penalizing rural or non-GPS complaints with 0 points, the engine dynamically normalizes the active weights:

$$W_{\text{active}} = \sum_{j \in \mathcal{A}} w_j$$

$$w'_i = \frac{w_i}{W_{\text{active}}} \quad \forall i \in \mathcal{A}$$

$$\sum_{i \in \mathcal{A}} w'_i = 1.0$$

The base score is then computed as:

$$P_{\text{base}} = \sum_{i \in \mathcal{A}} w'_i \cdot S_i$$

### 2.3 Exact Factor Contribution Tracking

Every factor $i$ produces a contribution $C_i$ measured in composite score points:

$$C_i = w'_i \cdot S_i$$

$$\sum_{i \in \mathcal{A}} C_i = P_{\text{base}}$$

This guarantees mathematical transparency for municipal auditability and dispatcher explainability.

### 2.4 Sublinear Saturating Frequency Curve

To prevent coordinated duplicate flooding or automated spam from unilaterally escalating low-severity issues into critical dispatch tiers, raw citizen report count $N$ is mapped via a concave sublinear piecewise function:

$$S_{\text{freq}}(N) = \begin{cases}
15.0 & N = 1 \\
28.0 & N = 2 \\
40.0 & N = 3 \\
60.0 & N = 5 \\
75.0 & N = 8 \\
85.0 & N = 10 \\
95.0 & N = 15 \\
100.0 & N \ge 20 \text{ (Saturation Cap)}
\end{cases}$$

For intermediate counts, linear interpolation between adjacent breakpoints is applied.

### 2.5 Temporal Aging Escalation

Unresolved complaints accumulate an aging boost to prevent neglect of persistent medium-severity hazards:

$$E = \min(t_{\text{days}} \times 1.5, 20.0)$$

$$P_{\text{final}} = \min(100.0, \max(0.0, P_{\text{base}} + E))$$

---

## 3. Urgency Tier Classification

| Priority Level | Score Range | Municipal Response Guideline |
| :--- | :--- | :--- |
| **URGENT** | $[90.0, 100.0]$ | Immediate same-day emergency dispatch; severe safety hazard or life-safety risk. |
| **HIGH** | $[70.0, 90.0)$ | Expedited dispatch within 24–48 hours; significant infrastructure disruption. |
| **MEDIUM** | $[40.0, 70.0)$ | Routine municipal workflow queue; scheduled maintenance within standard SLA. |
| **LOW** | $[0.0, 40.0)$ | Low-impact cosmetic or non-critical maintenance; batch-cycle resolution. |

---

## 4. API Endpoints

- `POST /api/ai/priority`: Evaluates priority for a verified complaint, persists results to `priority_analysis`, and appends an entry to `priority_history`.
- `GET /api/ai/priority/queue`: Retrieves paginated, sorted, and filtered triage queues for administrators.
- `GET /api/complaints/{id}/priority`: Returns the current priority assessment and explainable factor breakdown.
- `GET /api/complaints/{id}/priority/history`: Returns full timestamped historical audit log of all priority recalculations.

---

## 5. Civic Decision-Support Notice

> **Notice**: This AI-generated priority score is an explainable decision-support metric designed to assist municipal dispatchers and triage teams; it does not replace professional civil engineering inspection or emergency protocols.
