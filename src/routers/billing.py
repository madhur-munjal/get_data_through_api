from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user_payload, get_current_doctor_id
from src.dependencies import require_admin_owner
from src.models.billing import BillingCreate, BillingOut, BillingDetails, BillingDeleteIn
from src.models.enums import PaymentStatus
from src.models.response import APIResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.billing import Billing
from src.schemas.tables.notifications import Notification
from src.utility import save_data_to_db

router = APIRouter(
    prefix="/billings",
    tags=["billings"],
    responses={404: {"error": "Not found"}},
    dependencies=[Depends(require_admin_owner)]
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
        doctor_id: UUID = Depends(get_current_doctor_id),
        startDate: str = Query(None, description="Filter by start date in YYYY-MM-DD format"),
        endDate: str = Query(None, description="Filter by end date in YYYY-MM-DD format"),
        type: str = Query(None, description="what type of transaction, cash, card, upi etc."),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1),

):
    """Get billing details."""
    query = db.query(Billing).filter(Billing.is_deleted == False).join(Billing.appointment).filter(
        Appointment.doctor_id == doctor_id)
    if not query:
        raise HTTPException(status_code=404, detail="Billing details not found.")

    # 📆 Date range filter: match between startDate and endDate
    if startDate and endDate:
        try:
            start_dt = datetime.fromisoformat(startDate)
            end_dt = datetime.fromisoformat(endDate)
            end_dt = end_dt.replace(hour=23, minute=59, second=59)

            # start_date_obj = datetime.strptime(startDate, "%Y-%m-%d").date()
            # end_date_obj = datetime.strptime(endDate, "%Y-%m-%d").date()
            query = query.filter(Billing.created_at.between(start_dt, end_dt))
        except ValueError:
            return APIResponse(
                status_code=200,
                success=True,
                message=f"ValueError wile filtering from startDate and EndDate.",
                data=None
            ).model_dump()

    if type:
        query = query.filter(Billing.type.ilike(type))  # (func.lower(Billing.type) == type.lower())
    # query = query.order_by(Billing.created_at.desc())
    total_records = query.count()
    offset = (page - 1) * page_size
    query = query.order_by(Billing.created_at.desc()).offset(offset).limit(page_size).all()

    return APIResponse(
        status_code=200,
        success=True,
        message="Billing details fetched successfully.",
        data={"page": page, "page_size": page_size, "total_records": total_records,
              "billing_list": [BillingDetails.from_billing_row(row) for row in query]}
    ).model_dump()


@router.get("/billing_summary")
def get_billing_summary(
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        startDate: str = Query(None, description="Filter by start date in YYYY-MM-DD format"),
        endDate: str = Query(None, description="Filter by end date in YYYY-MM-DD format"),
        # type: str = Query(None, description="what type of transaction, cash, card, upi etc."),
        # page: int = Query(1, ge=1),
        # page_size: int = Query(20, ge=1),
):
    query = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).outerjoin(Appointment.billing).filter(
        Billing.is_deleted == False)
    # query = db.query(Billing).join(Billing.appointment).filter(Appointment.doctor_id == doctor_id)
    if not query:
        raise HTTPException(status_code=404, detail="No Appointment details found.")
    if startDate and endDate:
        try:
            start_dt = datetime.fromisoformat(startDate)
            end_dt = datetime.fromisoformat(endDate)
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(Billing.created_at.between(start_dt, end_dt))
        except ValueError:
            return APIResponse(
                status_code=200,
                success=True,
                message=f"Error while filtering from startDate and EndDate.",
                data=None
            ).model_dump()

    try:
        total_earning = query.with_entities(func.coalesce(func.sum(Billing.amount), 0)).scalar()
        completed_payment_ids = query.filter(Appointment.payment_status == PaymentStatus.PAID.value).with_entities(
            distinct(Appointment.id))
        completed_payment = completed_payment_ids.count()
        pending_payment = query.filter(Appointment.payment_status == PaymentStatus.UNPAID.value, ).with_entities(
            distinct(Appointment.id)).count()
        payment_details = query.with_entities(Billing.type, func.coalesce(func.sum(Billing.amount), 0).label('total')) \
            .group_by(Billing.type).having(func.sum(Billing.amount) > 0).all()

        payment_summary = {ptype: total for ptype, total in payment_details}

        fixed_types = ["Cash", "Card", "UPI"]
        final_result = [{"type": t, "total": payment_summary.get(t, 0)} for t in fixed_types]

        return APIResponse(
            status_code=200,
            success=True,
            message="Billing summary fetched successfully.",
            data={
                "totalEarning": total_earning,
                "completedPayment": completed_payment,
                "pendingPayment": pending_payment,
                "paymentDetails": final_result
            }
        ).model_dump()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error fetching billing summary: {str(ex)}")


@router.post("/delete_billing")
def soft_delete_billing(
        ids_to_delete: BillingDeleteIn,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Delete billing details on basis of billing id."""
    rows_updated = db.query(Billing).filter(Billing.billing_id.in_(ids_to_delete.ids_to_delete)).update(
    {Billing.is_deleted: True},
    synchronize_session=False
)
    db.commit()
    if rows_updated == 0:
        raise HTTPException(status_code=404, detail="No billing records found for given IDs")
    # billing.is_deleted = True
    # billing.deleted_at = datetime.utcnow()
    # db.commit()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"{rows_updated} billing records marked as deleted",
        data=f"Billing {ids_to_delete} marked as deleted"
    ).model_dump()
