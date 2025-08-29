from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.main import app  # Replace with your actual FastAPI app import
from src.schemas.tables import Patient  # Your SQLAlchemy model

# Sample UUID for testing
TEST_DOCTOR_ID = UUID("12345678-1234-5678-1234-567812345678")
TEST_PATIENT_ID = "patient-123"


# Sample patient data
def mock_patient():
    return Patient(
        patient_id=1,
        firstName="John",
        age=30,
        mobile="9999999999",
        assigned_doctor_id=TEST_DOCTOR_ID
    )


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db_session(mocker):
    mock_session = mocker.Mock()
    mock_session.query().filter().all.return_value = [mock_patient()]
    return mock_session


@pytest.fixture
def override_dependencies(client, mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_current_doctor_id] = lambda: TEST_DOCTOR_ID
    yield
    app.dependency_overrides.clear()


class MockQueryChain:
    def __init__(self, results):
        self._results = results

    def filter_by(self, **kwargs):
        return self

    def offset(self, offset):
        return self

    def limit(self, limit):
        return self

    def all(self):
        return self._results





