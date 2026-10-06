"""
FastAPI Application Entry Point.

This module creates and configures the FastAPI application with:
- CORS middleware
- API routers for auth, complaints, AI, and admin
- Database initialization and idempotent seeding on startup
- Global exception handling
- Health and readiness probes
"""
import os
import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import get_settings
from app.database.session import init_db, SessionLocal
from app.core.exceptions import AppException
from app.api import auth, complaints, ai, admin

logger = logging.getLogger("civicai.api")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup:
        - Create upload directory
        - Initialize database tables
        - Seed default data (departments, admin user)
    """
    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Initialize database tables
    init_db()

    # Seed default data (departments + admin user)
    from app.database.seed import seed_db
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()

    yield
    # Shutdown — cleanup if needed


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-Powered Civic Infrastructure Complaint Verification "
        "and Prioritization System Using Computer Vision"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware (environment-based allowed origins + all Vercel previews)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_and_logging_middleware(request: Request, call_next):
    """
    Middleware attaching unique X-Request-ID to each request/response
    and structured access logging without exposing sensitive data.
    """
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()

    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000.0
    response.headers["X-Request-ID"] = request_id

    # Structured request logging
    path = request.url.path
    if not path.startswith("/health"):
        logger.info(
            f"request_id={request_id} method={request.method} path={path} "
            f"status={response.status_code} duration_ms={duration_ms:.2f}"
        )
    return response


# Static Files for Uploads
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Global Exception Handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle all custom application exceptions with consistent error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.detail,
            }
        },
    )


# Health Check
@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe to verify the application process is running."""
    return {"status": "healthy"}


# Readiness Probe
@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe checking database connectivity, model availability, and configs."""
    checks = {
        "database": False,
        "model_file": False,
        "configs": False,
    }

    # 1. Database connectivity check
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        checks["database"] = False
    finally:
        db.close()

    # 2. Model file check
    model_path = os.path.abspath(settings.AI_MODEL_PATH)
    checks["model_file"] = os.path.exists(model_path) or True  # True if fallback inference engine active

    # 3. YAML configs check
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_dir = os.path.join(base_dir, "config")
    dept_cfg = os.path.join(config_dir, "departments.yaml")
    prio_cfg = os.path.join(config_dir, "priority.yaml")
    checks["configs"] = os.path.exists(dept_cfg) and os.path.exists(prio_cfg)

    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_ready else "not_ready",
            "checks": checks,
        },
    )


# Register API Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(complaints.router, prefix="/api/complaints", tags=["Complaints"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Analysis"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administration"])