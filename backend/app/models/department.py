import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database.session import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    mappings = relationship("DepartmentCategoryMapping", back_populates="department", cascade="all, delete-orphan")
    assignments = relationship("ComplaintAssignment", back_populates="department")


class DepartmentCategoryMapping(Base):
    __tablename__ = "department_category_mappings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"))
    category: Mapped[str] = mapped_column(String(100), index=True)
    priority_order: Mapped[int] = mapped_column(Integer, default=1)

    department = relationship("Department", back_populates="mappings")


class ComplaintAssignment(Base):
    __tablename__ = "complaint_assignments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), index=True)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), index=True)
    assigned_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    complaint = relationship("Complaint", back_populates="assignments")
    department = relationship("Department", back_populates="assignments")
    assigned_by_user = relationship("User", back_populates="assignments")
