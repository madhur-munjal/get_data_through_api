from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from src.auth_utils import hash_password
from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import get_current_user_payload
from src.models.response import APIResponse

# from src.models.users import UserIDRequest, UserOut, UserCreate
from src.models.staff import StaffCreate, StaffOut
from src.schemas.tables.staff import Staff

router = APIRouter(
    prefix="/staff", tags=["staff"], responses={404: {"error": "Not found"}}
)


@router.post("/register", response_model=APIResponse[StaffOut])
def register(
    user: StaffCreate,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
    current_user=Depends(get_current_user_payload),
):
    """Register a new user."""
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
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New staff account created under {current_user.get('sub')} supervision.",
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
        message="successfully fetched users",
        data=user_dtos,
    ).model_dump()


@router.get("/doc_wise_staff_list", response_model=APIResponse)
def get_staff_list_by_doc_info(
    email: Optional[str] = Query(None),
    mobile: Optional[str] = Query(None),
    doctor_id: UUID = Depends(get_current_doctor_id),
    db: Session = Depends(get_db),
):
    """Fetch staff details on the basis of doctors mobile or email."""
    if not email and not mobile:
        raise HTTPException(status_code=400, detail="Provide either email or mobile")

    query = db.query(Staff)
    staff_list = None
    if email:
        staff_list = query.filter(Staff.email == email).all()
    if not staff_list or mobile:
        staff_list = query.filter(Staff.mobile == mobile).all()
    if not staff_list:
        raise HTTPException(status_code=404, detail="Staff not found")

    user_dtos = [StaffOut.model_validate(staff) for staff in staff_list]

    return APIResponse(
        status_code=200,
        success=True,
        message="successfully fetched users",
        data=user_dtos,
    ).model_dump()
