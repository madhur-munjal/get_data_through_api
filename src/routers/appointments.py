from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import get_current_user
# from src.models.users import UserIDRequest, UserOut, UserCreate
# from src.models.staff import StaffCreate, StaffOut
from src.models.appointments import AppointmentCreate, AppointmentOut
from src.models.response import APIResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.patients import Patient
from src.utility import save_data_to_db

router = APIRouter(
    prefix="/appointments", tags=["appointments"], responses={404: {"error": "Not found"}}
)


@router.post("/appointments", response_model=APIResponse[AppointmentOut])
def create_appointment(
        appointment: AppointmentCreate,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user),
):
    """Register a new appointment."""

    # Extract patient data
    patient_data = appointment.patient.dict()
    save_patient_data = save_data_to_db(patient_data, Patient, db)  # Create patient here
    print(f"save_patient_data in routers/appointments.py: {save_patient_data}")
    print(type(save_patient_data))
    patient_id = save_patient_data.patient_id
    data = appointment.dict()
    data.update({"doctor_id": doctor_id})
    print(f"data in routers/appointments.py: {data}")
    db_appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id,
                                 scheduled_time=data["scheduled_time"], status=data["status"])
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New Appointment created.",
        data=AppointmentOut.model_validate(db_appointment),
    ).model_dump()
