import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import os

from app.main import app
from app.database import get_db, engine
from app.models import User
from app.security import get_password_hash

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    # Create a new engine instance for testing
    test_engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)

    # Create a new session for the test
    with Session(test_engine) as session:
        def override_get_db():
            try:
                yield session
            finally:
                pass

        # Override the get_db dependency
        app.dependency_overrides[get_db] = override_get_db
        yield session

    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_user(test_db):
    user = User(
        email="test@example.com",
        full_name="Test User",
        location="Test Location",
        hashed_password=get_password_hash(
            "test123")  # Using a shorter password
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user
