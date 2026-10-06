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
    complaints_over_time: List[dict]
    category_distribution: Dict[str, int]
    resolution_rate: float
    avg_resolution_time: Optional[float] = None

class HotspotData(BaseModel):
    latitude: float
    longitude: float
    count: int
    category: str
