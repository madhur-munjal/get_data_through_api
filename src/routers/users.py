from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_user_payload, require_owner
from src.models.response import APIResponse
from src.models.users import UserOut, UserUpdate
from src.schemas.tables.users import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"error": "Not found"}},
    dependencies=[Depends(require_owner)],
)


@router.get("/users_list", response_model=APIResponse)
def get_users(
    current_user=Depends(get_current_user_payload),
    db: Session = Depends(get_db),
    # role=Depends(require_owner),
):
    """Fetch all users."""
    users = db.query(User).all()
    user_dtos = [UserOut.model_validate(user) for user in users]
    return APIResponse(
        status_code=200,
        success=True,
        message="successfully fetched users",
        data=user_dtos,
    ).model_dump()


# Getting error(Cannot add or update a child row: a foreign key constraint fails (`my_db`.`staff`, CONSTRAINT `staff_ibfk_1` FOREIGN KEY (`doc_id`) REFERENCES `users` (`id`)))
# @router.delete("/delete-user", response_model=APIResponse)
# def delete_user(
#         request: UserIDRequest,
#         current_user=Depends(get_current_user_payload),
#         db: Session = Depends(get_db), role=Depends(require_owner)
# ):
#     """Delete a user by ID.
#     This endpoint allows an authenticated user to delete another user by their ID.
#     """
#     user = db.query(User).filter(User.id == request.user_id).first()
#     if not user:
#         return APIResponse(
#             status_code=200,
#             success=False,
#             message="ID mismatch: the provided ID does not match any existing resource.",
#             data=None,
#         ).model_dump()
#         # raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message="The user account was successfully deleted",
#         data=f"User with ID {request.user_id} has been permanently deleted.",
#     ).model_dump()


@router.patch("/", response_model=APIResponse)
def update_user(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_payload),
    # role=Depends(require_owner),
):
    doc_id = current_user.get("doc_id")
    user_db = db.query(User).filter(User.id == doc_id).first()
    if not user_db:
        return APIResponse(
            status_code=200,
            success=False,
            message=f"ID mismatch: the provided ID does not match any existing resource.",
        ).model_dump()
    try:
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(user_db, field, value)

        db.commit()
        db.refresh(user_db)
        return APIResponse(
            status_code=200,
            success=True,
            message="User profile updated successfully.",
            data=UserOut.model_validate(user_db),
        ).model_dump()
    except Exception as e:
        error_msg = str(e.orig) if hasattr(e, "orig") else str(e)

        return APIResponse(
            status_code=200,
            success=False,
            message=f"Failed to update user details",
            data=None,
            errors=[error_msg],
        ).model_dump()
