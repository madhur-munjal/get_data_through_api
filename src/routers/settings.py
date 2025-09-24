from uuid import UUID
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
from pydantic import constr
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
from fastapi.responses import FileResponse

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
        password: Optional[constr(min_length=5)] = Form(None),
        image: Optional[UploadFile] = File(None),

        # updated_login_data: UpdateLoginRecord,
        # # image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
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

        # return {"filename": unique_filename, "url": f"/profile-images/{unique_filename}"}
    else:
        message = "Login user details updated successfully."


    if updated_login_data.get('current_password') is None and updated_login_data.get('password'):
        raise HTTPException(status_code=400, detail="Current password is required to set a new password.")

    if updated_login_data.get('password') is None and updated_login_data.get('current_password'):
        raise HTTPException(status_code=400, detail="password is required to set a new password.")

    if updated_login_data.get('current_password'):
        if not pwd_context.verify(updated_login_data.get('current_password'), login_details.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect.")
        if updated_login_data.get('password'):
            hashed_pw = hash_password(updated_login_data.get('password'))
            login_details.password = hashed_pw

    if updated_login_data.get('mobile'):
        login_details.mobile = updated_login_data.get('mobile')

    db.commit()
    db.refresh(login_details)
    return APIResponse(
        status_code=200,
        success=True,
        message=message,
        data=UserOut.model_validate(login_details) if isinstance(login_details, User) else StaffOut.model_validate(
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
                               ):
    # Get general details
    username = current_user.get("sub")
    login_details = db.query(Staff).filter_by(username=username).first()
    if login_details is None:
        login_details = db.query(User).filter_by(username=username).first()

    if not login_details:
        raise HTTPException(status_code=404, detail="Login username does not found in staff and user table.")
    print("************")
    print(UserOut.model_validate(login_details))
    final_data = dict()
    final_data['general'] = UserOut.model_validate(login_details)


    # Get UPI Details
    upi_details = db.query(DoctorPaymentDetails).filter_by(doctor_id=doctor_id).first()
    print(DoctorsBillingInput.model_validate(upi_details))
    final_data['upi'] = DoctorsBillingInput.model_validate(upi_details) if upi_details else None
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
async def get_profile_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Image not found")
