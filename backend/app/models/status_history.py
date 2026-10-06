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
