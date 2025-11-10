import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.models.drop import Drop, DropStatus
from app.utils.jwt_handler import hash_password, create_access_token
from datetime import datetime, timedelta

# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Database fixture: Creates fresh DB for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI test client with overridden DB dependency"""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin user"""
    user = User(
        email="admin@example.com",
        password_hash=hash_password("adminpassword123"),
        role=UserRole.ADMIN
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def user_token(test_user):
    """Generate JWT token for test user"""
    return create_access_token(data={"sub": test_user.id})


@pytest.fixture
def admin_token(admin_user):
    """Generate JWT token for admin user"""
    return create_access_token(data={"sub": admin_user.id})


@pytest.fixture
def test_drop(db, admin_user):
    """Create a test drop"""
    drop = Drop(
        name="Test Drop",
        description="Test description",
        total_stock=100,
        claimed_count=0,
        claim_window_start=datetime.utcnow() + timedelta(hours=1),
        claim_window_end=datetime.utcnow() + timedelta(hours=2),
        status=DropStatus.ACTIVE,
        created_by_user_id=admin_user.id
    )
    db.add(drop)
    db.commit()
    db.refresh(drop)
    return drop


@pytest.fixture
def active_claim_drop(db, admin_user):
    """Create a drop with active claim window"""
    drop = Drop(
        name="Active Claim Drop",
        description="Claim window is open",
        total_stock=50,
        claimed_count=0,
        claim_window_start=datetime.utcnow() - timedelta(minutes=10),
        claim_window_end=datetime.utcnow() + timedelta(hours=1),
        status=DropStatus.ACTIVE,
        created_by_user_id=admin_user.id
    )
    db.add(drop)
    db.commit()
    db.refresh(drop)
    return drop
