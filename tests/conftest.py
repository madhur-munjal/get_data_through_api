from .mock_tables import MockAppointment, MockPatient, MockVisit
from fastapi.testclient import TestClient
import pytest
from src.main import app
from src.database import get_db
from src.dependencies import get_current_doctor_id

class MockQueryChain:
    def __init__(self, results):
        self._results = results
        self.joins = []
        self.count_called = False
        self.ordering = []

    def filter_by(self, **kwargs):
        return self

    def offset(self, offset):
        return self

    def outerjoin(self, target, onclause=None, isouter=True, full=False):
        # Store the join details for inspection if needed
        self.joins.append({
            "type": "outerjoin",
            "target": target,
            "onclause": onclause,
            "isouter": isouter,
            "full": full
        })
        return self  # Allow method chaining

    def join(self, target, onclause=None, isouter=False, full=False):
        self.joins.append({
            "type": "join",
            "target": target,
            "onclause": onclause,
            "isouter": isouter,
            "full": full
        })
        return self

    def count(self):
        self.count_called = True
        return 0  # Return mock count valu

    def order_by(self, *args):
        self.ordering.extend(args)
        return self

    def first(self, **kwargs):
        if self._results:
            return self._results[0]
        return None

    def limit(self, limit):
        return self

    def all(self):
        return self._results

    def add(self, obj):
        self._results.append(obj)

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_current_doctor_id] = mock_get_current_doctor_id
    return TestClient(app)

def mock_get_db(keep_model_empty=False):

    class MockSession:
        def __init__(self):
            self._added_objects = []
            self._committed = False
            self._refreshed = False

        def query(self, model):
            if keep_model_empty:
                return MockQueryChain([])

            if model.__name__ == "Appointment":
                return MockQueryChain([MockAppointment()])
            elif model.__name__ == "Patient":
                return MockQueryChain([MockPatient()])
            elif model.__name__ == "Visit":
                return MockQueryChain([MockVisit()])
            else:
                return MockQueryChain([])

        def add(self, obj):
            self._added_objects.append(obj)

        def commit(self):
            self._committed = True

        def refresh(self, obj):
            self._refreshed = True

    return MockSession()


def mock_get_current_doctor_id():
    return "11111111-1111-1111-1111-111111111111"
