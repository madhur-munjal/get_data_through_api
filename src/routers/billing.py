from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user_payload, get_current_doctor_id
from src.models.billing import BillingCreate, BillingOut, BillingDetails
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
        current_user=Depends(get_current_user_payload),
        doctor_id: UUID = Depends(get_current_doctor_id)
):
    try:
        updated_by = current_user.get('firstName') + " " + current_user.get('lastName') if current_user.get(
            'lastName') else current_user.get('firstName')
        db_billing = Billing(**billing_details.model_dump(), created_by=updated_by)
        appointment_db = db.query(Appointment).filter_by(id=billing_details.appointment_id).first()
        if not appointment_db:
            raise HTTPException(status_code=404, detail="Appointment not found")
        appointment_db.payment_status = PaymentStatus.PAID.value
        db.add(db_billing)
        db.commit()
        db.refresh(db_billing)
        created_billing_id = db_billing.billing_id
        created_appointment_id = db_billing.appointment.id
        notification_data = {'doctor_id': doctor_id, 'appointment_id': created_appointment_id,
                             'billing_id': created_billing_id, 'firstName': appointment_db.patient.firstName,
                             'lastName': appointment_db.patient.lastName,
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


@router.get("/billing_details")
def get_billing_details(
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id)
):
    """Get billing details."""
    billing_details = db.query(Billing).join(Billing.appointment).filter(Appointment.doctor_id == doctor_id).all()
    # patient_billing_details = billing_details
    if not billing_details:
        raise HTTPException(status_code=404, detail="Billing details not found.")
    return APIResponse(
        status_code=200,
        success=True,
        message="Billing details fetched successfully.",
        data=[BillingDetails.from_billing_row(row) for row in billing_details]
    ).model_dump()