from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth_utils import hash_password
from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import get_current_user
from src.models.response import APIResponse
from src.schemas.tables.patients import Patient
from src.utility import save_data_to_db
# from src.models.users import UserIDRequest, UserOut, UserCreate
# from src.models.staff import StaffCreate, StaffOut
from src.models.appointments import AppointmentCreate, AppointmentRead
from src.schemas.tables.appointments import Appointment

router = APIRouter(
    prefix="/staff", tags=["staff"], responses={404: {"error": "Not found"}}
)


@router.post("/appointments", response_model=APIResponse[AppointmentRead])
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
    current_user=Depends(get_current_user),
):
    """Register a new appointment."""

    # Extract patient data
    patient_data = appointment.patient.dict()
    save_data_to_db(patient_data, Patient, get_db)  # Create patient here

    data = appointment.dict()
    data.update({"doctor_id": doctor_id})
    db_appointment = Appointment(data)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New Appointment created.",
        data=Appointment.model_validate(db_appointment),
    ).model_dump()
