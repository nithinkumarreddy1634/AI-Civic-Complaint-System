import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Float, ForeignKey, Integer, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), unique=True)
    detected_class: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    bounding_box: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    image_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_civic_issue: Mapped[bool] = mapped_column(Boolean, default=False)
    detection_status: Mapped[str] = mapped_column(String(50), default="PROCESSED")
    verification_score: Mapped[float] = mapped_column(Float, default=0.0)
    verification_status: Mapped[str] = mapped_column(String(50), default="PENDING")

    # Phase 4 extensions: Quality, Consistency, Explainability, and Audit Trail
    image_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    text_consistency_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    explanation: Mapped[list | None] = mapped_column(JSON, nullable=True)
    audit_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    config_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    complaint = relationship("Complaint", back_populates="ai_analysis")
