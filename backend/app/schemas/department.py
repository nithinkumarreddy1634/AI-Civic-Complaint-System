import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    contact_email: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}

class DepartmentRecommendation(BaseModel):
    department_id: uuid.UUID
    department_name: str
    confidence: float
    reason: str

class AssignmentCreate(BaseModel):
    department_id: uuid.UUID
    notes: Optional[str] = None

class AssignmentResponse(BaseModel):
    id: uuid.UUID
    complaint_id: uuid.UUID
    department_id: uuid.UUID
    assigned_by: uuid.UUID
    notes: Optional[str]
    assigned_at: datetime

    model_config = {"from_attributes": True}
