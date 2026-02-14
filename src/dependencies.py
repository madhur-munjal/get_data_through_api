"""
Recheck the dependency, now using verify_token which is in auth_utils.py
"""

import os
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from redis import Redis

from src.models.response import APIResponse, TokenRevoked
from datetime import date
from src.schemas.tables.subscription import Subscription
from sqlalchemy.orm import Session
from src.database import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()

from src.redis_client import get_redis_client


def get_current_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis=Depends(get_redis_client),
):
    token = credentials.credentials
    if redis.get(f"blacklist:{token}"):  # is_token_blacklisted(redis, token):
        raise TokenRevoked()
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            # options={"verify_signature": False},
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise TokenRevoked(message="User ID missing in token", code=200)

        return payload  # user_id
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as ex:
        return APIResponse(
            status_code=200,
            success=False,
            message="Invalid token",
            data=None,
            errors=[str(ex)],
        ).model_dump()


def get_current_doctor_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user=Depends(get_current_user_payload),
) -> UUID:
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing"
        )
    try:
        payload = jwt.decode(
            rf"{token}",
            SECRET_KEY,
            algorithms=[ALGORITHM],
            # options={"verify_signature": False},
        )
        return payload["doc_id"]
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session Expired"
        )
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


def blacklist_token(redis: Redis, token: str, expiry_seconds: int):
    redis.setex(f"blacklist:{token}", expiry_seconds, "revoked")


def require_owner(user_payload=Depends(get_current_user_payload)):
    if user_payload.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Permission denied.")
    return user_payload


def require_admin_owner(user_payload=Depends(get_current_user_payload)):
    if user_payload.get("role").lower() not in ["owner", "admin"]:  # != "owner":
        raise HTTPException(status_code=403, detail="Permission denied.")
    return user_payload


def get_subscription_active_status_by_doctor(db: Session = Depends(get_db), doctor_id=Depends(get_current_doctor_id)):

    today = date.today()
    active_subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == doctor_id,
            Subscription.start_date <= today,
            Subscription.end_date >= today,
            Subscription.is_active == True,
        )
        .order_by(Subscription.start_date.desc())
        .first()
    )
    if not active_subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your subscription has expired. Please renew your subscription to access this feature."
        )
    return active_subscription is not None
