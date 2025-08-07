import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src import auth
from src.database import get_db
from src.dependencies import get_current_user
from src.models.users import User, PasswordResetToken
from src.schemas.users import ForgotPasswordRequest, ResetPasswordRequest, VerifyOTPRequest
from src.schemas.users import UserOut, UserCreate, UserLogin, Token
from src.utility import generate_otp, send_otp_email, otp_store
from pydantic import BaseModel

router = APIRouter(tags=["users"])

class DeleteUserRequest(BaseModel):
    user_id: int

@router.get("/users_list", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.post("/delete_user")
def delete_user(request: DeleteUserRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": f"User {request.user_id} deleted successfully"}

# from app.auth import get_current_user  # your JWT auth dependency
#
# @router.post("/delete-user")
# def delete_user(
#     request: DeleteUserRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     # Optional: check if current_user is admin
#     user = db.query(User).filter(User.id == request.user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return {"detail": f"User {request.user_id} deleted successfully"}
