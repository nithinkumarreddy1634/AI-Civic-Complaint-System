"""SQLAlchemy Models."""
from app.database.session import Base
from app.models.user import User
from app.models.complaint import Complaint
from app.models.ai_analysis import AIAnalysis
from app.models.severity import SeverityAnalysis
from app.models.priority import PriorityAnalysis, PriorityHistory
from app.models.department import Department, DepartmentCategoryMapping, ComplaintAssignment
from app.models.status_history import ComplaintStatusHistory
from app.models.duplicate import ComplaintEmbedding, DuplicateGroup, ComplaintDuplicateLink

__all__ = [
    "Base", "User", "Complaint", "AIAnalysis", "SeverityAnalysis", 
    "PriorityAnalysis", "PriorityHistory", "Department", "DepartmentCategoryMapping", 
    "ComplaintAssignment", "ComplaintStatusHistory",
    "ComplaintEmbedding", "DuplicateGroup", "ComplaintDuplicateLink"
]
