# test_routers_patients.py
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


def test_get_patients_list(client, override_dependencies):
    response = client.get("/patients/get_patients_list")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Patients fetched successfully."
    assert isinstance(data["data"], list)
    assert data["data"][0]["firstName"] == "John"
    assert data["data"][0]["age"] == 30



def test_update_patient_success(client, override_dependencies):
    payload = {
        "firstName": "Jane",
        "lastName": "string",
        "age": 35,
        "mobile": "string",
        "gender": "male",
        "address": "string",
        "bloodGroup": "A+"
    }
    response = client.put(f"/patients/{TEST_PATIENT_ID}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Patient updated successfully."


def test_update_patient_not_found(client, mocker):
    payload = {
        "firstName": "NotFound",
        "lastName": "string",
        "age": 35,
        "mobile": "string",
        "gender": "male",
        "address": "string",
        "bloodGroup": "A+"
    }
    mock_session = mocker.Mock()
    query_mock = mocker.Mock()
    query_mock.filter().first.return_value = None  # Simulate not found
    mock_session.query.return_value = query_mock

    app.dependency_overrides[get_db] = lambda: mock_session
    app.dependency_overrides[get_current_doctor_id] = lambda: TEST_DOCTOR_ID

    response = client.put(f"/patients/{TEST_PATIENT_ID}", json=payload)
    assert response.status_code == 404
    assert response.json()["message"] == "Patient not found"

    app.dependency_overrides.clear()
