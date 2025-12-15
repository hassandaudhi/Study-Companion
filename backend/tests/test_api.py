import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Set up test database before tests and clean up after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user with unique email"""
    unique_id = str(uuid.uuid4())[:8]
    response = client.post(
        "/api/users/",
        json={
            "email": f"test_{unique_id}@example.com",
            "username": f"testuser_{unique_id}",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201, f"Failed to create test user: {response.json()}"
    return response.json()


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_user():
    """Test user creation"""
    unique_id = str(uuid.uuid4())[:8]
    response = client.post(
        "/api/users/",
        json={
            "email": f"newuser_{unique_id}@example.com",
            "username": f"newuser_{unique_id}",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == f"newuser_{unique_id}@example.com"
    assert data["username"] == f"newuser_{unique_id}"
    assert "id" in data


def test_get_user(test_user):
    """Test getting a user"""
    user_id = test_user["id"]
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == test_user["email"]


def test_create_chat(test_user):
    """Test chat creation"""
    response = client.post(
        "/api/chats/",
        json={
            "user_id": test_user["id"],
            "title": "Test Chat",
            "agent_type": "summarizer"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Chat"
    assert data["user_id"] == test_user["id"]


def test_create_message(test_user):
    """Test message creation"""
    # First create a chat
    chat_response = client.post(
        "/api/chats/",
        json={
            "user_id": test_user["id"],
            "title": "Test Chat"
        }
    )
    chat_id = chat_response.json()["id"]
    
    # Create message
    response = client.post(
        "/api/messages/",
        json={
            "chat_id": chat_id,
            "role": "user",
            "content": "Hello, this is a test message"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Hello, this is a test message"
    assert data["role"] == "user"
