"""Department recommendation package."""
from app.ai.department.config import (
    DepartmentConfig,
    DepartmentMeta,
    FallbackDepartment,
    department_config,
)
from app.ai.department.department_service import (
    DepartmentRecommendationService,
    department_recommendation_service,
)

__all__ = [
    "DepartmentConfig",
    "DepartmentMeta",
    "FallbackDepartment",
    "department_config",
    "DepartmentRecommendationService",
    "department_recommendation_service",
]
