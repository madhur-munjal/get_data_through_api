import uuid
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.dependencies import authenticate_application
from src import auth
from src.common import send_email_reset_link
from src.database import get_db
from src.models.users import User, PasswordResetToken
from src.schemas.users import ForgotPasswordRequest, ResetPasswordRequest
from src.schemas.users import UserOut, UserCreate, UserLogin, Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = db.query(User).filter_by(username=user.username).first()
    if db_user:
        return Token(status_code=200, status="success", message="Username already exists", data=None)
        # raise Now username is unique. Need to rethink if duplicate username should be allowed or not
    hashed_pw = auth.hash_password(user.password)
    db_user = User(username=user.username, password=hashed_pw, email=user.email, address=user.address,
                   contact_number=user.contact_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db), dependencies=Depends(authenticate_application)):
    db_user = db.query(User).filter_by(username=user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        return Token(status_code=200, status="success", message="Invalid credentials", data=None)
        # raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": db_user.username})
    user_details = {column.name: getattr(db_user, column.name) for column in User.__table__.columns}
    return Token(
        status_code=200,
        status="Success",
        message="User logged in successfully",
        data={"access_token": token, "token_type": "bearer", "user_details": user_details}
        # Get Sign_up class and pass all details
    )


@router.post("/forgot-password", response_model=Token)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db),
                    background_tasks: BackgroundTasks = BackgroundTasks()):
    user = db.query(User).filter_by(email=request.email).first()
    if not user:
        return Token(status_code=200, status="success", message="Email not found", data=None)
    token = str(uuid.uuid4())
    reset_token = PasswordResetToken(user_id=user.id, token=token)
    db.add(reset_token)
    db.commit()
    background_tasks.add_task(send_email_reset_link, request.email, token)
    return {"message": "Password reset link sent to your email", "status_code": 200, "status": "success", "data": None}


@router.post("/reset-password", response_model=Token)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == request.token).first()
    if not reset_token or reset_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = pwd_context.hash(request.new_password)
    db.delete(reset_token)
    db.commit()
    return {"message": "Password reset successful", "status_code": 200, "status": "success", "data": None}
