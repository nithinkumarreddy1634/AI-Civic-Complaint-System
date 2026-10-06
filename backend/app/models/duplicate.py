"""Database models for embeddings, duplicate groups, and duplicate complaint links."""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base


class ComplaintEmbedding(Base):
    """
    Stores versioned visual and textual vector representations for a complaint.
    """
    __tablename__ = "complaint_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), unique=True, index=True)

    image_embedding: Mapped[list] = mapped_column(JSON)
    text_embedding: Mapped[list] = mapped_column(JSON)

    image_model: Mapped[str] = mapped_column(String(100), default="mobilenet_v3_feature_extractor")
    image_model_version: Mapped[str] = mapped_column(String(50), default="v1.0.0")
    text_model: Mapped[str] = mapped_column(String(100), default="semantic_civic_embedder")
    text_model_version: Mapped[str] = mapped_column(String(50), default="v1.0.0")
    dimension: Mapped[int] = mapped_column(Integer, default=512)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="embedding")


class DuplicateGroup(Base):
    """
    Represents an aggregated cluster of duplicate reports referring to the same physical issue.
    """
    __tablename__ = "duplicate_groups"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    representative_complaint_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("complaints.id"), nullable=True)

    report_count: Mapped[int] = mapped_column(Integer, default=1)
    unique_users_count: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    representative_complaint = relationship("Complaint", foreign_keys=[representative_complaint_id])
    links = relationship("ComplaintDuplicateLink", back_populates="group", cascade="all, delete-orphan")


class ComplaintDuplicateLink(Base):
    """
    Links an individual complaint to its parent DuplicateGroup with similarity metrics.
    """
    __tablename__ = "complaint_duplicate_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("duplicate_groups.id"), index=True)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), unique=True, index=True)

    similarity_score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    group = relationship("DuplicateGroup", back_populates="links")
    complaint = relationship("Complaint", foreign_keys=[complaint_id])
