from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import get_current_user
from src.models.response import APIResponse
from src.models.visits import VisitOut, VisitIn
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.visits import Visit

router = APIRouter(
    prefix="/visits", tags=["visits"], responses={404: {"error": "Not found"}}
)


# APIResponse(
#         status_code=404,
#         success=False,
#         message="Not found",
#         data=None,
#     ).model_dump())


# @router.get("/visits_list", response_model=APIResponse)
# def get_visits(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
#     """Fetch all users."""
#     visits = db.query(Visit).all()
#     user_dtos = [VisitOut.model_validate(visit) for visit in visits]
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message="successfully fetched visits",
#         data=user_dtos,
#     ).model_dump()


@router.post("/add_visits", response_model=APIResponse[VisitOut])
def add_visits(
        visit_data: VisitIn,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user),
):
    """Register a new visit details."""
    appointment_id = visit_data.appointment_id
    # prescription = visit_data.prescription
    # follow_up = visit_data.follow_up
    # print(
    #     f"Adding visit for appointment ID: {appointment_id}, doctor ID: {doctor_id}, follow-up: {follow_up}")
    # print(f"type of appointment_id: {type(appointment_id)}")
    # print(f"str(appointment_id): {str(appointment_id)}")
    # uuid_appointment_id = UUID(appointment_id)
    str_appointment_id = str(appointment_id)
    appointment_details = db.query(Appointment).filter_by(id=str_appointment_id).first()
    print(f"appointment_details: {appointment_details}")
    if appointment_details:
        patient_id = appointment_details.patient_id
    else:
        print(f"Appointment with ID {appointment_id} not found.")
        return APIResponse(
            status_code=200,
            success=False,
            message=f"Appointment with ID {appointment_id} not found.",
            data=None,
        ).model_dump()
    # print(f"type of patient_id: {type(patient_id)}")
    # print(f"type of doctor_id: {type(doctor_id)}")
    medicationDetails = [med.json() for med in visit_data.medicationDetails]
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
    db.commit()
    db.refresh(db_visit)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Visit was successfully added.",
        data=VisitOut.model_validate(db_visit),
    ).model_dump()
