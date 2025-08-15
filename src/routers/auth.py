import uuid

from fastapi import APIRouter, HTTPException, Depends, status, Response, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.auth_utils import create_access_token, verify_password, create_refresh_token, verify_refresh_token, \
    revoke_refresh_token, hash_password
from src.database import get_db
from src.models.response import APIResponse
from src.models.users import ForgotPasswordRequest, ResetPasswordRequest, VerifyOTPRequest, UserCreate, \
    UserLogin, UserOut
from src.schemas.tables.users import User
from src.utility import generate_otp, send_otp_email, otp_store

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(tags=["auth"])


@router.post("/register", response_model=APIResponse[UserOut])
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = db.query(User).filter_by(username=user.username).first()
    if db_user:
        return APIResponse(status_code=200, success=False, message="Username already exists", data=None).model_dump()
        # raise Now username is unique. Need to rethink if duplicate username should be allowed or not
    if db.query(User).filter_by(email=user.email).first():
        return APIResponse(status_code=200, success=False, message="Email already exists", data=None).model_dump()
    hashed_pw = hash_password(user.password)
    db_user = User(firstName=user.firstName, lastName=user.lastName, email=user.email, country=user.country,
                   mobile=user.mobile, username=user.username, password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return APIResponse(status_code=200,
                       success=True,
                       message="User has been registered successfully",
                       data=UserOut.model_validate(db_user)).model_dump()


@router.post("/login", response_model=APIResponse)
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
    """Login a user and return an access token."""
    username = user.username
    password = user.password
    db_user = db.query(User).filter_by(username=username).first()
    if not db_user or not verify_password(password, db_user.password):
        return APIResponse(status_code=200, success=False, message="Invalid credentials", data=None)
    access_token = create_access_token({"sub": username}, request=request)
    # refresh_token = create_refresh_token(username)
    # response.set_cookie(
    #     key="refresh_token",
        # value=refresh_token,
    #     httponly=True,
    #     secure=True,
    #     samesite="strict",
    #     max_age=7 * 24 * 60 * 60
    # )
    user_details = {column.name: getattr(db_user, column.name) for column in User.__table__.columns if
                    column.name != "password"}
    return APIResponse(status_code=200,
                       success=True,
                       message="User logged in successfully",
                       data={"access_token": access_token, "token_type": "bearer",
                             "user_details": user_details}
                       ).model_dump() # "refresh_token": refresh_token,


@router.post("/refresh")
def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    user_id = verify_refresh_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    revoke_refresh_token(token)
    new_refresh = create_refresh_token(user_id)
    new_access = create_access_token({"sub": user_id}, request=request)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60
    )
    return {"access_token": new_access}


@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    revoke_refresh_token(token)
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}


@router.post("/forgot-password", response_model=APIResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=request.email).first()
    if not user:
        return APIResponse(status_code=200, success=False, message="Email not found", data=None).model_dump()
    if user.username != request.username:
        return APIResponse(status_code=200, success=False, message="Username does not match with email",
                           data=None).model_dump()
    token = str(uuid.uuid4())

    otp = generate_otp()
    otp_store[request.email] = otp  # TODO: Save OTP (with expiry in production)

    try:
        # print(f"Sending OTP {otp} to {request.email}")
        send_otp_email(request.email, otp)
        print(f"otp_store: {otp_store}")  # For debugging purposes
        return APIResponse(status_code=200, success=True, message="OTP sent successfully", data=None).model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

    # reset_token = PasswordResetToken(user_id=user.id, token=token)
    # db.add(reset_token)
    # db.commit()
    # background_tasks.add_task(send_email_reset_link, request.email, token)
    # return {"message": "Password reset link sent to your email", "status_code": 200, "status": "success", "data": None}



@router.post("/verify-otp", response_model=APIResponse, status_code=status.HTTP_200_OK)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    print(f"otp_store in verify: {otp_store}")  # For debugging purposes
    stored_otp = otp_store.get(request.email)
    if not stored_otp:
        return APIResponse(status_code=200, success=False, message="OTP not found or expired").model_dump()
    if request.otp != stored_otp:
        return APIResponse(status_code=200, success=False, message="Incorrect OTP").model_dump()

    # You can add logic to mark OTP as verified (e.g., setting a flag in DB or cache)
    # For demo purposes, we delete it from the store
    del otp_store[request.email]

    return APIResponse(status_code=200, success=True, message="OTP verified successfully", data=None).model_dump()

@router.post("/reset-password", response_model=APIResponse, status_code=status.HTTP_200_OK)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    # print(f"otp_store in reset: {otp_store}")  # For debugging purposes
    # if request.email not in otp_store:
    #     raise HTTPException(status_code=404, detail="User not found in otp store")

    # Update password in your DB
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return APIResponse(status_code=200, success=False, message="User not found", data=None).model_dump()
        # raise HTTPException(status_code=404, detail="User not found")
    user.password = pwd_context.hash(request.new_password)
    db.commit()
    return APIResponse(status_code=200, success=True, message="Password reset successful", data=None).model_dump()


@router.put("/config/token-expiry")
def update_token_expiry(minutes: int, request: Request):
    if minutes <= 0 or minutes > 1440:
        return APIResponse(status_code=200, success=False, message="Invalid expiry time, it should be greater than 0 and less than 1440", data=None)
    request.app.state.ACCESS_TOKEN_EXPIRE_MINUTES = minutes
    return APIResponse(status_code=200, success=True, message="Token expiry updated", data={"new_expiry": minutes})
