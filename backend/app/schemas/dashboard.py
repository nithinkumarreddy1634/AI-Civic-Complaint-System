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
    complaints_over_time: List[dict] = []
    category_distribution: Dict[str, int] = {}
    resolution_rate: float = 0.0
    avg_resolution_time: Optional[float] = None
    total_complaints: int = 0
    avg_severity_score: Optional[float] = None
    avg_priority_score: Optional[float] = None
    by_category: Dict[str, int] = {}
    by_priority: Dict[str, int] = {}
    by_severity: Dict[str, int] = {}
    by_verification: Dict[str, int] = {}
    by_status: Dict[str, int] = {}

class HotspotData(BaseModel):
    latitude: float
    longitude: float
    count: int = 1
    category: str = "general"
    complaint_count: Optional[int] = 1
    top_category: Optional[str] = "general"
