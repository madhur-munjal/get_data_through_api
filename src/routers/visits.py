from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user
from src.models.response import APIResponse
from src.models.visits import VisitOut, VisitCreate
from uuid import UUID
from src.dependencies import get_current_doctor_id
from src.schemas.tables.visits import Visit
from src.schemas.tables.appointments import Appointment
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
        visit_data: VisitCreate,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user),
):
    """Register a new appointment."""
    appointment_id = visit_data.appointment_id
    prescription = visit_data.prescription
    follow_up = visit_data.follow_up
    print(f"Adding visit for appointment ID: {appointment_id}, doctor ID: {doctor_id}, prescription: {prescription}, follow-up: {follow_up}")
    appointment_details = db.query(Appointment).filter_by(id=appointment_id).first()
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
    db_visit = Visit(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_id=appointment_id,
        prescription=prescription,
        follow_up=follow_up,
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
