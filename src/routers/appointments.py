from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import get_current_user
from src.models.appointments import AppointmentCreate, AppointmentOut
from src.models.response import APIResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.patients import Patient
from src.utility import save_data_to_db

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    responses={404: {"error": "Not found"}},
)


@router.get("/")
def get_appointment_data(db: Session = Depends(get_db)):
    results = db.query(Appointment).all()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched appointment lists.",
        data=[
            {
                "appointment_id": row.id,
                "scheduled_date": row.scheduled_date,
                "scheduled_time": row.scheduled_time,
                "patient_id": row.patient_id,
                "patient_first_name": row.patient.firstName,
                "patient_first_name": row.patient.lastName,
            }
            for row in results
        ],
    ).model_dump() # CHanged it to pydantic Type


@router.post("/create_appointment", response_model=APIResponse[AppointmentOut])
def create_appointment(
        appointment: AppointmentCreate,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user),
):
    """Register a new appointment.
    If enter new mobile number, then it will create under new patients record."""
    patient_mobile_number = appointment.patient.mobile
    db_user = db.query(Patient).filter_by(mobile=patient_mobile_number).first()
    if db_user:
        patient_id = db_user.patient_id
    else:
        # Extract patient data
        patient_data = appointment.patient.dict()
        save_patient_data = save_data_to_db(
            patient_data, Patient, db
        )
        patient_id = save_patient_data.patient_id
    data = appointment.dict()
    data.update({"doctor_id": doctor_id})
    db_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        scheduled_date=data["scheduled_date"],
        scheduled_time=data["scheduled_time"],
        type=data["type"],
        status=data["status"],
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New Appointment created.",
        data=AppointmentOut.model_validate(db_appointment),
    ).model_dump()
