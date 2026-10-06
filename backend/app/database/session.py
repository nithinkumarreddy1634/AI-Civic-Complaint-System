"""
Database session management.

Provides:
    - SQLAlchemy engine and session factory
    - Declarative base for ORM models
    - get_db() dependency for FastAPI route injection
    - init_db() for creating all tables
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator
from app.config import get_settings

settings = get_settings()

# SQLite requires check_same_thread=False for FastAPI's threaded request handling
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Usage:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...

    The session is automatically closed after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all database tables defined by ORM models.

    This imports all models to ensure they are registered with Base.metadata
    before calling create_all().
    """
    # Import all models so they are registered with Base
    from app.models import user, complaint, ai_analysis, severity, priority, department, status_history  # noqa: F401
    Base.metadata.create_all(bind=engine)