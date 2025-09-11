from typing import Optional
from uuid import UUID
from src.auth_utils import pwd_context, hash_password
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.auth_utils import hash_password
from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import get_current_user_payload, require_owner
from src.models.response import APIResponse
from src.models.users import UserIDRequest, UserOut, UserCreate, UpdateLoginRecord
from src.models.staff import StaffCreate, StaffOut, DeleteStaffRequest, StaffUpdate
from src.schemas.tables.staff import Staff
from src.schemas.tables.users import User
from src.dependencies import get_current_user_payload

router = APIRouter(
    prefix="/settings", tags=["settings"], responses={404: {"error": "Not found"}}
    # , dependencies=[Depends(require_owner)]
)


@router.post("/update_login_user") #, response_model=APIResponse[StaffOut])
def update_login_user(
        updated_login_data: UpdateLoginRecord,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user_payload),
):
    """Used to update data of login user(doctor/staff)."""
    # print("****** Updated Login Data *****", updated_login_data)
    # print(current_user)
    username = current_user.get("sub")
    login_details = db.query(Staff).filter_by(username=username).first()
    if login_details is None:
        login_details = db.query(User).filter_by(username=username).first()

    if not login_details:
        raise HTTPException(status_code=404, detail="login username does not found in staff and user table.")

    if updated_login_data.password:
        if not pwd_context.verify(updated_login_data.current_password, login_details.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect.")

    # if updated_login_data.password != updated_login_data.confirm_password:
    #     raise HTTPException(status_code=400, detail="New password and confirm password do not match.")

    if updated_login_data.mobile:
        login_details.mobile = updated_login_data.mobile

    if updated_login_data.password:
        hashed_pw = hash_password(updated_login_data.password)
        login_details.password = hashed_pw
    db.commit()
    db.refresh(login_details)
    return APIResponse(
        status_code=200,
        success=True,
        message="Login user details updated successfully.",
        data=UserOut.model_validate(login_details) if isinstance(login_details, User) else StaffOut.model_validate(login_details),
    ).model_dump()

    #
    # db.commit()
    # db.refresh(staff_details)
    # if staff_updated_data.sendToEmail:
    #     # send email to staff with updated details
    #     from src.utility import send_msg_on_email as send_email
    #     subject = "Your staff account details have been updated"
    #     body = f"""
    #     Dear {staff_details.firstName},
    #
    #     Your staff account details have been updated. Here are your updated details:
    #
    #     First Name: {staff_details.firstName}
    #     Last Name: {staff_details.lastName}
    #     Email: {staff_details.email}
    #     Country: {staff_details.country}
    #     Mobile: {staff_details.mobile}
    #     Username: {staff_details.username}
    #     Role: {staff_details.role}
    #
    #     If you did not request this change, please contact the administrator immediately.
    #
    #     Best regards,
    #     SmartHealApp Management Team
    #     """
    #     send_email(to_email=staff_details.email, message=body, Subject=subject)
    # return APIResponse(
    #     status_code=200,
    #     success=True,
    #     message="staff details updated successfully.",
    #     data=StaffOut.model_validate(staff_details),
    # ).model_dump()