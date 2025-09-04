from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id, require_owner
from src.dependencies import get_current_user_payload
from src.models.enums import AppointmentStatus
from src.models.response import APIResponse
from src.models.appointments import AppointmentResponse, AppointmentById
from src.models.visits import VisitOut, VisitCreate, VisitResponse, VisitAllResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.patients import Patient
from src.schemas.tables.visits import Visit

router = APIRouter(
    prefix="/visits", tags=["visits"], responses={404: {"error": "Not found"}}, dependencies=[Depends(require_owner)]
)


@router.post("/add_visits", response_model=APIResponse[VisitOut])
def add_visits(
        visit_data: VisitCreate,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user_payload),
):
    """Register a new visit details."""
    appointment_id = visit_data.appointment_id
    str_appointment_id = str(appointment_id)
    appointment_details = db.query(Appointment).filter_by(id=str_appointment_id).first()
    if appointment_details:
        patient_id = appointment_details.patient_id
    else:
        return APIResponse(
            status_code=200,
            success=False,
            message=f"Appointment with ID {appointment_id} not found.",
            data=None,
        ).model_dump()
    db_visit = Visit(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_id=appointment_id,
        analysis=visit_data.analysis,
        advice=visit_data.advice,
        tests=visit_data.tests,
        followUpVisit=visit_data.followUpVisit,
        medicationDetails=[med.dict() for med in visit_data.medicationDetails],
    )
    db.add(db_visit)

    # 2. Update patient's lastVisit field
    patient = db.query(Patient).filter_by(patient_id=patient_id, assigned_doctor_id=doctor_id).first()
    if patient:
        if (
                not patient.lastVisit
                or appointment_details.scheduled_date > patient.lastVisit
        ):
            patient.lastVisit = appointment_details.scheduled_date

    # 2. Update appointment status as completed.
    appointment_details.status = AppointmentStatus.COMPLETED.value

    db.commit()
    db.refresh(db_visit)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Visit was successfully added.",
        data=VisitOut.model_validate(db_visit),
    ).model_dump()


@router.get("/visits_list/{patient_id}")  # , response_model=APIResponse[VisitResponse])
def get_visits_by_patient_id(
        patient_id: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user_payload),
):
    """Fetch visit details by patient id."""
    visits = db.query(Visit).filter(Visit.patient_id == patient_id).all()
    if not visits:
        raise HTTPException(
            status_code=404, detail=f"No visit by Patient id {patient_id}"
        )
    # visit_details = [convert_visit_to_response(v) for v in visits]
    visit_details = [VisitResponse.from_row(row) for row in visits]
    return APIResponse(
        status_code=200,
        success=True,
        message="successfully fetched visits",
        data=visit_details,
    ).model_dump()


@router.get("/visit_details/")  # , response_model=APIResponse[VisitResponse])
def get_visit_details(
        appointment_id: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user_payload),
):
    """Fetch visit details by patient id."""
    visit = db.query(Visit).filter_by(appointment_id=appointment_id).first()
    if not visit:
        appointment_details = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment_details:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return APIResponse(
            status_code=200,
            success=True,
            message=f"Successfully fetched appointment details.",
            data=AppointmentById.from_row(appointment_details)
            # PatientOut.from_row(appointment_details)  # [PatientOut.from_row(p) for p in appointment_details]
        ).model_dump()
        # raise HTTPException(
        #     status_code=404, detail=f"No visit found by Appointment id {appointment_id}"
        # )
    # visit_details = [VisitResponse.from_row(row) for row in visits]
    # visit_patient_details = [{row.created_at.date(): row.id} for row in visits]
    return APIResponse(
        status_code=200,
        success=True,
        message="successfully fetched visit datails",
        data=VisitAllResponse.from_visit_row(visit),
    ).model_dump()


@router.get("/visits_date_list/{patient_id}")  # , response_model=APIResponse[VisitResponse])
def get_patient_details_with_visits_dates(
        patient_id: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user_payload),
):
    """Fetch patient details with their previous visit dates by patient id."""
    patient_details = db.query(Patient).filter_by(patient_id=patient_id).first()
    visits = db.query(Visit).filter(Visit.patient_id == patient_id).all()
    if not visits:
        raise HTTPException(
            status_code=404, detail=f"No visit by Patient id {patient_id}"
        )
    # visit_details = [convert_visit_to_response(v) for v in visits]
    visit_dates_details = [{row.created_at.date(): row.id} for row in visits]
    return APIResponse(
        status_code=200,
        success=True,
        message="successfully fetched patients details with visits date",
        data={'patient_details': patient_details, 'visit_dates_details': visit_dates_details},
    ).model_dump()


@router.get("/get_date_patient_wise_visits_details/")  # , response_model=APIResponse[VisitResponse])
def get_date_patient_wise_visit_details(
        patient_id: str,
        scheduled_date: date = Query(..., description="Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Fetch patient details with their previous visit dates by patient id."""
    # patient_details = db.query(Patient).filter_by(patient_id=patient_id).first()
    # visits = db.query(Visit).filter_by(doctor_id=doctor_id,patient_id=patient_id).all()
    visits = db.query(Visit).join(Appointment).filter(
            Visit.doctor_id == doctor_id,
            Visit.patient_id == patient_id,
            Appointment.scheduled_date == scheduled_date
        ).first()

    if not visits:
        raise HTTPException(
            status_code=404, detail=f"No visit by Patient id {patient_id} on date {scheduled_date}"
        )
    return APIResponse(
        status_code=200,
        success=True,
        message="successfully fetched patients details with visits date",
        data=VisitAllResponse.from_visit_row(visits),
    ).model_dump()
