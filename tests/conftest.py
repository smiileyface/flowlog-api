"""
Pytest configuration and fixtures for testing.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.main import app
from app.models.base import Base

# Use PostgreSQL test database
# This matches your development environment and avoids SQLite compatibility issues
TEST_DATABASE_URL = (
    "postgresql://flowlog_user:flowlog_password@localhost:5432/flowlog_test"
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Create the test database schema once at the start of the test session.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables at the end of the test session
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Uses transactions that are rolled back after each test for isolation.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with the test database session.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_project(client):
    """
    Create a sample project for testing.
    """
    response = client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "description": "A test project"},
    )
    assert response.status_code == 201
    return response.json()["data"]


@pytest.fixture
def sample_journal(client, sample_project):
    """
    Create a sample journal for testing.
    """
    response = client.post(
        "/api/v1/journals/",
        json={"date": "2024-01-01", "project_id": sample_project["id"]},
    )
    assert response.status_code == 201
    return response.json()["data"]


@pytest.fixture
def sample_note(client, sample_journal):
    """
    Create a sample note for testing.
    """
    response = client.post(
        "/api/v1/notes/",
        json={
            "text": "Test note",
            "journal_id": sample_journal["id"],
            "meta": {"key": "value"},
        },
    )
    assert response.status_code == 201
    return response.json()["data"]


@pytest.fixture
def sample_tag(client):
    """
    Create a sample tag for testing.
    """
    response = client.post(
        "/api/v1/tags/",
        json={"name": "test-tag"},
    )
    assert response.status_code == 201
    return response.json()["data"]


@pytest.fixture
def sample_ai_job(client, sample_journal):
    """
    Create a sample AI job for testing.
    """
    response = client.post(
        "/api/v1/ai-jobs/",
        json={
            "journal_id": sample_journal["id"],
            "model_name": "gpt-4",
            "model_version": "0125",
            "prompt": "Test prompt",
        },
    )
    assert response.status_code == 201
    return response.json()["data"]
