import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base


class SeverityAnalysis(Base):
    """
    AI Severity Assessment and Damage Impact Analysis record.

    Stores multi-factor severity scores, safety risk, infrastructure impact,
    public impact, component evidence breakdown, and explainable audit trails.
    """
    __tablename__ = "severity_analysis"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), unique=True, index=True)
    severity_score: Mapped[float] = mapped_column(Float)
    severity_level: Mapped[str] = mapped_column(String(50))  # LOW, MEDIUM, HIGH, CRITICAL

    safety_risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    infrastructure_impact_score: Mapped[float] = mapped_column(Float, default=0.0)
    public_impact_score: Mapped[float] = mapped_column(Float, default=0.0)

    severity_factors: Mapped[dict] = mapped_column(JSON, default=dict)
    detection_analysis: Mapped[list] = mapped_column(JSON, default=list)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    explanation: Mapped[str] = mapped_column(Text)

    model_version: Mapped[str] = mapped_column(String(50), default="civic_yolo_v1")
    configuration_version: Mapped[str] = mapped_column(String(50), default="v1.0.0")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="severity_analysis")
