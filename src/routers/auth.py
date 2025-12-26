import uuid
from datetime import date, timedelta
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from passlib.context import CryptContext
from redis import Redis
from sqlalchemy.orm import Session

from src.auth_utils import SECRET_KEY, ALGORITHM
from src.auth_utils import (
    create_access_token,
    verify_password,
    create_refresh_token,
    hash_password,
)
from src.database import get_db
from src.models.billing import DoctorsBillingSave
from src.models.response import APIResponse
from src.models.subscription import SubscriptionCreate
from src.models.users import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserCreate,
    UserLogin,
    UserOut,
    VerifyOTPRequest
)
from src.redis_client import get_redis_client
from src.routers.subscription import create_subscription
from src.schemas.tables.doctor_payment_details import DoctorPaymentDetails
from src.schemas.tables.plans import Plan
from src.schemas.tables.staff import Staff
from src.schemas.tables.users import User
from src.utility import generate_otp, send_otp_email

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

    start_date = date.today()
    end_date = start_date + timedelta(days=180)
    plan = db.query(Plan).filter(Plan.name == "Basic").first()

    # if not plan:
    #     raise HTTPException(400, "Plan not found")

    subscription_data = SubscriptionCreate(
        user_id=db_user.id,
        plan_id=plan.id,  # "7d6c3a9a-3907-448e-aa38-effc448007ab",  # id of free plan
        start_date=start_date,  # .isoformat() + "T07:11:38.682Z",
        end_date=end_date,  # "2025-12-28T07:11:38.682Z",
        auto_renew=False
    )
    create_subscription(subscription=subscription_data, db=db)
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
    billing_details_db = db.query(DoctorPaymentDetails).filter_by(doctor_id=doc_id).first()
    if billing_details_db:
        billing_details = DoctorsBillingSave(doctor_id=doc_id, upi_id=billing_details_db.upi_id,
                                             name=billing_details_db.name,
                                             currency=billing_details_db.currency).model_dump()
    else:
        billing_details = None
    # TODO: add id in below
    access_token = create_access_token(
        {"sub": username, "doc_id": doc_id, "role": db_user.role, "firstName": db_user.firstName,
         "lastName": db_user.lastName, "billingDetails": billing_details}, request=request
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
        payload = jwt.decode(
            refresh_token,
            "refresh_secret",
            algorithms=["HS256"],
            # options={"verify_signature": False},
        )
    except jwt.ExpiredSignatureError:
        return APIResponse(
            status_code=200, success=False, message="Refresh token expired"
        ).model_dump()
    new_access_token = create_access_token(
        {"sub": payload["sub"]},
        secret="access_secret",
        expires_delta=timedelta(minutes=15),
    )
    return APIResponse(
        status_code=200,
        success=True,
        message="Token refresh successfully",
        data={"access_token": new_access_token},
    ).model_dump()


@router.post("/logout")
def logout(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        redis=Depends(get_redis_client),
):
    token = credentials.credentials
    payload = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False}
    )
    exp = payload.get("exp")

    ttl = exp - int(datetime.now(timezone.utc).timestamp())

    redis.setex(f"blacklist:{token}", ttl, "revoked")

    # blacklist_token(redis, token, expiry_seconds=3600)
    return APIResponse(
        status_code=200, success=True, message="Logged out.", data=None
    ).model_dump()


@router.post("/forgot-password", response_model=APIResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db),
                    redis_client=Depends(get_redis_client)):
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
    expiry_minutes: int = 10  # OTP expiry time in minutes
    otp = generate_otp()
    # otp_store[request.email] = otp  # TODO: Save OTP (with expiry in production)
    session_data = {
        "email": request.email,
        "otp": otp,
        "verified": "false"
    }
    redis_client.hmset(token, session_data)
    redis_client.expire(token, timedelta(minutes=expiry_minutes))
    try:
        send_otp_email(request.email, otp)
        return APIResponse(
            status_code=200, success=True, message="OTP sent successfully", data={'token': token}
        ).model_dump()

    except Exception as e:
        return APIResponse(
            status_code=200,
            success=False,
            message="Failed to sent OTP",
            error=f"Failed to send OTP: {str(e)}",
        ).model_dump()


@router.post("/verify-otp", response_model=APIResponse, status_code=status.HTTP_200_OK)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db),
               redis_client=Depends(get_redis_client)):
    # stored_otp = otp_store.get(request.email)
    # session = get_otp_session(token)
    session = redis_client.hgetall(request.token)
    if not session or session["otp"] != request.otp:  # stored_otp:
        return APIResponse(
            status_code=200, success=False, message="Invalid/Expired OTP."
        ).model_dump()
    # mark_otp_verified(token)
    redis_client.hset(request.token, "verified", "true")
    # if request.otp != stored_otp:
    #     return APIResponse(
    #         status_code=200, success=False, message="Incorrect OTP."
    #     ).model_dump()

    # You can add logic to mark OTP as verified (e.g., setting a flag in DB or cache)
    # For demo purposes, we delete it from the store
    # del otp_store[request.email]

    return APIResponse(
        status_code=200, success=True, message="OTP verified successfully.", data=None
    ).model_dump()


@router.post(
    "/reset-password", response_model=APIResponse, status_code=status.HTTP_200_OK
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db),
                   redis_client=Depends(get_redis_client)):
    session = redis_client.hgetall(request.token)
    if not session or session.get('verified') == 'false':
        return APIResponse(
            status_code=200, success=False, message="Session is either expired or has not been verified"
        ).model_dump()
    # mark_otp_verified(token)

    user = db.query(User).filter(User.email == session.get('email')).first()
    if not user:
        return APIResponse(
            status_code=200, success=False, message="User not found.", data=None
        ).model_dump()
    user.password = pwd_context.hash(request.password)
    db.commit()
    return APIResponse(
        status_code=200, success=True, message="Password reset successfully.", data=None
    ).model_dump()


@router.put("/config/token-expiry")
def update_token_expiry(
        minutes: int, request: Request, redis: Redis = Depends(get_redis_client)
):
    if minutes <= 0 or minutes > 1440:
        return APIResponse(
            status_code=200,
            success=False,
            message="Invalid expiry time. Must be between 1 and 1440 minutes.",
            data=None,
        )
    request.app.state.ACCESS_TOKEN_EXPIRE_MINUTES = minutes
    redis.set("config:access_token_expiry", minutes)
    return APIResponse(
        status_code=200,
        success=True,
        message="Token expiry has been updated.",
        data={"new_expiry": minutes},
    )
