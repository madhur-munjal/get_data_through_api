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
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login a user and return an access token."""
    username = user.username
    password = user.password
    db_user = db.query(User).filter_by(username=username).first()
    if not db_user or not auth.verify_password(password, db_user.password):
        return Token(status_code=200, status="success", message="Invalid credentials", data=None)
    token = auth.create_access_token(data={"sub": username})
    user_details = {column.name: getattr(db_user, column.name) for column in User.__table__.columns}
    return Token(
        status_code=200,
        status="Success",
        message="User logged in successfully",
        data={"access_token": token, "token_type": "bearer", "user_details": user_details}
        # Get Sign_up class and pass all details
    )

# @router.post("/login", response_model=Token)
# def login(user: UserLogin, db: Session = Depends(get_db), dependencies=Depends(authenticate_application)):
#     db_user = db.query(User).filter_by(username=user.username).first()
#     if not db_user or not auth.verify_password(user.password, db_user.password):
#         return Token(status_code=200, status="success", message="Invalid credentials", data=None)
#         # raise HTTPException(status_code=401, detail="Invalid credentials")
#     token = auth.create_access_token(data={"sub": db_user.username})
#     user_details = {column.name: getattr(db_user, column.name) for column in User.__table__.columns}
#     return Token(
#         status_code=200,
#         status="Success",
#         message="User logged in successfully",
#         data={"access_token": token, "token_type": "bearer", "user_details": user_details}
#         # Get Sign_up class and pass all details
#     )


@router.post("/forgot-password", response_model=Token)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=request.email).first()
    if not user:
        return Token(status_code=200, status="success", message="Email not found", data=None)
    if user.username != request.username:
        return Token(status_code=200, status="success", message="Username does not match with email", data=None)
    token = str(uuid.uuid4())

    otp = generate_otp()
    otp_store[request.email] = otp  # TODO: Save OTP (with expiry in production)

    try:
        # print(f"Sending OTP {otp} to {request.email}")
        send_otp_email(request.email, otp)
        print(f"otp_store: {otp_store}")  # For debugging purposes
        return {"message": "OTP sent successfully", "status_code": 200, "status": "success", "data": None}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

    # reset_token = PasswordResetToken(user_id=user.id, token=token)
    # db.add(reset_token)
    # db.commit()
    # background_tasks.add_task(send_email_reset_link, request.email, token)
    # return {"message": "Password reset link sent to your email", "status_code": 200, "status": "success", "data": None}


@router.post("/reset-password", response_model=Token, status_code=status.HTTP_200_OK)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    # print(f"otp_store in reset: {otp_store}")  # For debugging purposes
    # if request.email not in otp_store:
    #     raise HTTPException(status_code=404, detail="User not found in otp store")

    # Update password in your DB
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = pwd_context.hash(request.new_password)
    db.commit()
    return {"message": "Password reset successful", "status_code": 200, "status": "success", "data": None}


@router.post("/verify-otp", response_model=Token, status_code=status.HTTP_200_OK)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    print(f"otp_store in verify: {otp_store}")  # For debugging purposes
    stored_otp = otp_store.get(request.email)
    if not stored_otp:
        raise HTTPException(status_code=404, detail="OTP not found or expired")
    if request.otp != stored_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # You can add logic to mark OTP as verified (e.g., setting a flag in DB or cache)
    # For demo purposes, we delete it from the store
    del otp_store[request.email]

    return {"message": "OTP verified successfully", "status_code": 200, "status": "success", "data": None}
