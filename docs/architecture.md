# System Architecture

## System Overview Diagram

```text
+-------------------------------------------------------------+
|                     Frontend (React + Vite)                 |
|  +-------------+   +---------------+   +-----------------+  |
|  | Citizen App |   | Admin Portal  |   | Dept Dashboard  |  |
|  +-------------+   +---------------+   +-----------------+  |
+------------------------------+------------------------------+
                               | HTTPS / JSON
+------------------------------v------------------------------+
|                    API Gateway (FastAPI)                    |
|  +--------+ +-------------+ +-----------+ +--------------+  |
|  |  Auth  | | Complaints  | | Analytics | | Users & Roles|  |
|  +--------+ +-------------+ +-----------+ +--------------+  |
+------------------------------+------------------------------+
                               |
+------------------------------v------------------------------+
|                      Service Layer                          |
|  +-------------+   +---------------+   +-----------------+  |
|  | AI Pipeline |   | Duplicate Det |   | Routing Service |  |
|  +-------------+   +---------------+   +-----------------+  |
+------------------------------+------------------------------+
                               |
+------------------------------v------------------------------+
|                    Data Access Layer (ORM)                  |
|                   (SQLAlchemy 2.0 mapped_column)            |
+------------------------------+------------------------------+
                               |
       +-----------------------+-----------------------+
       |                                               |
+------v-------+                                +------v------+
|  PostgreSQL  |                                | Local Files |
| (Relational) |                                | (Images)    |
+--------------+                                +-------------+
```

## Component Descriptions
- **Frontend Layer:** Built with React 18 and Vite. Handles user interaction and presentation.
- **API Gateway Layer:** FastAPI application serving RESTful endpoints. Manages request validation (Pydantic), routing, and security.
- **Service Layer:** Contains business logic for handling complaints, orchestrating ML predictions, determining priorities, and routing to departments.
- **AI Processing Layer:** Computer vision subsystem utilizing YOLO for object detection, alongside rule-based severity scoring.
- **Data Access Layer:** Uses SQLAlchemy 2.0 to interface with PostgreSQL.
- **Storage Layer:** PostgreSQL for structured data and local filesystem (or S3 in future) for media uploads.

## Data Flow Walkthrough
1. Citizen logs in and submits a complaint with an image, location, and description.
2. The frontend sends a multipart request to the FastAPI endpoint.
3. The API validates the request, saves the image, and inserts a `pending` complaint record into the DB.
4. The API asynchronously triggers the AI Processing Layer.
5. The YOLO model analyzes the image, extracts bounding boxes, classes, and confidence scores.
6. The severity algorithm determines impact (e.g., pothole size).
7. Duplicate detection compares location and features with recent complaints.
8. Priority is calculated and the complaint is routed to a department.
9. DB is updated with results. Citizen and Department receive real-time or polled updates.

## Authentication Flow
Uses OAuth2 with Password Flow (Bearer JWT). Passwords hashed using passlib (bcrypt).

## Security Architecture
- JWT-based authentication.
- Role-based authorization at the route level.
- Input validation via Pydantic.
- CORS configured for authorized domains.

## Scalability Considerations
- Stateless API architecture allows horizontal scaling.
- Heavy ML inference can be decoupled into a celery worker / message queue in Phase 3.
- Database indexing on geospatial fields (latitude, longitude) for fast duplicate detection.

## Technology Justification
- **FastAPI:** High performance, built-in async support, automatic OpenAPI docs.
- **React:** Component-based, large ecosystem, performant UI updates.
- **PostgreSQL:** Reliable ACID compliance, PostGIS support for geospatial queries.
- **YOLO:** State-of-the-art real-time object detection suitable for civic issues.
