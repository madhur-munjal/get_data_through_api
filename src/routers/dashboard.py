from calendar import month_name
from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import desc
from sqlalchemy import or_, extract
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id, require_owner
from src.models.appointments import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentResponse,
    AppointmentUpdate,
    AppointmentById,
    PaginatedAppointmentResponse
)
from src.models.enums import AppointmentType, AppointmentStatus
from src.models.response import APIResponse
from src.models.visits import VisitAllResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.patients import Patient
from src.schemas.tables.visits import Visit
from src.utility import save_data_to_db, get_appointment_status

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"error": "Not found"}}
    # ,
    # dependencies=[Depends(require_owner)]
)


@router.post("/search/{text}", response_model=APIResponse[AppointmentOut])
def create_appointment(
        text: str,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id)
):
    """
    Used to filter patients and staff details through name and mobile.

    data response like {"patient":[{patient1 details}, {patient2 details}],
					"staff":[{staff1 details}, {staff2 details}]}.
					"""
    patient_data = appointment.patient.dict(exclude_unset=True)
    patient_id = patient_data.get("patient_id")
