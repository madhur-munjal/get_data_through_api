from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.dependencies import get_current_user
from src.database import get_db
from src.models.response import APIResponse
from src.models.users import DeleteUserRequest, UserOut
from src.schemas.tables.users import User

router = APIRouter(tags=["users"])


@router.get("/users_list", response_model=APIResponse)
def get_users(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch all users."""
    users = db.query(User).all()
    user_dtos = [UserOut.model_validate(user) for user in users]
    return APIResponse(status_code=200,
                       status="success",
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
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return APIResponse(status_code=200,
                       status="success",
                       message="successfully deleted user",
                       data=f"User {request.user_id} deleted successfully"
                       ).model_dump()
