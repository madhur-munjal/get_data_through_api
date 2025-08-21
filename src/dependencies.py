"""
Recheck the dependency, now using verify_token which is in auth_utils.py
"""

import os
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from redis import Redis

from src.exceptions import APIException
from src.models.response import APIResponse, TokenRevoked

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()

from src.redis_client import get_redis_client


def get_current_user(
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
            options={"verify_signature": False},
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise TokenRevoked(message="User ID missing in token", code=200)

        return user_id
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
) -> UUID:
    token = credentials.credentials
    print(f"token in get_current_doctor_id: {token}")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing"
        )
        # .model_dump())
        # return APIResponse(
        #     status_code=200, success=False, message="Used id doesn't found", data=None
        # ).model_dump()

    try:
        payload = jwt.decode(
            rf"{token}",
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_signature": False},
        )
        print(f"payload: {payload}")  # payload in get_current_doctor_id
        return payload["doc_id"]
    except JWTError as e:
        print("JWT decode error:", str(e))  # Log this!
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


def blacklist_token(redis: Redis, token: str, expiry_seconds: int):
    redis.setex(f"blacklist:{token}", expiry_seconds, "revoked")
