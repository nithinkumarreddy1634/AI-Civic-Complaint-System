# System Screenshots & Visual Presentation Guide

This catalog documents the **18 core user interfaces and decision-support panels** in the **AI Civic Complaint System**, detailing layout components, data visualizations, aesthetic design choices, and user flow states.

---

## 1. Landing Page (`/`)
- **Theme**: Dark civic operations aesthetic (`#0B0F19`) with purple and cyan ambient lighting.
- **Hero Banner**: "Verify, Assess & Prioritize Civic Complaints with AI".
- **Key Elements**:
  - Live technical performance counters (91.4% mAP@50, 1.42s latency, 210 passing tests).
  - Quick action buttons ("Submit a Complaint", "Admin & Citizen Login").
  - 4-step civic workflow overview cards (Snap & Report, AI Analysis, Prioritization, Resolution).

---

## 2. Authentication Screen (`/login`, `/register`)
- **Layout**: Centered glassmorphic card on dark navy canvas.
- **Form Controls**:
  - Email and password input fields with real-time client-side regex validation.
  - Role switcher button ("Citizen Portal" vs "Municipal Admin").
  - Test account credentials quick-fill buttons for evaluator demonstrations.

---

## 3. Citizen Dashboard (`/complaints`)
- **Header**: Incident status filter tabs (`All`, `Processing`, `Verified`, `Assigned`, `In Progress`, `Resolved`, `Rejected`) with live count badges.
- **Grid View**: 3-column responsive card layout displaying thumbnail photographs, category pills, priority badges, locality landmarks, and relative timestamps.
- **Quick Action**: "Report Issue" purple floating button.

---

## 4. Complaint Submission Form (`/complaints/new`)
- **Layout**: Structured multi-input workflow:
  1. Category selector dropdown covering 7 civic classes.
  2. Multi-line detailed description with live character counter.
  3. Optional landmark / street address text field.
  4. Drag-and-drop evidence image upload zone.
  5. Interactive Leaflet GPS map with draggable marker.

---

## 5. Image Upload & Audit Zone
- **Visuals**: Dashed purple border upload box with drag-and-drop event feedback.
- **Client Validation**: Instant checks for allowed MIME types (JPEG, PNG) and file size ceiling (10 MB).
- **Preview Thumbnail**: High-resolution preview with "Replace Image" and "Remove" options.

---

## 6. Real-Time AI Processing Pipeline Tracker
- **Visuals**: Animated step-by-step progress timeline displaying current analysis state:
  - `Image Quality Audit` $\rightarrow$ `YOLO Detection` $\rightarrow$ `NLP Consistency` $\rightarrow$ `Severity` $\rightarrow$ `Duplicate Check` $\rightarrow$ `Priority Scoring`.
- **States**: Color-coded transitions (`Completed` in emerald green, `Processing` with spinner, `Pending` in slate, `Failed` in rose).

---

## 7. AI Verification Panel
- **Verification Score**: Prominent numerical score (e.g., $94/100$) and status badge (`VERIFIED`).
- **Audit Metrics**:
  - Detection Confidence score bar ($91.4\%$).
  - Image Quality audit bar ($96\%$) with blur variance and brightness readouts.
  - Text-Image Cross-Modal Consistency score bar ($88\%$).
- **Reasoning Tags**: Pill badges explaining affirmative verification evidence.

---

## 8. Damage Severity Assessment Panel
- **Overall Severity**: Large font gauge ($84/100$ - `CRITICAL`).
- **3-Factor Risk Breakdown**:
  - Safety Risk bar ($90/100$) in rose.
  - Infrastructure Impact bar ($80/100$) in orange.
  - Public Impact bar ($85/100$) in purple.
- **Evidence List**: Geometric defect area percentage, proximity to traffic lanes.

---

## 9. Duplicate Detection Card
- **Status Badge**: `NEW` (No duplicate), `POSSIBLE_DUPLICATE`, or `LIKELY_DUPLICATE`.
- **Similarity Gauge**: Fused similarity percentage bar combining spatial Haversine distance, visual ResNet50 embedding similarity, and text cosine similarity.
- **Linked Records**: Direct clickable links to existing parent complaint tickets within $500\text{ m}$.

---

## 10. Intelligent Priority Score Card
- **Score Meter**: Circular SVG progress ring displaying calculated score ($87.5/100$).
- **Tier Badge**: Pulsing red `URGENT` badge.
- **Factor Attribution Table**:
  - Severity Weight (35%)
  - Safety Hazard Weight (25%)
  - Public Exposure Weight (15%)
  - Frequency Boost (+12.0 points)

---

## 11. Complaint Details Master View (`/complaints/:id`)
- **Two-Column Responsive Grid**:
  - Left Column: Photographic evidence with YOLO bounding box overlay, street address, and GPS coordinates.
  - Right Column: AI verification scores, severity cards, duplicate cards, and status timeline.

---

## 12. Admin Command Dashboard (`/admin`)
- **Top Welcome Hero**: Urban roadway photo backdrop with greeting and quick navigation button.
- **4 KPI Stat Cards**:
  - Total Complaints: `248` (+12%) with purple sparkline.
  - Pending Review: `28` (+8%) with amber sparkline.
  - In Progress: `86` (+15%) with cyan sparkline.
  - Resolved: `93` (+22%) with emerald sparkline.
- **Middle Section**: Recent verified complaints list alongside the Live GIS Incident Map.
- **Bottom Section**: Category Donut Chart (`248 Total` center hole), Monthly Trendline Chart, and AI Engine accuracy telemetry.

---

## 13. Admin Complaint Management Table (`/admin/complaints`)
- **Controls**: Full-text search bar, category dropdown, priority multi-select, and status tabs.
- **Table Columns**: Checkbox, ID (`#CIV-XXXX`), Category, Locality, Priority, Status, AI Confidence, Created Date, Actions menu.
- **Batch Operations**: "Assign Department", "Mark as In Progress", "Export CSV".

---

## 14. Admin Complaint Evidence Review (`/admin/complaints/:id`)
- **Specialized Features**:
  - Raw YOLO bounding box coordinate coordinates inspector `[xmin, ymin, xmax, ymax]`.
  - Manual override toggle allowing administrators to correct AI classification or priority.
  - Department reassignment dropdown with municipal routing justification notes.

---

## 15. Full-Screen Interactive GIS Incident Map (`/admin/map`)
- **Basemap**: Dark CartoDB styling with high-contrast road corridors.
- **Pins**: Glowing markers colored by Priority (Red for Urgent, Orange for High, Amber for Medium, Slate for Low).
- **Interactive Popup**: Thumbnail preview, Incident ID, Category, Address, and "View Details $\rightarrow$" button.

---

## 16. Municipal Analytics & Workload Portal (`/admin/analytics`)
- **Visualizations**:
  - Complaints by Department workload bar chart.
  - Average resolution turnaround time by category (Days).
  - Monthly defect seasonality comparison.
  - AI Verification accuracy & false positive distribution.

---

## 17. Department Assignment Modal
- **Inputs**: Department selector (Roads & Highway, Solid Waste, Electrical, Water Board).
- **AI Recommendation Callout**: Displays AI recommended agency with confidence score (e.g., "AI Suggests: Roads & Highway Authority (94.2%)").
- **Notes Field**: Instructions for field engineers and contractors.

---

## 18. Status Audit Timeline
- **Visuals**: Vertical connecting line with step icons.
- **Milestones**:
  - `SUBMITTED`: Logged by citizen.
  - `VERIFIED`: Confirmed by YOLO & AI pipeline.
  - `ASSIGNED`: Routed to department.
  - `IN_PROGRESS`: Field crew dispatched.
  - `RESOLVED`: Repair completed with closing remarks.
