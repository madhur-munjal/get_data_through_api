from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth_utils import hash_password, pwd_context
from src.database import get_db
from src.dependencies import get_current_doctor_id, get_current_user_payload
from src.models.billing import DoctorsBillingInput
from src.models.response import APIResponse
from src.models.staff import StaffOut
from src.models.users import UserOut, UpdateLoginRecord
from src.schemas.tables.doctor_payment_details import DoctorPaymentDetails
from src.schemas.tables.staff import Staff
from src.schemas.tables.users import User

router = APIRouter(
    prefix="/settings", tags=["settings"], responses={404: {"error": "Not found"}}
    # , dependencies=[Depends(require_owner)]
)


@router.post("/general")  # , response_model=APIResponse[StaffOut])
def update_login_user(
        updated_login_data: UpdateLoginRecord,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user_payload),
):
    """Used to update data of login user(doctor/staff)."""
    username = current_user.get("sub")
    login_details = db.query(Staff).filter_by(username=username).first()
    if login_details is None:
        login_details = db.query(User).filter_by(username=username).first()

    if not login_details:
        raise HTTPException(status_code=404, detail="Login username does not found in staff and user table.")

    if updated_login_data.current_password is None and updated_login_data.password:
        raise HTTPException(status_code=400, detail="Current password is required to set a new password.")

    if updated_login_data.password is None and updated_login_data.current_password:
        raise HTTPException(status_code=400, detail="password is required to set a new password.")

    if updated_login_data.current_password:
        if not pwd_context.verify(updated_login_data.current_password, login_details.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect.")
        if updated_login_data.password:
            hashed_pw = hash_password(updated_login_data.password)
            login_details.password = hashed_pw

    if updated_login_data.mobile:
        login_details.mobile = updated_login_data.mobile

    db.commit()
    db.refresh(login_details)
    return APIResponse(
        status_code=200,
        success=True,
        message="Login user details updated successfully.",
        data=UserOut.model_validate(login_details) if isinstance(login_details, User) else StaffOut.model_validate(
            login_details),
    ).model_dump()


@router.post("/billing")  # , response_model=APIResponse[StaffOut])
def upsert_billing(data: DoctorsBillingInput,
                   db: Session = Depends(get_db),
                   doctor_id: UUID = Depends(get_current_doctor_id),
                   current_user=Depends(get_current_user_payload),
                   ):
    existing = db.query(DoctorPaymentDetails).filter_by(doctor_id=doctor_id).first()
    if existing:
        # Update existing billing record
        existing.name = data.name
        existing.upi_id = data.upi_id
        existing.currency = data.currency
    else:
        # Create new billing record
        billing_data = data.model_dump()
        billing_data['doctor_id'] = doctor_id
        # import pdb; pdb.set_trace()
        new_billing = DoctorPaymentDetails(**billing_data)
        db.add(new_billing)

    db.commit()
    return APIResponse(
        status_code=200,
        success=True,
        message="Billing details were updated successfully.",
        data=None
    ).model_dump()
