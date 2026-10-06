import os
from pathlib import Path

ROOT = r"c:\Users\nithi\Downloads\AI-Powered Civic Infrastructure Complaint Verification and Prioritization System Using Computer Vision\backend"

files = {
    "app/__init__.py": '''
"""CivicAI Backend Application."""
''',
    "app/config.py": '''
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = 'CivicAI'
    DEBUG: bool = True
    SECRET_KEY: str = 'change_this_to_a_secure_random_string'
    ALLOWED_ORIGINS: str = 'http://localhost:5173'
    DATABASE_URL: str = 'sqlite:///./civicai.db'
    JWT_SECRET_KEY: str = 'change_this_to_a_secure_jwt_secret'
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = './uploads'
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = 'jpg,jpeg,png'
    AI_MODEL_PATH: str = './ml/models/best.pt'
    AI_CONFIDENCE_THRESHOLD: float = 0.5

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]

    @property
    def allowed_extensions_list(self) -> list[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(',')]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

@lru_cache
def get_settings() -> Settings:
    return Settings()
''',
    "app/main.py": '''
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.session import init_db
from app.database.seed import seed_db
from app.core.exceptions import AppException

# Import routers once they are created
# from app.api import auth, complaints, ai, admin

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    init_db()
    # Call seed_db() inside a session in real life
    yield
    # Shutdown

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Civic Infrastructure Complaint Verification and Prioritization System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(complaints.router, prefix="/api/complaints", tags=["complaints"])
# app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
# app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
''',
    "app/core/__init__.py": '''
"""Core functionality (security, exceptions)."""
''',
    "app/core/security.py": '''
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    try:
        decoded_data = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decoded_data
    except JWTError:
        raise ValueError("Invalid token")
''',
    "app/core/exceptions.py": '''
class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)

class ForbiddenException(AppException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)

class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=400, detail=detail)

class ConflictException(AppException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=409, detail=detail)

class AIProcessingException(AppException):
    def __init__(self, detail: str = "AI Processing Error"):
        super().__init__(status_code=500, detail=detail)

class FileValidationException(AppException):
    def __init__(self, detail: str = "File Validation Error"):
        super().__init__(status_code=422, detail=detail)
''',
    "app/database/__init__.py": '''
"""Database connections and seeding."""
''',
    "app/database/session.py": '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator
from app.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async def get_db() -> AsyncGenerator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
''',
    "app/database/seed.py": '''
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.department import Department, DepartmentCategoryMapping
from app.core.security import hash_password

def seed_db(db: Session):
    # Seed Admin
    admin = db.query(User).filter(User.email == 'admin@civicai.com').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@civicai.com',
            password_hash=hash_password('admin123'),
            role='admin'
        )
        db.add(admin)

    # Seed Departments
    departments = [
        "Roads Department",
        "Sanitation Department",
        "Electrical Department",
        "Water Department",
        "Horticulture/Municipal Department",
        "Public Works Department"
    ]
    
    dept_map = {}
    for d_name in departments:
        dept = db.query(Department).filter(Department.name == d_name).first()
        if not dept:
            dept = Department(name=d_name, description=f"{d_name} description")
            db.add(dept)
            db.flush()
        dept_map[d_name] = dept.id

    # Seed Mappings
    mappings = {
        'pothole': 'Roads Department',
        'garbage_accumulation': 'Sanitation Department',
        'open_manhole': 'Public Works Department',
        'damaged_road': 'Roads Department',
        'broken_streetlight': 'Electrical Department',
        'water_leakage': 'Water Department',
        'damaged_sidewalk': 'Roads Department',
        'fallen_tree': 'Horticulture/Municipal Department',
        'illegal_dumping': 'Sanitation Department',
        'other': 'Public Works Department'
    }

    for cat, d_name in mappings.items():
        existing = db.query(DepartmentCategoryMapping).filter(DepartmentCategoryMapping.category == cat).first()
        if not existing:
            mapping = DepartmentCategoryMapping(
                department_id=dept_map[d_name],
                category=cat,
                priority_order=1
            )
            db.add(mapping)

    db.commit()
''',
    "app/models/__init__.py": '''
"""SQLAlchemy Models."""
from app.database.session import Base
from app.models.user import User
from app.models.complaint import Complaint
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from app.models.priority import PriorityAnalysis
from app.models.department import Department, DepartmentCategoryMapping, ComplaintAssignment
from app.models.status_history import ComplaintStatusHistory

__all__ = [
    "Base", "User", "Complaint", "AIAnalysis", "SeverityAnalysis", 
    "PriorityAnalysis", "Department", "DepartmentCategoryMapping", 
    "ComplaintAssignment", "ComplaintStatusHistory"
]
''',
    "app/models/user.py": '''
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default='citizen')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    complaints = relationship("Complaint", back_populates="user")
    assignments = relationship("ComplaintAssignment", back_populates="assigned_by_user")
    status_history_changes = relationship("ComplaintStatusHistory", back_populates="changer")
''',
    "app/models/complaint.py": '''
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base

class ComplaintCategory:
    POTHOLE = "pothole"
    GARBAGE = "garbage_accumulation"
    MANHOLE = "open_manhole"
    DAMAGED_ROAD = "damaged_road"
    STREETLIGHT = "broken_streetlight"
    WATER_LEAKAGE = "water_leakage"
    SIDEWALK = "damaged_sidewalk"
    TREE = "fallen_tree"
    DUMPING = "illegal_dumping"
    OTHER = "other"

class ComplaintStatus:
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"

class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    image_path: Mapped[str] = mapped_column(String(255))
    image_original_name: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=ComplaintStatus.SUBMITTED)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_of: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("complaints.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="complaints")
    ai_analysis = relationship("AIAnalysis", back_populates="complaint", uselist=False)
    severity_analysis = relationship("SeverityAnalysis", back_populates="complaint", uselist=False)
    priority_analysis = relationship("PriorityAnalysis", back_populates="complaint", uselist=False)
    assignments = relationship("ComplaintAssignment", back_populates="complaint")
    status_history = relationship("ComplaintStatusHistory", back_populates="complaint")
''',
    "app/models/ai_analysis.py": '''
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Integer, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base

class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), unique=True)
    detected_class: Mapped[str] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float)
    bounding_box: Mapped[dict] = mapped_column(JSON)
    image_width: Mapped[int] = mapped_column(Integer)
    image_height: Mapped[int] = mapped_column(Integer)
    is_civic_issue: Mapped[bool] = mapped_column(Boolean)
    detection_status: Mapped[str] = mapped_column(String(50))
    verification_score: Mapped[float] = mapped_column(Float)
    verification_status: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="ai_analysis")
''',
    "app/models/severity.py": '''
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base

class SeverityAnalysis(Base):
    __tablename__ = "severity_analysis"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), unique=True)
    severity_score: Mapped[float] = mapped_column(Float)
    severity_level: Mapped[str] = mapped_column(String(50))
    severity_factors: Mapped[dict] = mapped_column(JSON)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="severity_analysis")
''',
    "app/models/priority.py": '''
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base

class PriorityAnalysis(Base):
    __tablename__ = "priority_analysis"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), unique=True)
    priority_score: Mapped[float] = mapped_column(Float)
    priority_level: Mapped[str] = mapped_column(String(50))
    contributing_factors: Mapped[dict] = mapped_column(JSON)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="priority_analysis")
''',
    "app/models/department.py": '''
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    mappings = relationship("DepartmentCategoryMapping", back_populates="department")
    assignments = relationship("ComplaintAssignment", back_populates="department")


class DepartmentCategoryMapping(Base):
    __tablename__ = "department_category_mappings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"))
    category: Mapped[str] = mapped_column(String(100))
    priority_order: Mapped[int] = mapped_column(Integer, default=1)

    department = relationship("Department", back_populates="mappings")


class ComplaintAssignment(Base):
    __tablename__ = "complaint_assignments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"))
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"))
    assigned_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="assignments")
    department = relationship("Department", back_populates="assignments")
    assigned_by_user = relationship("User", back_populates="assignments")
''',
    "app/models/status_history.py": '''
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base

class ComplaintStatusHistory(Base):
    __tablename__ = "complaint_status_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"))
    old_status: Mapped[str] = mapped_column(String(50))
    new_status: Mapped[str] = mapped_column(String(50))
    changed_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="status_history")
    changer = relationship("User", back_populates="status_history_changes")
''',
    "app/schemas/__init__.py": '''
"""Pydantic Schemas."""
from .user import UserRegister, UserLogin, UserResponse, TokenResponse
from .complaint import ComplaintCreate, ComplaintUpdate, ComplaintResponse, ComplaintListResponse, ComplaintCategory, ComplaintStatus
from .ai_analysis import DetectionResult, VerificationResult, AIAnalysisResponse
from .severity import SeverityResult, SeverityLevel
from .priority import PriorityResult, PriorityLevel
from .department import DepartmentResponse, DepartmentRecommendation, AssignmentCreate, AssignmentResponse
from .dashboard import DashboardStats, AnalyticsData, HotspotData

__all__ = [
    "UserRegister", "UserLogin", "UserResponse", "TokenResponse",
    "ComplaintCreate", "ComplaintUpdate", "ComplaintResponse", "ComplaintListResponse", "ComplaintCategory", "ComplaintStatus",
    "DetectionResult", "VerificationResult", "AIAnalysisResponse",
    "SeverityResult", "SeverityLevel",
    "PriorityResult", "PriorityLevel",
    "DepartmentResponse", "DepartmentRecommendation", "AssignmentCreate", "AssignmentResponse",
    "DashboardStats", "AnalyticsData", "HotspotData"
]
''',
    "app/schemas/user.py": '''
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
''',
    "app/schemas/complaint.py": '''
import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class ComplaintCategory(str, Enum):
    POTHOLE = "pothole"
    GARBAGE = "garbage_accumulation"
    MANHOLE = "open_manhole"
    DAMAGED_ROAD = "damaged_road"
    STREETLIGHT = "broken_streetlight"
    WATER_LEAKAGE = "water_leakage"
    SIDEWALK = "damaged_sidewalk"
    TREE = "fallen_tree"
    DUMPING = "illegal_dumping"
    OTHER = "other"

class ComplaintStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"

class ComplaintCreate(BaseModel):
    category: ComplaintCategory
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None

class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    category: Optional[ComplaintCategory] = None
    description: Optional[str] = None

class ComplaintListResponse(BaseModel):
    id: uuid.UUID
    category: str
    description: str
    status: str
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    priority_level: Optional[str] = None

    model_config = {"from_attributes": True}

class ComplaintResponse(ComplaintListResponse):
    user_id: uuid.UUID
    image_path: str
    image_original_name: str
    address: Optional[str]
    is_duplicate: bool
    duplicate_of: Optional[uuid.UUID]
    updated_at: datetime
    
    # Needs to be populated with real nested objects optionally
    # user: Optional[UserResponse] = None
    # ai_analysis: Optional[AIAnalysisResponse] = None
    # severity_analysis: Optional[dict] = None
    # priority_analysis: Optional[dict] = None

    model_config = {"from_attributes": True}
''',
    "app/schemas/ai_analysis.py": '''
import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class DetectionResult(BaseModel):
    detected_issue: Optional[str] = None
    confidence: float
    bounding_box: Optional[List[float]] = None
    image_width: int
    image_height: int
    is_civic_issue: bool
    detection_status: str

class VerificationResult(BaseModel):
    verification_score: float
    verification_status: str
    is_civic_issue: bool

class AIAnalysisResponse(BaseModel):
    id: uuid.UUID
    complaint_id: uuid.UUID
    detected_class: str
    confidence: float
    bounding_box: dict
    image_width: int
    image_height: int
    is_civic_issue: bool
    detection_status: str
    verification_score: float
    verification_status: str
    created_at: datetime

    model_config = {"from_attributes": True}
''',
    "app/schemas/severity.py": '''
from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any

class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SeverityResult(BaseModel):
    severity_score: float
    severity_level: SeverityLevel
    severity_factors: Dict[str, Any]
    explanation: str
''',
    "app/schemas/priority.py": '''
from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any

class PriorityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class PriorityResult(BaseModel):
    priority_score: float
    priority_level: PriorityLevel
    contributing_factors: Dict[str, Any]
    explanation: str
''',
    "app/schemas/department.py": '''
import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    contact_email: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}

class DepartmentRecommendation(BaseModel):
    department_id: uuid.UUID
    department_name: str
    confidence: float
    reason: str

class AssignmentCreate(BaseModel):
    department_id: uuid.UUID
    notes: Optional[str] = None

class AssignmentResponse(BaseModel):
    id: uuid.UUID
    complaint_id: uuid.UUID
    department_id: uuid.UUID
    assigned_by: uuid.UUID
    notes: Optional[str]
    assigned_at: datetime

    model_config = {"from_attributes": True}
''',
    "app/schemas/dashboard.py": '''
from pydantic import BaseModel
from typing import Dict, List, Optional

class DashboardStats(BaseModel):
    total_complaints: int
    verified: int
    pending: int
    rejected: int
    high_priority: int
    urgent: int
    resolved: int
    by_category: Dict[str, int]
    by_department: Dict[str, int]
    by_status: Dict[str, int]
    recent_complaints: List[dict]

class AnalyticsData(BaseModel):
    complaints_over_time: List[dict]
    category_distribution: Dict[str, int]
    resolution_rate: float
    avg_resolution_time: Optional[float] = None

class HotspotData(BaseModel):
    latitude: float
    longitude: float
    count: int
    category: str
''',
    "requirements.txt": '''
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
aiofiles>=23.0.0
Pillow>=10.0.0
numpy>=1.24.0
opencv-python>=4.8.0
torch>=2.0.0
ultralytics>=8.0.0
scikit-learn>=1.3.0
python-dotenv>=1.0.0
alembic>=1.12.0
httpx>=0.25.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
''',
    ".env.example": '''
# Application Settings
APP_NAME=CivicAI
DEBUG=True
SECRET_KEY=generate_a_strong_secret_key
ALLOWED_ORIGINS=http://localhost:5173

# Database Settings
DATABASE_URL=sqlite:///./civicai.db

# JWT Settings
JWT_SECRET_KEY=generate_a_strong_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# File Upload Settings
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=jpg,jpeg,png

# AI Settings
AI_MODEL_PATH=./ml/models/best.pt
AI_CONFIDENCE_THRESHOLD=0.5
'''
}

def main():
    for rel_path, content in files.items():
        full_path = Path(ROOT) / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\\n")
    print("Files created successfully.")

if __name__ == "__main__":
    main()
