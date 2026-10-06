import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base


class PriorityAnalysis(Base):
    """
    Intelligent Complaint Prioritization record.

    Stores the composite priority score (0-100), urgency tier (LOW, MEDIUM, HIGH, URGENT),
    exact mathematical factor contributions, explainable narrative, and model/config version.
    """
    __tablename__ = "priority_analysis"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), unique=True, index=True)
    priority_score: Mapped[float] = mapped_column(Float)
    priority_level: Mapped[str] = mapped_column(String(50))  # LOW, MEDIUM, HIGH, URGENT
    base_score: Mapped[float] = mapped_column(Float, default=0.0)
    escalation_boost: Mapped[float] = mapped_column(Float, default=0.0)
    contributing_factors: Mapped[dict] = mapped_column(JSON, default=dict)
    explanation: Mapped[str] = mapped_column(Text)

    algorithm_version: Mapped[str] = mapped_column(String(50), default="v1.0.0")
    config_version: Mapped[str] = mapped_column(String(50), default="v1.0.0")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="priority_analysis")


class PriorityHistory(Base):
    """
    Historical log of priority score changes for an individual complaint.
    Enables transparency and auditability when reports cluster or escalation triggers.
    """
    __tablename__ = "priority_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), index=True)
    priority_score: Mapped[float] = mapped_column(Float)
    priority_level: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(String(255), default="INITIAL_ANALYSIS")
    contributing_factors: Mapped[dict] = mapped_column(JSON, default=dict)
    explanation: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="priority_history")
