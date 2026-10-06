import pytest
import uuid
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.session import Base, get_db
from app.models.user import User
from app.core.security import hash_password, create_access_token
from app.main import app

# Create in-memory sqlite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    user = User(
        id=uuid.uuid4(),
        name="Test Citizen",
        email=f"citizen_{uuid.uuid4().hex[:6]}@civicai.com",
        password_hash=hash_password("password123"),
        role="citizen",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db: Session) -> User:
    admin = User(
        id=uuid.uuid4(),
        name="Test Admin",
        email=f"admin_{uuid.uuid4().hex[:6]}@civicai.com",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def user_headers(test_user: User) -> dict:
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(test_admin: User) -> dict:
    token = create_access_token({"sub": str(test_admin.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_client(client: TestClient) -> TestClient:
    return client


@pytest.fixture
def test_db(db: Session) -> Session:
    return db
