from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user_payload
from src.models.billing import BillingCreate, BillingOut
from src.models.enums import PaymentStatus
from src.models.response import APIResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.billing import Billing
from src.schemas.tables.notifications import Notification
from src.utility import save_data_to_db

router = APIRouter(
    prefix="/billings",
    tags=["billings"],
    responses={404: {"error": "Not found"}}
    # ,
    # dependencies=[Depends(require_owner)]
)


@router.post("/create_billing")  # , response_model=APIResponse[AppointmentOut])
def create_billing(
        billing_details: BillingCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user_payload)
):
    """"""
    try:
        db_billing = Billing(**billing_details.model_dump())
        appointment_db = db.query(Appointment).filter_by(id=billing_details.appointment_id).first()
        if not appointment_db:
            raise HTTPException(status_code=404, detail="Appointment not found")
        appointment_db.payment_status = PaymentStatus.PAID.value
        db.add(db_billing)
        db.commit()
        db.refresh(db_billing)
        updated_by = current_user.get('firstName') + " " + current_user.get('lastName') if current_user.get(
            'lastName') else current_user.get('firstName')
        notification_data = {'firstName': appointment_db.patient.firstName, 'lastName': appointment_db.patient.lastName,
                             'type': "payment", 'message': 'Payment Received', 'updated_by': updated_by,
                             }
        save_data_to_db(notification_data, Notification, db)

        return APIResponse(
            status_code=200,
            success=True,
            message=f"New Billing created.",
            data=BillingOut.model_validate(db_billing)
        ).model_dump()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")
