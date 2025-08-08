from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.dependencies import get_current_user
from src.models.response import APIResponse
from src.models.users import DeleteUserRequest, UserOut
from src.schemas.tables.users import User

# from app.auth import get_current_user  # your JWT auth dependency

router = APIRouter(tags=["users"])



@router.get("/users_list", response_model=APIResponse)
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    # if not users:
    #     return APIResponse(
    #         status_code=200,
    #         status="success",
    #         message="No user found",
    #         data=None
    #     )
    user_dtos = [UserOut.model_validate(user) for user in users]
    return APIResponse(status_code=200,
                       status="success",
                       message="successfully fetched users",
                       data=user_dtos
                       )


# @router.post("/delete_user")
# def delete_user(request: DeleteUserRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == request.user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return {"detail": f"User {request.user_id} deleted successfully"}


@router.post("/delete-user")
def delete_user(
        request: DeleteUserRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Optional: check if current_user is admin
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return APIResponse(status_code=200,
                       status="success",
                       message="successfully deleted user",
                       data=f"User {request.user_id} deleted successfully"
                       )
