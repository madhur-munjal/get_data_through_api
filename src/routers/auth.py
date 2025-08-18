import uuid
from jose import jwt, JWTError
from fastapi import APIRouter, HTTPException, Depends, status, Response, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import timedelta
from src.auth_utils import (
    create_access_token,
    verify_password,
    create_refresh_token,
    revoke_refresh_token,
    hash_password,
)
from src.database import get_db
from src.models.response import APIResponse
from src.models.users import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyOTPRequest,
    UserCreate,
    UserLogin,
    UserOut,
)
from src.schemas.tables.users import User
from src.schemas.tables.staff import Staff
from src.utility import generate_otp, send_otp_email, otp_store
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# import redis
# from src.dependencies import blacklist_token
from src.redis_client import get_redis_client
from datetime import datetime, timezone
from src.auth_utils import SECRET_KEY, ALGORITHM

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(
    prefix="/auth", tags=["auth"], responses={404: {"error": "Not found"}}
)


@router.post("/register", response_model=APIResponse[UserOut])
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = db.query(User).filter_by(username=user.username).first()
    if db_user:
        return APIResponse(
            status_code=200, success=False, message="Username already exists", data=None
        ).model_dump()
    if db.query(User).filter_by(email=user.email).first():
        return APIResponse(
            status_code=200, success=False, message="Email already exists", data=None
        ).model_dump()
    hashed_pw = hash_password(user.password)
    db_user = User(
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        country=user.country,
        mobile=user.mobile,
        username=user.username,
        password=hashed_pw,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return APIResponse(
        status_code=200,
        success=True,
        message="Your account has been created successfully.",
        data=UserOut.model_validate(db_user),
    ).model_dump()


@router.post("/login", response_model=APIResponse)
def login(
    request: Request, user: UserLogin, response: Response, db: Session = Depends(get_db)
):
    """Login a user and return an access token."""
    username = user.username
    password = user.password
    doc_db_user = db.query(User).filter_by(username=username).first()
    if not doc_db_user:
        # or not verify_password(password, db_user.password):
        staff_db_user = db.query(Staff).filter_by(username=username).first()
        if not staff_db_user:
            return APIResponse(
                status_code=200, success=False, message="User not found.", data=None
            )
        user_password = staff_db_user.password
        doc_id = staff_db_user.doc_id
        user_details = {
            column.name: getattr(staff_db_user, column.name)
            for column in Staff.__table__.columns
            if column.name != "password"
        }
    else:
        user_password = doc_db_user.password
        doc_id = doc_db_user.id
        user_details = {
            column.name: getattr(doc_db_user, column.name)
            for column in User.__table__.columns
            if column.name != "password"
        }

    if not verify_password(password, user_password):
        return APIResponse(
            status_code=200, success=False, message="Incorrect password.", data=None
        )
    db_user = doc_db_user or staff_db_user
    # TODO: add id in below
    access_token = create_access_token(
        {"sub": username, "doc_id": doc_id}, request=request
    )
    refresh_token = create_refresh_token(username)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=30 * 24 * 60 * 60,
    )
    # print(f"db_user: {db_user}")
    return APIResponse(
        status_code=200,
        success=True,
        message="User logged in successfully.",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user_details": user_details,
        },
    ).model_dump()  # "refresh_token": refresh_token,


@router.post("/refresh")
def refresh(request: Request, response: Response, response_model=APIResponse):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        return APIResponse(
            status_code=200, success=False, message="Missing refresh token"
        ).model_dump()
    try:
        payload = jwt.decode(refresh_token, "refresh_secret", algorithms=["HS256"], options={"verify_signature": False})
    except jwt.ExpiredSignatureError:
        return APIResponse(
            status_code=200, success=False, message="Refresh token expired"
        ).model_dump()
    new_access_token = create_access_token(
        {"sub": payload["sub"]},
        secret="access_secret",
        expires_delta=timedelta(minutes=15),
    )
    return {"access_token": new_access_token}

    # token = request.cookies.get("refresh_token")
    # user_id = verify_refresh_token(token)
    # if not user_id:
    #     raise HTTPException(status_code=401, detail="Invalid refresh token")
    #
    # revoke_refresh_token(token)
    # new_refresh = create_refresh_token(user_id)
    # new_access = create_access_token({"sub": user_id}, request=request)
    #
    # response.set_cookie(
    #     key="refresh_token",
    #     value=new_refresh,
    #     httponly=True,
    #     secure=True,
    #     samesite="strict",
    #     max_age=7 * 24 * 60 * 60
    # )
    # return {"access_token": new_access}



@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis = Depends(get_redis_client)
):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
    exp = payload.get("exp")

    ttl = exp - int(datetime.now(timezone.utc).timestamp())

    redis.setex(f"blacklist:{token}", ttl, "revoked")

    # blacklist_token(redis, token, expiry_seconds=3600)
    return APIResponse(
        status_code=200, success=True, message="Logged out.", data=None
    ).model_dump()



# @router.post("/logout")
# def logout(request: Request, response: Response):
#     response.delete_cookie("access_token")
#     response.delete_cookie("access_token", path="/", domain="yourdomain.com")
#
#     # token = request.cookies.get("refresh_token")
#     # revoke_refresh_token(token)
#     # response.delete_cookie("refresh_token")
#     return APIResponse(
#         status_code=200, success=True, message="Logged out.", data=None
#     ).model_dump()


@router.post("/forgot-password", response_model=APIResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=request.email).first()
    if not user:
        return APIResponse(
            status_code=200, success=False, message="Email not found", data=None
        ).model_dump()
    if user.username != request.username:
        return APIResponse(
            status_code=200, success=False, message="Username not found.", data=None
        ).model_dump()
    token = str(uuid.uuid4())

    otp = generate_otp()
    otp_store[request.email] = otp  # TODO: Save OTP (with expiry in production)

    try:
        # print(f"Sending OTP {otp} to {request.email}")
        send_otp_email(request.email, otp)
        print(f"otp_store: {otp_store}")  # For debugging purposes
        return APIResponse(
            status_code=200, success=True, message="OTP sent successfully", data=None
        ).model_dump()

    except Exception as e:
        return APIResponse(
            status_code=200,
            success=False,
            message="Failed to sent OTP",
            error=f"Failed to send OTP: {str(e)}",
        ).model_dump()
        # raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")
    # TODO: # Change it to APIResponse

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
        return APIResponse(
            status_code=200, success=False, message="OTP not found or expired."
        ).model_dump()
    if request.otp != stored_otp:
        return APIResponse(
            status_code=200, success=False, message="Incorrect OTP."
        ).model_dump()

    # You can add logic to mark OTP as verified (e.g., setting a flag in DB or cache)
    # For demo purposes, we delete it from the store
    del otp_store[request.email]

    return APIResponse(
        status_code=200, success=True, message="OTP verified successfully.", data=None
    ).model_dump()


@router.post(
    "/reset-password", response_model=APIResponse, status_code=status.HTTP_200_OK
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    # print(f"otp_store in reset: {otp_store}")  # For debugging purposes
    # if request.email not in otp_store:
    #     raise HTTPException(status_code=404, detail="User not found in otp store")

    # Update password in your DB
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        return APIResponse(
            status_code=200, success=False, message="User not found.", data=None
        ).model_dump()
        # raise HTTPException(status_code=404, detail="User not found")
    user.password = pwd_context.hash(request.new_password)
    db.commit()
    return APIResponse(
        status_code=200, success=True, message="Password reset successfully.", data=None
    ).model_dump()


@router.put("/config/token-expiry")
def update_token_expiry(minutes: int, request: Request):
    if minutes <= 0 or minutes > 1440:
        return APIResponse(
            status_code=200,
            success=False,
            message="Invalid expiry time. Must be between 1 and 1440 minutes.",
            data=None,
        )
    request.app.state.ACCESS_TOKEN_EXPIRE_MINUTES = minutes
    return APIResponse(
        status_code=200,
        success=True,
        message="Token expiry has been updated.",
        data={"new_expiry": minutes},
    )
