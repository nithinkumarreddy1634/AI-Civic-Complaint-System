"""Idempotent database seeding script for municipal departments and category mappings."""
import sys
import os

# Add backend directory to sys.path so script can be run standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.department import Department, DepartmentCategoryMapping
from app.ai.department.config import DepartmentConfig


def seed_departments(db: Session, config: DepartmentConfig = None):
    """Seed or update departments and category mappings from configuration."""
    if config is None:
        config = DepartmentConfig.load()

    print(f"Seeding {len(config.departments)} departments from configuration...")

    for code, dept_meta in config.departments.items():
        # Check by code or name
        dept = db.query(Department).filter(
            (Department.code == code) | (Department.name == dept_meta.name)
        ).first()

        if not dept:
            dept = Department(
                code=code,
                name=dept_meta.name,
                description=dept_meta.description,
                contact_email=dept_meta.contact_email,
                is_active=True,
            )
            db.add(dept)
            db.flush()
            print(f"  + Added department: {dept_meta.name} [{code}]")
        else:
            dept.code = code
            dept.description = dept_meta.description
            dept.contact_email = dept_meta.contact_email
            dept.is_active = True
            db.flush()
            print(f"  * Updated department: {dept.name} [{code}]")

        # Seed category mappings
        for category in dept_meta.categories:
            mapping = db.query(DepartmentCategoryMapping).filter(
                DepartmentCategoryMapping.department_id == dept.id,
                DepartmentCategoryMapping.category == category,
            ).first()

            if not mapping:
                mapping = DepartmentCategoryMapping(
                    department_id=dept.id,
                    category=category,
                    priority_order=dept_meta.priority_order,
                )
                db.add(mapping)
                print(f"    -> Mapped category '{category}' to {dept.name}")

    db.commit()
    print("Department seeding completed successfully.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_departments(db)
    finally:
        db.close()
