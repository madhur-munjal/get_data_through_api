import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from src.database import get_db
from src.main import app  # or wherever your FastAPI app is defined
from src.schemas.tables.users import User
from src.models.users import UserLogin
from src.auth_utils import verify_password, create_access_token

client = TestClient(app)


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.username = "testuser"
    user.password = "hashedpassword"
    user.id = 1
    user.email = "test@example.com"
    return user


def test_login_success(mock_user):
    with patch("src.database.get_db") as mock_get_db, patch(
        "src.auth_utils.verify_password", return_value=True
    ), patch("src.auth_utils.create_access_token", return_value="mocked_token"):

        mock_session = MagicMock(spec=Session)
        mock_session.query().filter_by().first.return_value = mock_user
        mock_get_db.return_value = mock_session

        payload = {"username": "testuser", "password": "correctpassword"}

        response = client.post("/api/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "User logged in successfully"
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["user_details"]["username"] == "testuser"


def test_login_invalid_credentials():
    with patch("app.routes.auth.get_db") as mock_get_db, patch(
        "app.routes.auth.verify_password", return_value=False
    ):

        mock_session = MagicMock(spec=Session)
        mock_session.query().filter_by().first.return_value = None
        mock_get_db.return_value = mock_session

        payload = {"username": "wronguser", "password": "wrongpassword"}

        response = client.post("/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Invalid credentials"
        assert data["data"] is None
