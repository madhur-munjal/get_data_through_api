from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.auth_utils import hash_password
from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import require_admin_owner
from src.models.response import APIResponse

# from src.models.users import UserIDRequest, UserOut, UserCreate
from src.models.staff import StaffCreate, StaffOut, DeleteStaffRequest, StaffUpdate
from src.schemas.tables.staff import Staff
from src.schemas.tables.users import User
from src.utility import get_subscription_active_status_by_doctor

router = APIRouter(
    prefix="/staff",
    tags=["staff"],
    responses={404: {"error": "Not found"}},
    dependencies=[Depends(require_admin_owner)],
)


@router.post("/register", response_model=APIResponse[StaffOut])
def register(
    user: StaffCreate,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Register a new staff."""
    get_subscription_active_status = get_subscription_active_status_by_doctor(
        db, doctor_id
    )
    # if get_subscription_active_status is False:
    #     return APIResponse(
    #         status_code=200,
    #         success=False,
    #         message="Your subscription has expired. Please renew your subscription to access this feature.",
    #         data=None,
    #     ).model_dump()
    db_user = (
        db.query(Staff)
        .filter_by(doc_id=doctor_id)
        .filter_by(username=user.username)
        .first()
    )
    if db_user:
        return APIResponse(
            status_code=200, success=False, message="Username already exists", data=None
        ).model_dump()
    if db.query(Staff).filter_by(email=user.email).first():
        return APIResponse(
            status_code=200, success=False, message="Email already exists", data=None
        ).model_dump()
    # Need to re-validate as in some cases staff will join from one clinic to another
    hashed_pw = hash_password(user.password)
    db_user = Staff(
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        country=user.country,
        mobile=user.mobile,
        username=user.username,
        password=hashed_pw,
        doc_id=doctor_id,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    if user.sendToEmail:
        # send email to staff with updated details
        from src.utility import send_msg_on_email as send_email

        subject = "Your staff account details - SmartHealApp"
        body = f"""

        Here are your staff account details:

        First Name: {user.firstName}
        Last Name: {user.lastName}
        Email: {user.email}
        Country: {user.country}
        Mobile: {user.mobile}
        Username: {user.username}
        Password: {user.password}
        Role: {user.role}

        If you did not request this change, please contact the administrator immediately.

        Best regards,
        SmartHealApp Management Team
        """
        send_email(to_email=user.email, message=body, Subject=subject)

    return APIResponse(
        status_code=200,
        success=True,
        message=f"New staff account has been created successfully!",
        data=StaffOut.model_validate(db_user),
    ).model_dump()


@router.get("/staff_list", response_model=APIResponse)
def get_staff_list(
    doctor_id: UUID = Depends(get_current_doctor_id), db: Session = Depends(get_db)
):
    """Fetch all users."""
    users = db.query(Staff).filter(Staff.doc_id == doctor_id).all()
    user_dtos = [StaffOut.model_validate(user) for user in users]
    return APIResponse(
        status_code=200,
        success=True,
        message="Successfully fetched staff lists",
        data=user_dtos,
    ).model_dump()


# @router.get("/doc_wise_staff_list", response_model=APIResponse)
# def get_staff_list_by_doc_info(
#         email: Optional[str] = Query(None),
#         mobile: Optional[str] = Query(None),
#         doctor_id: UUID = Depends(get_current_doctor_id),
#         db: Session = Depends(get_db),
# ):
#     """Fetch staff details on the basis of doctors mobile or email."""
#     if not email and not mobile:
#         raise HTTPException(status_code=400, detail="Provide either email or mobile")
#
#     # staff_db = db.query(Staff).filter(Staff.doc_id == doctor_id).all()
#     staff_list = None
#     if email:
#         staff_list = db.query(Staff).join(Staff.doctor).filter(
#             Staff.doc_id == doctor_id,
#             User.email == email
#         ).all()
#     if not staff_list or mobile:
#         staff_list = db.query(Staff).join(Staff.doctor).filter(
#             Staff.doc_id == doctor_id,
#             User.mobile == mobile
#         ).all()
#     if not staff_list:
#         raise HTTPException(status_code=404, detail="No Staff found")
#
#     user_dtos = [StaffOut.model_validate(staff) for staff in staff_list]
#
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message="successfully fetched staff lists",
#         data=user_dtos,
#     ).model_dump()


@router.get("/staff_details/{staff_id}", response_model=APIResponse)
def get_staff_detail(
    staff_id: str,
    doctor_id: UUID = Depends(get_current_doctor_id),
    db: Session = Depends(get_db),
):
    """Fetch staff details."""
    staff_detail = db.query(Staff).filter_by(doc_id=doctor_id, id=staff_id).first()
    if not staff_detail:
        raise HTTPException(status_code=404, detail="Staff not found")
    # print([StaffOut.model_validate(staff_detail)])
    return APIResponse(
        status_code=200,
        success=True,
        message="Successfully fetched staff lists",
        data=StaffOut.model_validate(staff_detail),
    ).model_dump()


@router.post("/delete", response_model=APIResponse)
def delete_staff(
    delete_payload: DeleteStaffRequest,
    doctor_id: UUID = Depends(get_current_doctor_id),
    db: Session = Depends(get_db),
):
    user = db.query(Staff).filter_by(doc_id=doctor_id, id=delete_payload.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Staff with name {user.firstName} deleted successfully.",
        data=StaffOut.model_validate(user),
    ).model_dump()


@router.post("/update", response_model=APIResponse[StaffOut])
def update_staff(
    staff_updated_data: StaffUpdate,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Update staff details."""
    staff_details = db.query(Staff).filter(Staff.id == staff_updated_data.id).first()
    if not staff_details:
        raise HTTPException(status_code=404, detail="Staff not found")
    for field, value in staff_updated_data.dict(exclude_unset=True).items():
        if field != "id":
            setattr(staff_details, field, value)

    db.commit()
    db.refresh(staff_details)
    if staff_updated_data.sendToEmail:
        # send email to staff with updated details
        from src.utility import send_msg_on_email as send_email

        subject = "Your staff account details have been updated"
        body = f"""
        Dear {staff_details.firstName},

        Your staff account details have been updated. Here are your updated details:

        First Name: {staff_details.firstName}
        Last Name: {staff_details.lastName}
        Email: {staff_details.email}
        Country: {staff_details.country}
        Mobile: {staff_details.mobile}
        Username: {staff_details.username}
        Role: {staff_details.role}

        If you did not request this change, please contact the administrator immediately.

        Best regards,
        SmartHealApp Management Team
        """
        send_email(to_email=staff_details.email, message=body, Subject=subject)
    return APIResponse(
        status_code=200,
        success=True,
        message="Staff details updated successfully.",
        data=StaffOut.model_validate(staff_details),
    ).model_dump()
