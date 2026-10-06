from abc import ABC, abstractmethod
from pydantic import BaseModel
import uuid
from sqlalchemy.orm import Session

class DepartmentRecommendation(BaseModel):
    department_id: uuid.UUID
    confidence_score: float

class BaseDepartmentRecommender(ABC):
    """
    Abstract interface for recommending a department for a civic issue.
    """
    @abstractmethod
    async def recommend(self, category: str, db: Session) -> DepartmentRecommendation:
        pass

class DepartmentRecommender(BaseDepartmentRecommender):
    """
    Recommends department.
    Will look up department_category_mapping table, return best-match department.
    """
    async def recommend(self, category: str, db: Session) -> DepartmentRecommendation:
        raise NotImplementedError("Department Recommendation will be implemented in Phase 2.")
