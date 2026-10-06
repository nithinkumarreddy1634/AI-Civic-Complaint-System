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
