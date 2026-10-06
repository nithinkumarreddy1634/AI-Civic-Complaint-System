from sqlalchemy.orm import Session
from app.models.department import Department, DepartmentCategoryMapping
import uuid
from typing import List, Optional

def recommend_department(db: Session, category: str) -> Department | None:
    mapping = db.query(DepartmentCategoryMapping).filter(DepartmentCategoryMapping.category == category).order_by(DepartmentCategoryMapping.priority_order.desc()).first()
    if mapping:
        return db.query(Department).filter(Department.id == mapping.department_id).first()
    return None

def get_all_departments(db: Session) -> List[Department]:
    return db.query(Department).all()

def get_department(db: Session, department_id: uuid.UUID) -> Department | None:
    return db.query(Department).filter(Department.id == department_id).first()
