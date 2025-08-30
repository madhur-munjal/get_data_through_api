from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import get_current_user_payload
from src.models.response import APIResponse
from src.models.visits import VisitOut, VisitCreate, VisitResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.visits import Visit
from src.schemas.tables.patients import Patient

router = APIRouter(
    prefix="/visits", tags=["visits"], responses={404: {"error": "Not found"}}
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
    print(appointment_details.scheduled_date_time)
    print(type(appointment_details.scheduled_date_time))

    if patient:
        if (
            not patient.lastVisit
            or appointment_details.scheduled_date_time.date() > patient.lastVisit
        ):  # visit_data.visit_date > patient.lastVisit:
            patient.lastVisit = appointment_details.scheduled_date_time.date()

    # 2. Update appointment status as completed.
    appointment_details.status = 2  # AppointmentStatus.COMPLETED.value

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


@router.get("/visits_list/{mobile}", response_model=APIResponse[VisitResponse])
def get_visits_by_patient_mobile(
    mobile: str, db: Session = Depends(get_db), current_user=Depends(get_current_user_payload)
):
    """Fetch visit details by mobile number."""
    patient_details = db.query(Patient).filter(Patient.mobile == mobile).first()
    if not patient_details:
        raise HTTPException(
            status_code=404, detail=f"No Patient found with mobile number {mobile}"
        )
    get_visits_by_patient_id(patient_details.patient_id, db)

    # visits = db.query(Patient).filter(Visit.patient_id == patient_id).all()


#     if not visits:
#         raise HTTPException(status_code=404, detail=f"No visit by Patient id {patient_id}")
#     # visit_details = [convert_visit_to_response(v) for v in visits]
#     visit_details =[ VisitResponse.from_row(row)
#             for row in visits
#         ]
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message="successfully fetched visits",
#         data=visit_details,
#     ).model_dump()
