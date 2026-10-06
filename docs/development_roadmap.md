# Development Roadmap

## Phase 1: Architecture & Foundation (Current)
- Initialize project structure.
- Create all core documentation (README, architecture, API reference, DB schema, roadmap).
- Define ML placeholder directories.
- Create Gitignore and Docker configuration.

## Phase 2: Backend Core
- Set up FastAPI framework and structure.
- Configure SQLAlchemy 2.0 and PostgreSQL (or SQLite for dev).
- Implement User Authentication (JWT, registration, login).
- Implement CRUD operations for complaints.
- Setup file upload functionality.
- Write Pytest unit tests for core endpoints.

## Phase 3: AI Pipeline
- Gather and preprocess dataset (e.g., potholes, garbage, streetlights).
- Train YOLOv8 object detection model.
- Implement computer vision inference service in FastAPI.
- Build severity algorithm and priority scoring mechanism.
- Implement duplicate detection logic based on proximity and visual similarity.
- Build automated department routing logic.

## Phase 4: Frontend Implementation
- Initialize React (Vite) + Tailwind CSS project.
- Implement authentication UI (Login/Register).
- Build Citizen dashboard (Submit complaint, view status).
- Build Admin/Department dashboard (View list, maps, update status).
- Integrate mapping library (Leaflet or Google Maps).
- Connect frontend to FastAPI endpoints.

## Phase 5: Integration & Polish
- End-to-end integration testing.
- UI/UX polish and responsiveness improvements.
- Performance optimization (Database indexing, API caching).
- Docker deployment finalization.
- Update documentation with final deployment instructions.
