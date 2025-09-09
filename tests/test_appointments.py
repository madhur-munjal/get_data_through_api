from fastapi.testclient import TestClient

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.main import app
from .conftest import mock_get_db, mock_get_current_doctor_id

client = TestClient(app)
app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_current_doctor_id] = mock_get_current_doctor_id


def test_create_appointments():
    payload = {
        "patient": {
            "patient_id": "12345678-1234-5678-1234-567812345778",
            "firstName": "sample_name",
            "lastName": "string",
            "age": 25,
            "mobile": "123456781",
            "gender": "male",
            "address": "pune",
            "bloodGroup": "A+",
            "weight": 80.5,
            "bloodPressureUpper": 0,
            "bloodPressureLower": 0,
            "temperature": 0,
            "temperatureType": "celsius"
        },
        "scheduled_date": "09/09/2025",
        "scheduled_time": "10:10:10"
    }
    response = client.post("/appointments/create_appointment", json=payload)
    print(response.json())
    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True


def test_update_appointment():
    payload = {
        "scheduled_date": "09/10/2025",
        "scheduled_time": "11:00:00"
    }
    response = client.put("/appointments/update_appointment/123", json=payload)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Appointment updated successfully."
    assert data["data"]["scheduled_date"] == "2025-09-10"
    assert data["data"]["scheduled_time"] == "11:00:00"


def test_get_appointments_data():
    response = client.get("/appointments/?page=1&page_size=20")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Successfully fetched appointment lists."
    assert isinstance(data["data"], dict)
    assert data["data"]["appointment_list"][0]["appointment_id"] == "12345678-1234-5678-1234-567812345678"
    assert data["data"]["appointment_list"][0]["scheduled_date"] == '08/29/2025'  # date(2025, 8, 29)
    assert data["data"]["appointment_list"][0]["scheduled_time"] == '10:00:00'  # time(10, 0).isoformat()
    assert data["data"]["appointment_list"][0]["patient_id"] == "12345678-1234-5678-1234-567812345778"
    assert data["data"]["appointment_list"][0]["type"] == 0
    assert data["data"]["appointment_list"][0]["status"] == 0
    assert data["data"]["appointment_list"][0]["firstName"] == "John"
    assert data["data"]["appointment_list"][0]["lastName"] == "Doe"


def test_get_patient_details_through_appointment_id():
    appointment_id = "12345678-1234-5678-1234-567812345678"  # kept as similar of mock appointment id
    response = client.get(f"/appointments/{appointment_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["message"] == "successfully fetched visit datails"


def test_get_appointments_by_date():
    response = client.get("/appointments/get_appointment_by_date/2025-09-10")
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Successfully fetched appointment lists for date 2025-09-10." in data["message"]
    assert isinstance(data["data"], list)
    assert data["data"][0]["scheduled_date"] == "08/29/2025"
