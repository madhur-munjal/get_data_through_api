from fastapi.testclient import TestClient

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.main import app
from .conftest import mock_get_db, mock_get_current_doctor_id

client = TestClient(app) # Try to use fixture of client in all tests
app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_current_doctor_id] = mock_get_current_doctor_id


# def test_create_patient_mobile_exists(client):
#     # existing_patient = MockPatient(mobile="9999999999")
#     # app.dependency_overrides[get_db] = lambda: MockSession(existing_patients=[existing_patient])
#
#     payload = {
#         "name": "John Doe",
#         "mobile": "9999999999",
#         "age": 30,
#         "gender": "Male",
#         "address": "123 Street",
#         "email": "john@example.com"
#     }
#
#     response = client.post("patients/register", json=payload)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["success"] is False
#     assert data["message"] == "Mobile number already exists"
#     assert data["data"] is None


def test_create_patient_success():
    app.dependency_overrides[get_db] = lambda: mock_get_db(keep_model_empty=True)
    payload = {
        "firstName": "Jane",
        "lastName": "Doe",
        "mobile": "8888888888",
        "age": 28,
        "gender": "female",
        "address": "456 Avenue",
        "email": "jane@example.com"
    }
    response = client.post("patients/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Patient created successfully."
    assert "id" in data["data"]


def test_update_patent_success(client):
    payload = {
        "firstName": "Jane",
        "mobile": "8888888888",
        "age": 28,
        "gender": "female",
        "email": "jane@example.com",
        "address": "456 Avenue"
    }

    response = client.put("patients/12345678-1234-5678-1234-567812345778", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Patient updated successfully."
    assert data["data"] is None


def test_update_patient_not_found(client):
    # app.dependency_overrides[get_db] = lambda: MockSession(patients=[])
    app.dependency_overrides[get_db] = lambda: mock_get_db(keep_model_empty=True)
    payload = {
        "firstName": "Ghost Patient",
        "mobile": "0000000000"
    }
    response = client.put("patients/ghost-id", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["message"] == "Patient not found"


def test_get_patients_list(client):
    response = client.get("/patients/?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["patient_list"][0].get('patient_id') == "12345678-1234-5678-1234-567812345778"
    assert isinstance(data["data"]["patient_list"], list)


def test_get_patients_details_with_appointment_list(client):
    response = client.get("/patients/12345678-1234-5678-1234-567812345778")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Patients fetched successfully."
    assert "list_of_appointments" in data["data"]
    assert data["data"]["list_of_appointments"] == ["2025-08-29"]


def test_get_patients_list_on_basis_of_mobile(client):
    pass
