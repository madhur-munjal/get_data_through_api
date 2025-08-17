from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth_utils import hash_password
from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import get_current_user
from src.models.response import APIResponse
# from src.models.users import UserIDRequest, UserOut, UserCreate
from src.models.staff import StaffCreate, StaffOut
from src.schemas.tables.staff import Staff

router = APIRouter(prefix="/staff", tags=["staff"],
                   responses={404: {"error": "Not found"}})


@router.post("/register", response_model=APIResponse[StaffOut])
def register(user: StaffCreate, db: Session = Depends(get_db), doctor_id: UUID = Depends(get_current_doctor_id),
             current_user=Depends(get_current_user)):
    """Register a new user."""
    db_user = db.query(Staff).filter_by(doc_id=doctor_id).filter_by(username=user.username).first()
    if db_user:
        return APIResponse(status_code=200, success=False, message="Username already exists", data=None).model_dump()
    if db.query(Staff).filter_by(email=user.email).first():
        return APIResponse(status_code=200, success=False, message="Email already exists", data=None).model_dump()
    #Need to re-validate as in some cases staff will join from one clinic to another
    hashed_pw = hash_password(user.password)
    db_user = Staff(firstName=user.firstName, lastName=user.lastName, email=user.email, country=user.country,
                    mobile=user.mobile, username=user.username, password=hashed_pw, doc_id=doctor_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return APIResponse(status_code=200,
                       success=True,
                       message=f"- New staff account created under {current_user} supervision.",
                       data=StaffOut.model_validate(db_user)).model_dump()


@router.get("/staff_list", response_model=APIResponse)
def get_staff_list(doctor_id: UUID = Depends(get_current_doctor_id), db: Session = Depends(get_db)):
    """Fetch all users."""
    users = db.query(Staff).filter(Staff.doc_id == doctor_id).all()
    user_dtos = [StaffOut.model_validate(user) for user in users]
    return APIResponse(status_code=200,
                       success=True,
                       message="successfully fetched users",
                       data=user_dtos
                       ).model_dump()

# @router.delete("/delete-user", response_model=APIResponse)
# def delete_user(
#         request: UserIDRequest,
#         current_user=Depends(get_current_user),
#         db: Session = Depends(get_db)
# ):
#     """Delete a user by ID.
#     This endpoint allows an authenticated user to delete another user by their ID.
#     """
#     user = db.query(Doctor).filter(Doctor.id == request.user_id).first()
#     if not user:
#         return APIResponse(status_code=200,
#                            success=False,
#                            message="ID mismatch: the provided ID does not match any existing resource.",
#                            data=None
#                            ).model_dump()
#         # raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return APIResponse(status_code=200,
#                        success=True,
#                        message="The user account was successfully deleted",
#                        data=f"User with ID {request.user_id} has been permanently deleted."
#                        ).model_dump()
#
#
# @router.put("/update-user", response_model=APIResponse)
# def update_item(request: UserIDRequest, payload: UserCreate, current_user=Depends(get_current_user),
#                 db: Session = Depends(get_db)):
#     user_db = db.query(Doctor).filter(Doctor.id == request.user_id).first()
#     if not user_db:
#         return APIResponse(status_code=200,
#                            success=False,
#                            message=f"ID mismatch: the provided ID does not match any existing resource."
#                            ).model_dump()
#         # raise HTTPException(status_code=404, detail="Item not found")
#
#     try:
#         for field, value in payload.dict(exclude_unset=True).items():
#             setattr(user_db, field, value)
#
#         db.commit()
#         db.refresh(user_db)
#         return APIResponse(status_code=200,
#                            success=True,
#                            message="User profile updated successfully.",
#                            data=UserOut.model_validate(user_db)).model_dump()
#     # except IntegrityError as e:
#     #     msg = str(e.orig) if hasattr(e, "orig") else str(e)
#     #     if "Duplicate entry" in msg:
#     #         start = msg.find("Duplicate entry")
#     #         end = msg.find(" for key", start)
#     #         clean_msg = msg[start:end + len(" for key 'users.email'")]
#     #         return APIResponse(status_code=200,
#     #                            success=False,
#     #                            message=f"Failed to update user details",
#     #                            data=None,
#     #                            errors=clean_msg
#     #                            )
#     #     return APIResponse(status_code=200,
#     #                 success=False,
#     #                 message=f"Failed to update user details",
#     #                 data=None,
#     #                 errors=[msg]
#     #                 )
#     except Exception as e:
#         error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
#
#         return APIResponse(status_code=200,
#                            success=False,
#                            message=f"Failed to update user details",
#                            data=None,
#                            errors=[error_msg]
#                            )
#
#         # UserOut.model_validate(user_db)).model_dump()
