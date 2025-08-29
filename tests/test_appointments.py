from src.main import app
from src.database import get_db
from src.dependencies import get_current_doctor_id
from fastapi.testclient import TestClient
from .conftest import MockQueryChain
from uuid import UUID


from uuid import UUID
from datetime import date, time

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

    # assert data["data"][0]["age"] == 30
    #
    # {
    #     "appointment_id": "20e8b7fa-4ec2-4f92-8330-099011dc8c50",
    #     "scheduled_date": "2025-08-27",
    #     "scheduled_time": "18:50:33",
    #     "patient_id": "47663479-d2b1-4e29-a16e-5bb085ed9c95",
    #     "type": "follow-up",
    #     "status": "scheduled",
    #     "firstName": "string",
    #     "lastName": "string"
    # },

