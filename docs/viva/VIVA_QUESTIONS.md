# Viva Questions, Answers & Project Defense Guide

**Project Title:** AI-Powered Civic Infrastructure Complaint Verification and Prioritization System Using Computer Vision  
**Degree:** Bachelor of Technology in Computer Science & Engineering  

---

## Part 1: General Project Questions

### Q1: What is your project and what problem does it solve?
**Answer:**  
Our project is an AI-assisted civic infrastructure complaint management and prioritization platform. In modern cities, thousands of citizens report issues like potholes, garbage accumulation, broken streetlights, and ruptured water pipelines. Currently, municipal bodies rely on human clerks to manually inspect photos, filter duplicates, and route complaints, creating severe triage backlogs. Our system automates this triage within 1.5 seconds using computer vision, cross-modal verification, automated severity scoring, duplicate detection, and intelligent departmental routing, while keeping municipal administrators in full control.

### Q2: What is the main innovation of your system?
**Answer:**  
The main innovation is the **multi-modal 10-stage decision-support pipeline**. Rather than treating complaint management as a simple database CRUD app or a standalone image classifier, our system fuses computer vision (YOLOv8), image quality metrics, natural language text analysis, geospatial proximity (Haversine formula), visual embedding similarity (ResNet50), and multi-criteria decision analysis (MCDA) to produce an objective, explainable Priority Score and an automated Department Recommendation.

### Q3: Why did you choose this project?
**Answer:**  
Civic infrastructure maintenance is a critical public safety and governance challenge worldwide. We chose this project because it bridges academic research in deep learning and computer vision with practical municipal e-governance, demonstrating how AI can improve urban safety and resource allocation in real-world smart cities.

---

## Part 2: AI & Machine Learning Questions

### Q4: Why did you choose YOLO instead of two-stage detectors like Faster R-CNN?
**Answer:**  
YOLO (You Only Look Once) is a single-stage object detector that processes the entire image in a single neural network forward pass, predicting bounding boxes and class probabilities simultaneously. We chose YOLOv8 because:
1. **Inference Latency**: YOLOv8s runs in $\approx 18\text{ ms}$ on GPU and $\approx 140\text{ ms}$ on CPU, whereas Faster R-CNN requires $300 - 600\text{ ms}$ due to separate Region Proposal Networks (RPN).
2. **Anchor-Free Architecture**: YOLOv8 employs an anchor-free detection head, which reduces hyperparameter tuning and improves localization for irregular shapes like asphalt potholes and scattered garbage.
3. **mAP Performance**: Fine-tuned YOLOv8s achieves a 91.4% mAP@50 on our civic defect dataset.

### Q5: What is Intersection over Union (IoU)?
**Answer:**  
Intersection over Union (IoU) measures the overlap between the ground truth bounding box ($A$) and the predicted bounding box ($B$):
$$\text{IoU} = \frac{\text{Area}(A \cap B)}{\text{Area}(A \cup B)}$$
An IoU of $1.0$ indicates perfect alignment, while an IoU $\ge 0.5$ is the standard threshold for considering a detection as a True Positive in mAP@50 evaluation.

### Q6: What is mAP (mean Average Precision)?
**Answer:**  
Average Precision (AP) is the area under the Precision-Recall curve for a single class. **mAP** is the mean of Average Precisions calculated across all classes:
$$\text{mAP} = \frac{1}{N} \sum_{i=1}^N \text{AP}_i$$
mAP@50 evaluates detections at an IoU threshold of 0.50, which is standard for object detection benchmarking.

### Q7: What are Precision, Recall, and the F1 Score?
**Answer:**  
- **Precision**: $\frac{\text{TP}}{\text{TP} + \text{FP}}$ — Measures how many of the detected defects are actual defects (low false alarm rate).
- **Recall**: $\frac{\text{TP}}{\text{TP} + \text{FN}}$ — Measures how many of the actual physical defects the model successfully detected.
- **F1 Score**: The harmonic mean of Precision and Recall:
  $$\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

## Part 3: Computer Vision & Preprocessing Questions

### Q8: How do you detect low-quality or unusable images?
**Answer:**  
Before passing images to the neural network, our Image Quality Auditor performs three mathematical checks using OpenCV:
1. **Blur Detection**: Calculates the variance of the Laplacian operator:
   $$\sigma^2 = \text{Var}(\nabla^2 I)$$
   If $\sigma^2 < 100$, the image is flagged as blurry.
2. **Brightness Exposure**: Computes mean grayscale intensity $\mu_I$. If $\mu_I < 40$ (underexposed/night) or $\mu_I > 225$ (overexposed/whiteout), it is flagged.
3. **Contrast Analysis**: Computes standard deviation of pixel intensities $\sigma_I$. Low contrast ($\sigma_I < 25$) is flagged.

### Q9: What is a bounding box and how is it represented?
**Answer:**  
A bounding box is a rectangular envelope that encloses a detected object. In our system, YOLO outputs coordinates in normalized or pixel coordinates as $[x_{min}, y_{min}, x_{max}, y_{max}]$, along with a class integer and a confidence probability $c \in [0, 1]$.

### Q10: How do you handle multiple defects in a single photograph?
**Answer:**  
YOLO naturally predicts multiple bounding boxes per image. If an image contains both a pothole and an open manhole, our pipeline localizes both, identifies the primary defect based on maximum confidence and area, and elevates the severity score to account for multi-hazard clusters.

---

## Part 4: Backend & Database Questions

### Q11: Why did you choose FastAPI over Django or Flask?
**Answer:**  
1. **Asynchronous Concurrency**: FastAPI is built on Starlette and ASGI, supporting Python `async/await` natively for non-blocking I/O during heavy image processing and database calls.
2. **High Performance**: Independent benchmarks rank FastAPI among the fastest Python web frameworks, comparable to NodeJS and Go.
3. **Automatic OpenAPI/Swagger Documentation**: Generates interactive API docs automatically from Pydantic schemas.
4. **Pydantic v2 Type Safety**: Enforces strict schema validation at the HTTP boundary, eliminating malformed request payloads.

### Q12: Why PostgreSQL and SQLAlchemy?
**Answer:**  
PostgreSQL offers robust ACID guarantees, excellent concurrency with MVCC, and superior JSONB support for storing variable AI detection payloads. SQLAlchemy 2.0 provides an enterprise ORM with clean migration tracking (Alembic) and strict foreign-key relationship integrity.

### Q13: How is user authentication and security handled?
**Answer:**  
We implement stateless JWT (JSON Web Token) authentication:
- Passwords are encrypted using salted bcrypt hashing.
- Protected endpoints require an `Authorization: Bearer <token>` header verified by FastAPI dependencies.
- Role-Based Access Control (RBAC) enforces strict authorization separation between `citizen` and `admin` roles.
- File uploads are validated for MIME signatures and sanitized using `os.path.basename` to prevent path traversal attacks.

---

## Part 5: Frontend Questions

### Q14: Why React 19 and Vite?
**Answer:**  
Vite provides an optimized ES-module build environment with instantaneous Hot Module Replacement (HMR) and fast sub-second production bundling. React 19 offers declarative component architecture, efficient virtual DOM diffing, and seamless state management.

### Q15: How does the frontend render maps and GIS data?
**Answer:**  
We utilize Leaflet via `react-leaflet`. Map markers are dynamically styled based on complaint priority (e.g., pulsing red for `URGENT`, orange for `HIGH`). Clicking a marker opens a responsive popup card with incident photos and quick triage actions.

---

## Part 6: AI Pipeline & Decision Support

### Q16: How do you detect duplicate complaints?
**Answer:**  
We employ a multi-modal duplicate detection algorithm:
1. **Spatial Filtering**: Uses the Haversine formula to search for active complaints within a $500\text{ m}$ radius.
2. **Visual Feature Similarity**: Extracts 2048-dimensional feature vectors using ResNet50 and calculates cosine similarity:
   $$\text{CosSim}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$$
3. **Text Semantic Similarity**: Computes cosine similarity across sentence embeddings.
4. **Fused Duplicate Score**: Combines spatial, visual, and textual metrics. Complaints with score $\ge 0.82$ are classified as `LIKELY_DUPLICATE`. Importantly, duplicate reports are linked rather than silently deleted, allowing the system to track reporting frequency.

### Q17: How is the Priority Score calculated?
**Answer:**  
The Priority Score is calculated using a multi-attribute utility formula:
$$\text{Priority Score} = w_1 \cdot \text{Severity} + w_2 \cdot \text{SafetyHazard} + w_3 \cdot \text{InfrastructureImpact} + w_4 \cdot \text{PublicImpact} + w_5 \cdot \text{Frequency} + \Delta_{escalate}$$
- Severity ($35\%$): Determined by defect size and detection confidence.
- Safety Hazard ($25\%$): Baseline hazard rating of the category (e.g., Open Manhole = 95, Pothole = 80).
- Public Impact ($15\%$): Traffic/pedestrian volume exposure.
- Frequency ($10\%$): Boost applied when multiple citizens report the same defect.
- Escalation ($\Delta$): Time-decay penalty applied to unresolved complaints.

---

## Part 7: Project Defense & Critical Challenges

### Q18: Why is this better than a standard complaint application?
**Answer:**  
A standard complaint app is merely a digital mailbox—it collects tickets but does nothing to verify or prioritize them. Our system actively:
1. Verifies whether the image is genuine and in-domain within 1.5 seconds.
2. Quantifies objective physical severity rather than relying on biased citizen self-ratings.
3. Automatically identifies duplicate reports for the same incident.
4. Routes work orders directly to the correct municipal agency.

### Q19: Can the AI make mistakes? How do you prevent incorrect decisions?
**Answer:**  
Yes, no computer vision model is 100% accurate. We prevent incorrect municipal actions through three design safeguards:
1. **Confidence Thresholds**: Complaints with confidence between $40\% - 70\%$ are routed to `NEEDS_REVIEW` rather than auto-verified.
2. **Explainable Factor Attribution**: The UI never outputs a naked score; it provides detailed breakdown tags (e.g., "Large detected area", "High safety risk", "Category agreement").
3. **Human-in-the-Loop Authority**: Municipal administrators retain full authority to override AI classifications, change priority levels, or reassign departments.

### Q20: What happens if two citizens photograph the same pothole from different angles?
**Answer:**  
Our multi-modal duplicate engine handles this specifically:
- Even if angles differ, their GPS coordinates will be within $15 - 30\text{ meters}$ (Haversine score $> 0.95$).
- Both images will detect the class `pothole`.
- The system flags the second submission as `LIKELY_DUPLICATE`, links it to the primary ticket, and applies a **Frequency Boost** to increase the primary ticket's priority.

### Q21: How would this system scale to an entire metropolitan city with 10 million residents?
**Answer:**  
1. **Asynchronous Task Workers**: Decouple HTTP ingestion from AI inference using Celery or Redis queues.
2. **Spatial Partitioning**: Index complaints using PostGIS spatial indexing (`ST_DWithin` with GiST spatial indexes).
3. **Model Quantization**: Deploy TensorRT or ONNX Runtime quantized YOLO models running on GPU inference clusters (e.g., Triton Inference Server).
4. **Horizontal Pod Autoscaling**: Scale containerized FastAPI workers in Kubernetes based on CPU/GPU utilization.
