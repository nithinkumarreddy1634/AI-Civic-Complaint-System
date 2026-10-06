# 5–10 Minute Live Demonstration Script

**Project Title:** AI-Powered Civic Infrastructure Complaint Verification and Prioritization System Using Computer Vision  
**Role Assignments:**
- **Presenter 1:** Demonstrates Citizen submission workflow, AI processing status, and mobile views.
- **Presenter 2:** Demonstrates Administrator console, GIS mapping, AI evidence inspector, and work order dispatch.

---

## Pre-Demo Checklist & Setup

1. **Backend Server**: Running at `http://localhost:8000` (`python -m uvicorn backend.app.main:app`).
2. **Frontend App**: Running at `http://localhost:5173` (`npm run dev`).
3. **Demo Credentials**:
   - Citizen: `citizen@example.com` / `password123`
   - Administrator: `admin@example.com` / `adminpassword123`
4. **Demo Assets**: Sample civic defect images located in `demo/` folder:
   - `demo/pothole/crater_pothole.jpg`
   - `demo/garbage/overflowing_bin.jpg`
   - `demo/water_leakage/pipe_burst.jpg`

---

## Step-by-Step Demonstration Walkthrough

### Part 1: Context & Citizen Complaint Submission (Minutes 0:00 – 3:00)

1. **Problem Intro (30s)**:
   - "Good morning. In most cities, citizen complaints sit in backlogs because human clerks have to manually inspect each photo. We demonstrate how our AI pipeline automates this triage within 1.5 seconds."
2. **Landing Page**:
   - Navigate to `http://localhost:5173`.
   - Point out the dark civic theme, live performance metrics (91.4% mAP50, 1.42s latency, 210 passing tests), and clear value proposition.
3. **Citizen Login**:
   - Click **Login** $\rightarrow$ enter `citizen@example.com` / `password123`.
   - Redirects to Citizen portal.
4. **Initiate Complaint**:
   - Click **Report Civic Issue** or **Submit Complaint**.
   - Select Category: `Pothole`.
   - Description: `Deep crater pothole near metro pillar 142 causing major traffic congestion and wheel damage.`
   - Street Address: `MG Road, Central Junction, Ward 84`.
5. **Upload Realistic Evidence**:
   - Drag and drop `demo/pothole/crater_pothole.jpg` into the evidence upload box.
   - Show image preview and instant client-side size/type validation.
6. **Pin Location**:
   - Click on the interactive Leaflet map to pin location (coordinates: $12.9716, 77.5946$).
7. **Submit & Trigger AI Pipeline**:
   - Click **Submit Complaint**.
   - Show the success modal with unique Incident ID `#CIV-1024`.
   - Click **Track AI Verification**.

---

### Part 2: AI Processing & Decision-Support Inspection (Minutes 3:00 – 5:30)

8. **AI Verification Timeline**:
   - Show the live progress bar transition through the pipeline stages:
     - Image Quality Audit $\rightarrow$ YOLO Detection $\rightarrow$ NLP Consistency $\rightarrow$ Severity Assessment $\rightarrow$ Duplicate Detection $\rightarrow$ Priority Scoring.
9. **YOLO Defect Visualization**:
   - Inspect the Detection Overlay:
     - Show the green/purple bounding box around the detected defect.
     - Note the badge: `POTHOLE (91.4% Confidence)`.
     - Highlight that bounding boxes are generated directly by the computer vision model.
10. **Explainable AI Breakdown**:
    - **Verification Card**: Show the 4-part score (Image Quality 94%, Detection Confidence 91%, Text-Image Consistency 88%, Civic Relevance 96%).
    - **Severity Assessment Card**: Point to overall severity score ($84/100$) and explain contributing factors:
      - Relative defect footprint on asphalt.
      - Structural hazard weighting.
      - Public traffic exposure index.
    - **Intelligent Priority Card**: Show final score ($87/100$ - `URGENT`) with factor breakdown (Severity 35%, Safety Risk 25%, Public Footfall 15%, Frequency Boost +12).
    - **Duplicate Detection**: Note the classification: `NEW` (no spatial duplicate within $500\text{ m}$).
    - **Department Recommendation**: Note target agency: `Roads & Highway Authority (94% confidence)`.

---

### Part 3: Administrator Operations Console & Resolution (Minutes 5:30 – 8:00)

11. **Admin Console Navigation**:
    - Open an incognito tab or log out and log in as `admin@example.com` / `adminpassword123`.
    - Landing on `/admin` reveals the dark-themed command center.
12. **Command Dashboard Telemetry**:
    - Show 4 KPI stat cards with purple/amber/cyan/emerald wavy sparklines (248 Total, 28 Pending Review, 86 In Progress, 93 Resolved).
    - Show the **Complaints by Category Donut Chart** with `248 Total` in the center hole.
    - Show the **Monthly Trend Chart** comparing Submissions vs Resolutions.
13. **Live GIS Incident Map**:
    - Focus on the Bangalore map. Point out the glowing red marker at MG Road.
    - Click the marker: popup shows `#CIV-1024`, `Pothole`, `URGENT`, `In Progress`.
    - Click **View Details $\rightarrow$** to enter administrative evidence review.
14. **Administrative Action & Dispatch**:
    - Show the Admin can view identical AI evidence with raw bounding box coordinates.
    - Click **Confirm Department Routing** $\rightarrow$ routes to `Roads & Highway Authority`.
    - Change Status from `SUBMITTED` $\rightarrow$ `ASSIGNED` with note: *"Field repair unit dispatched to MG Road junction."*
    - Update Status $\rightarrow$ `IN_PROGRESS` $\rightarrow$ `RESOLVED`.
15. **Audit Trail Verification**:
    - Point to the immutable **Status Timeline** at the bottom of the complaint:
      - Records exact timestamps, status transitions, and user IDs.

---

### Part 4: Conclusion & Viva Transition (Minutes 8:00 – 10:00)

16. **Wrap-up Summary (30s)**:
    - "In under 8 minutes, we demonstrated a complete end-to-end incident lifecycle: from citizen submission and sub-second multi-modal AI verification, to administrative GIS triage and verified departmental resolution. We are ready to answer your questions."
