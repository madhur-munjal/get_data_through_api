import os
from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from src.auth_utils import hash_password, pwd_context
from src.constants import total_appointments_basic_plan
from src.database import get_db
from src.dependencies import get_current_doctor_id, get_current_user_payload
from src.models.billing import DoctorsBillingInput
from src.models.response import APIResponse
from src.models.staff import StaffOut
from src.models.subscription import SubscriptionOutWithPlan
from src.models.users import UserOut
from src.schemas.tables.doctor_payment_details import DoctorPaymentDetails
from src.schemas.tables.plans import Plan
from src.schemas.tables.staff import Staff
from src.schemas.tables.subscription import Subscription
from src.schemas.tables.users import User
from src.schemas.tables.appointments import Appointment

router = APIRouter(
    prefix="/settings", tags=["settings"], responses={404: {"error": "Not found"}}
    # , dependencies=[Depends(require_owner)]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/general")  # , response_model=APIResponse[StaffOut])
async def update_login_user(
        mobile: Optional[str] = Form(None),
        current_password: Optional[str] = Form(None),
        password: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        # doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user_payload),
):
    """Used to update data of login user(doctor/staff)."""
    updated_login_data = {
        "mobile": mobile,
        "current_password": current_password,
        "password": password
    }

    username = current_user.get("sub")
    login_details = db.query(Staff).filter_by(username=username).first()

    if login_details is None:
        login_details = db.query(User).filter_by(username=username).first()

    if not login_details:
        raise HTTPException(status_code=404, detail="Login username does not found in staff and user table.")

    if image:
        contents = await image.read()
        if len(contents) > 2 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image exceeds 2MB limit")

        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Generate unique filename
        file_ext = os.path.splitext(image.filename)[1]
        unique_filename = f"{login_details.id}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save the file
        with open(file_path, "wb") as f:
            f.write(await image.read())

        message = "Image and login user details updated successfully."
        login_details.profile_image_url = unique_filename

    else:
        message = "Login user details updated successfully."

    current_password = updated_login_data.get('current_password')
    password = updated_login_data.get('password')

    if current_password is None and password:
        raise HTTPException(status_code=400, detail="Current password is required to set a new password.")

    if password is None and current_password:
        raise HTTPException(status_code=400, detail="password is required to set a new password.")

    if current_password:
        if not pwd_context.verify(current_password, login_details.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect.")

        if password:
            hashed_pw = hash_password(password)
            login_details.password = hashed_pw
    mobile = updated_login_data.get('mobile')
    if mobile:
        login_details.mobile = mobile

    db.commit()
    db.refresh(login_details)
    return APIResponse(
        status_code=200,
        success=True,
        message=message,
        data=UserOut.from_orm_with_image(login_details) if isinstance(login_details,
                                                                      User) else StaffOut.from_orm_with_image(
            login_details),
    ).model_dump()


@router.post("/upi")  # , response_model=APIResponse[StaffOut])
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
        message="UPI details were updated successfully.",
        data=None
    ).model_dump()


@router.get("/configurations")
def get_doctor_billing_details(db: Session = Depends(get_db),
                               doctor_id: UUID = Depends(get_current_doctor_id),
                               current_user=Depends(get_current_user_payload),
                               # request: Request = None
                               ):
    # Get general details
    username = current_user.get("sub")
    login_details = db.query(User).filter_by(username=username).first()
    if login_details is None:
        login_details = db.query(Staff).filter_by(username=username).first()

    if not login_details:
        raise HTTPException(status_code=404, detail="Login username does not found in staff and user table.")
    final_data = dict()
    final_data['general'] = UserOut.from_orm_with_image(login_details) if isinstance(login_details,
                                                                                     User) else StaffOut.from_orm_with_image(
        login_details)

    # Get UPI Details
    upi_details = db.query(DoctorPaymentDetails).filter_by(doctor_id=doctor_id).first()
    final_data['upi'] = DoctorsBillingInput.model_validate(upi_details) if upi_details else None

    # Get Subscription Details
    # subscription_details = db.query(Subscription).filter_by(user_id=doctor_id, is_active=True).order_by(
    #     Subscription.created_at.desc()).first()  # order_by(Subscription.start_date.desc())
    # final_data['subscription'] = subscription_details # [sub for sub in subscription_details] if subscription_details else []
    subscription, plan = db.query(Subscription, Plan).join(Plan, Subscription.plan_id == Plan.id).filter(
        Subscription.user_id == doctor_id).order_by(
        Subscription.created_at.desc()).first()
    final_data['subscription'] = SubscriptionOutWithPlan.from_orm(subscription,
                                                                  plan)  # for subscription, plan in all_subscription_details],
    if plan.name == "Professional":
        final_data['subscription'].appointment_left = -1
    else:
        today = date.today()
        if final_data['subscription'].end_date < today or final_data['subscription'] is None:
            final_data['subscription'].appointment_left = 0
        else:
            used_appointments = db.query(Appointment).filter(
                    Appointment.doctor_id == str(doctor_id),
                    Appointment.scheduled_date.between(
                        final_data['subscription'].start_date,
                        final_data['subscription'].end_date
                    )
                ).count()
            final_data['subscription'].appointment_left = total_appointments_basic_plan - used_appointments

    return APIResponse(
        status_code=200,
        success=True,
        message="Successfully fetched user details.",
        data=final_data
    ).model_dump()

    # if not upi_details:
    #     return APIResponse(
    #         status_code=200,
    #         success=True,
    #         message="No UPI details found.",
    #         data=None
    #     ).model_dump()
    # else:
    #     return APIResponse(
    #         status_code=200,
    #         success=True,
    #         message="UPI details fetched successfully.",
    #         data=DoctorsBillingInput.model_validate(upi_details)
    #     ).model_dump()


@router.get("/profile-images/{filename}")
async def get_profile_image(filename: str, current_user=Depends(get_current_user_payload)):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Image not found")
