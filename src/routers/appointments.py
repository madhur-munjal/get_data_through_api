from datetime import date, datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id, require_owner
from src.dependencies import get_current_user_payload
from src.models.appointments import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentResponse,
)
from src.models.enums import AppointmentType
from src.models.patients import PatientOut
from src.models.response import APIResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.patients import Patient
from src.utility import save_data_to_db, get_appointment_status

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    responses={404: {"error": "Not found"}},
    dependencies=[Depends(require_owner)]
)


@router.post("/create_appointment", response_model=APIResponse[AppointmentOut])
def create_appointment(
        appointment: AppointmentCreate,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user_payload),
):
    """Register a new appointment.
    If enter new mobile number, then it will create under new patients record."""
    patient_mobile_number = appointment.patient.mobile
    db_user = db.query(Patient).filter_by(assigned_doctor_id=doctor_id, mobile=patient_mobile_number).first()
    if db_user:
        patient_id = db_user.patient_id
        type = AppointmentType.FOLLOW_UP.value
    else:
        # Extract patient data
        patient_data = appointment.patient.dict()
        patient_data["assigned_doctor_id"] = doctor_id
        save_patient_data = save_data_to_db(patient_data, Patient, db)
        patient_id = save_patient_data.patient_id
        type = AppointmentType.NEW.value
    data = appointment.dict()
    data.update({"doctor_id": doctor_id})
    db_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        scheduled_date=datetime.strptime(data["scheduled_date"], "%m/%d/%Y").date(),
        scheduled_time=datetime.strptime(data["scheduled_time"], "%H:%M:%S").time(),
        type=type,
        status=get_appointment_status(datetime.strptime(f"{data["scheduled_date"]} {data["scheduled_time"]}", "%m/%d/%Y %H:%M:%S")
                                      )
# data["scheduled_date_time"])  # AppointmentStatus.UPCOMING.value
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


@router.put("/update_appointment/{appointment_id}", response_model=APIResponse[AppointmentOut])
def update_appointment(appointment_id: int, update_data: AppointmentCreate, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter_by(id=appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    data = update_data.dict(exclude_unset=True)

    # Convert known fields
    if "scheduled_date" in data:
        data["scheduled_date"] = datetime.strptime(data["scheduled_date"], "%m/%d/%Y").date()

    if "appointment_time" in data:
        data["scheduled__time"] = datetime.strptime(data["scheduled_time"], "%H:%M:%S").time()

    # Apply all fields
    for key, value in data.items():
        setattr(appointment, key, value)

    # for key, value in update_data.dict(exclude_unset=True).items():
    #     setattr(appointment, key, value)

    db.commit()
    db.refresh(appointment)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Appointment updated successfully.",
        data=AppointmentOut.model_validate(appointment),
    ).model_dump()


@router.get("", response_model=APIResponse[list[AppointmentResponse]])
def get_appointment_data(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1),
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    offset = (page - 1) * page_size
    results = db.query(Appointment).filter_by(doctor_id=doctor_id).order_by(
        Appointment.scheduled_date).offset(offset).limit(page_size).all()
    # TODO need to add time as well
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched appointment lists.",
        data=[AppointmentResponse.from_row(p) for p in results]
    ).model_dump()
    #     [
    #         {
    #             "appointment_id": row.id,
    #             "scheduled_date": row.scheduled_date,
    #             "scheduled_time": row.scheduled_time,
    #             "patient_id": row.patient_id,
    #             "firstName": row.patient.firstName,
    #             "lastName": row.patient.lastName,
    #         }
    #         for row in results
    #     ],


# @router.get("/id", response_model=APIResponse[list[PatientOut]])
# def get_appointment_data(
#         # page: int = Query(1, ge=1),
#         # page_size: int = Query(20, ge=1),
#         db: Session = Depends(get_db),
#         doctor_id: UUID = Depends(get_current_doctor_id),
# ):
#     # offset = (page - 1) * page_size
#     results = db.query(Appointment).filter_by(doctor_id=doctor_id).order_by(Appointment.scheduled_date_time.desc()).offset(offset).limit(page_size).all()
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message=f"Successfully fetched appointment lists.",
#         data=[AppointmentResponse.from_row(p) for p in results]
#     ).model_dump()

@router.get("/id", response_model=APIResponse[PatientOut])
def get_patient_details_through_appointment_id(appointment_id: str, db: Session = Depends(get_db)):
    appointment_details = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment_details:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # patient = db.query(Patient).filter(Patient.patient_id == appointment.patient_id).first()
    # if not patient:
    #     raise HTTPException(status_code=404, detail="Patient not found")
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched appointment details.",
        data=PatientOut.from_row(appointment_details)  # [PatientOut.from_row(p) for p in appointment_details]
    ).model_dump()


@router.get(
    "/get_appointment_by_date", response_model=APIResponse[list[AppointmentResponse]]
)
def get_appointment_by_date(
        appointment_date: date = Query(..., description="Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user_payload),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    results = (
        db.query(Appointment)
        .filter_by(doctor_id=doctor_id, scheduled_date=appointment_date)
        .all()
    )
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched appointment lists for date {appointment_date}.",
        data=[AppointmentResponse.from_row(row) for row in results],
    ).model_dump()
