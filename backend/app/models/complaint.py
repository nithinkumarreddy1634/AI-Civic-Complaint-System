import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Text, Integer, JSON
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


class ProcessingState:
    """Internal states of the AI Processing Pipeline."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    VERIFICATION_COMPLETE = "VERIFICATION_COMPLETE"
    SEVERITY_COMPLETE = "SEVERITY_COMPLETE"
    DUPLICATE_CHECK_COMPLETE = "DUPLICATE_CHECK_COMPLETE"
    PRIORITY_COMPLETE = "PRIORITY_COMPLETE"
    DEPARTMENT_RECOMMENDED = "DEPARTMENT_RECOMMENDED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


class ComplaintStatus:
    """Complaint lifecycle statuses."""
    SUBMITTED = "SUBMITTED"
    AI_PROCESSING = "AI_PROCESSING"
    VERIFIED = "VERIFIED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    REJECTED = "REJECTED"
    PRIORITIZED = "PRIORITIZED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(Text)
    image_path: Mapped[str] = mapped_column(String(255))
    image_original_name: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=ComplaintStatus.SUBMITTED, index=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_of: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("complaints.id"), nullable=True)

    # Phase 8: AI Processing State & Department Recommendation
    processing_state: Mapped[str] = mapped_column(String(50), default=ProcessingState.PENDING, index=True)
    processing_progress: Mapped[int] = mapped_column(Integer, default=0)
    processing_message: Mapped[str | None] = mapped_column(String(255), nullable=True)
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    department_recommendation: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="complaints")
    ai_analysis = relationship("AIAnalysis", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    severity_analysis = relationship("SeverityAnalysis", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    priority_analysis = relationship("PriorityAnalysis", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    priority_history = relationship("PriorityHistory", back_populates="complaint", cascade="all, delete-orphan")
    assignments = relationship("ComplaintAssignment", back_populates="complaint", cascade="all, delete-orphan")
    status_history = relationship("ComplaintStatusHistory", back_populates="complaint", cascade="all, delete-orphan")
    embedding = relationship("ComplaintEmbedding", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
    duplicate_link = relationship("ComplaintDuplicateLink", foreign_keys="[ComplaintDuplicateLink.complaint_id]", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
