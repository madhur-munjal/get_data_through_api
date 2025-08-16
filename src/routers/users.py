from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from mysql.connector.errors import IntegrityError

from src.dependencies import get_current_user
from src.database import get_db
from src.models.response import APIResponse
from src.models.users import DeleteUserRequest, UserOut, UserCreate
from src.schemas.tables.users import User

router = APIRouter(tags=["users"])


@router.get("/users_list", response_model=APIResponse)
def get_users(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch all users."""
    users = db.query(User).all()
    user_dtos = [UserOut.model_validate(user) for user in users]
    return APIResponse(status_code=200,
                       success=True,
                       message="successfully fetched users",
                       data=user_dtos
                       ).model_dump()


@router.post("/delete-user")
def delete_user(
        request: DeleteUserRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Delete a user by ID.
    This endpoint allows an authenticated user to delete another user by their ID.
    """
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        return APIResponse(status_code=200,
                           success=False,
                           message="User not found",
                           data=None
                           ).model_dump()
        # raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return APIResponse(status_code=200,
                       success=True,
                       message="successfully deleted user",
                       data=f"User {request.user_id} deleted successfully"
                       ).model_dump()


@router.put("/update/{id}", response_model=APIResponse)
def update_item(id: str, payload: UserCreate, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == id).first()
    if not user_db:
        return APIResponse(status_code=200,
                           success=False,
                           message=f"User not found with the id {id}."
                           ).model_dump()
        # raise HTTPException(status_code=404, detail="Item not found")

    try:
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(user_db, field, value)

        db.commit()
        db.refresh(user_db)
        return APIResponse(status_code=200,
                           success=True,
                           message="User details updated successfully.",
                           data=UserOut.model_validate(user_db)).model_dump()
    # except IntegrityError as e:
    #     msg = str(e.orig) if hasattr(e, "orig") else str(e)
    #     if "Duplicate entry" in msg:
    #         start = msg.find("Duplicate entry")
    #         end = msg.find(" for key", start)
    #         clean_msg = msg[start:end + len(" for key 'users.email'")]
    #         return APIResponse(status_code=200,
    #                            success=False,
    #                            message=f"Failed to update user details",
    #                            data=None,
    #                            errors=clean_msg
    #                            )
    #     return APIResponse(status_code=200,
    #                 success=False,
    #                 message=f"Failed to update user details",
    #                 data=None,
    #                 errors=[msg]
    #                 )
    except Exception as e:
        error_msg = str(e.orig) if hasattr(e, "orig") else str(e)

        return APIResponse(status_code=200,
                           success=False,
                           message=f"Failed to update user details",
                           data=None,
                           errors=[error_msg]
                           )

        # UserOut.model_validate(user_db)).model_dump()

