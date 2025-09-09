from datetime import date, time


class MockColumn:
    def __init__(self, name):
        self.name = name


class MockTable:
    def __init__(self, column_names):
        self.columns = [MockColumn(name) for name in column_names]


class MockPatient:
    def __init__(self):
        self.patient_id = "12345678-1234-5678-1234-567812345778"
        self.gender = "male"
        self.address = "pune"
        self.assigned_doctor_id = "11111111-1111-1111-1111-111111111111"
        self.firstName = "John"
        self.lastName = "Doe"
        self.email = "sample@example.com"
        self.age = 30
        self.mobile = "1234567890"
        self.lastVisit = None
        self.bloodGroup = "O+"
        self.weight = 70.5
        self.bloodPressureUpper = 120
        self.bloodPressureLower = 80
        self.temperature = 98.6
        self.temperatureType = "celsius"

        # Simulate SQLAlchemy's __table__.columns
        self.__table__ = MockTable([
            "patient_id", "firstName", "lastName", "mobile", "email", "age", "gender", "email", "address",
            "assigned_doctor_id", "lastVisit",
            "bloodGroup", "weight", "bloodPressureUpper", "bloodPressureLower", "temperature",
            "temperatureType"
        ])


class MockAppointment:
    def __init__(self):
        self.id = "12345678-1234-5678-1234-567812345678"
        self.scheduled_date = date(2025, 8, 29)
        self.scheduled_time = time(10, 0)
        self.doctor_id = "11111111-1111-1111-1111-111111111111"
        self.patient_id = "12345678-1234-5678-1234-567812345778"
        self.patient = MockPatient()
        self.type = 0
        self.status = 0


class MockVisit:
    def __init__(self):
        self.id = "22345678-1234-5678-1234-567812345678"
        self.patient_id = "12345678-1234-5678-1234-567812345778"
        self.doctor_id = "11111111-1111-1111-1111-111111111111"
        self.appointment_id = "12345678-1234-5678-1234-567812345678"
        self.patient = MockPatient()
        self.analysis = "Sample analysis"
        self.advice = "Sample advice"
        self.tests = "Sample tests"
        self.followUpVisit = None
        self.medicationDetails = "Sample medication details"
        self.appointments = MockAppointment()
