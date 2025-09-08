from datetime import date, time
from uuid import UUID

from fastapi.testclient import TestClient

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.main import app
from .conftest import MockQueryChain


class MockPatient:
    def __init__(self, firstName, lastName):
        self.firstName = firstName
        self.lastName = lastName


class MockAppointment:
    def __init__(self):
        self.id = "12345678-1234-5678-1234-567812345678"
        self.scheduled_date = date(2025, 8, 29)
        self.scheduled_time = time(10, 0)
        self.patient_id = "87654321-4321-8765-4321-876543218765"
        self.patient = MockPatient("John", "Doe")
        self.type = "new"
        self.status = "scheduled"


def mock_get_db():
    class MockSession:
        def query(self, model):
            return MockQueryChain([MockAppointment()])

    return MockSession()


def mock_get_current_doctor_id():
    return UUID("11111111-1111-1111-1111-111111111111")


def test_get_appointments_list():
    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_current_doctor_id] = mock_get_current_doctor_id

    client = TestClient(app)

    response = client.get("/appointments/?page=1&page_size=20")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Successfully fetched appointment lists."
    assert isinstance(data["data"], list)
    assert data["data"][0]["appointment_id"] == "12345678-1234-5678-1234-567812345678"
    assert data["data"][0]["scheduled_date"] == date(2025, 8, 29).isoformat()
    assert data["data"][0]["scheduled_time"] == time(10, 0).isoformat()
    assert data["data"][0]["patient_id"] == "87654321-4321-8765-4321-876543218765"
    assert data["data"][0]["type"] == "new"
    assert data["data"][0]["status"] == "scheduled"
    assert data["data"][0]["firstName"] == "John"
    assert data["data"][0]["lastName"] == "Doe"
