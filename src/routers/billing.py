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
from src.models.enums import AppointmentType, AppointmentStatus, PaymentStatus
from src.models.response import APIResponse
from src.models.billing import BillingCreate, BillingOut
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.patients import Patient
from src.schemas.tables.visits import Visit
from src.schemas.tables.billing import Billing
from src.utility import save_data_to_db, get_appointment_status

router = APIRouter(
    prefix="/billings",
    tags=["billings"],
    responses={404: {"error": "Not found"}}
    # ,
    # dependencies=[Depends(require_owner)]
)


@router.post("/create_billing")  #, response_model=APIResponse[AppointmentOut])
def create_billing(
        billing_details: BillingCreate,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id)
):
    """"""
    try:
        # Check if appointment exists
        billing_dict = billing_details.dict()

        appointment_id = billing_dict.pop("appointment_id", None)

        db_billing = Billing(**billing_details.model_dump())
        save_billing_data = save_data_to_db(billing_details.dict(), Billing, db)
        visit = db.query(Visit).filter_by(appointment_id=billing_details.appointment_id).first()
        visit.type = PaymentStatus.PAID.value
        db.commit()
        # db.refresh(db_appointment)
        return APIResponse(
            status_code=200,
            success=True,
            message=f"New Appointment created.",
            data=BillingOut.model_validate(save_billing_data),
        ).model_dump()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")


