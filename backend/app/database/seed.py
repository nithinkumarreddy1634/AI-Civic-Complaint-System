from sqlalchemy.orm import Session
from app.models.user import User
from app.models.department import Department, DepartmentCategoryMapping
from app.core.security import hash_password
from app.ai.department.config import DepartmentConfig


def seed_db(db: Session):
    """Seed administrator account and departments with category mappings."""
    # 1. Seed Admin
    admin = db.query(User).filter(User.email == 'admin@civicai.com').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@civicai.com',
            password_hash=hash_password('admin123'),
            role='admin',
            is_active=True,
        )
        db.add(admin)

    # 2. Seed Departments from DepartmentConfig
    config = DepartmentConfig.load()
    for code, dept_meta in config.departments.items():
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
        else:
            dept.code = code
            dept.description = dept_meta.description
            dept.contact_email = dept_meta.contact_email
            dept.is_active = True
            db.flush()

        # Seed mappings
        for cat in dept_meta.categories:
            mapping = db.query(DepartmentCategoryMapping).filter(
                DepartmentCategoryMapping.department_id == dept.id,
                DepartmentCategoryMapping.category == cat,
            ).first()
            if not mapping:
                mapping = DepartmentCategoryMapping(
                    department_id=dept.id,
                    category=cat,
                    priority_order=dept_meta.priority_order,
                )
                db.add(mapping)

    db.commit()
