"""
Recheck the dependency, now using verify_token which is in auth_utils.py
"""

import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from uuid import UUID
from src.models.response import APIResponse, TokenRevoked
# import redis
from redis import Redis

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()

from src.redis_client import get_redis_client

# def is_token_blacklisted(redis: Redis, token: str) -> bool:
#     return redis.get(f"blacklist:{token}") == "revoked"

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis = Depends(get_redis_client)
):
    token = credentials.credentials
    if redis.get(f"blacklist:{token}"): # is_token_blacklisted(redis, token):
        raise TokenRevoked()

        # return APIResponse(
        #     status_code=200, success=False, message="Token has been revoked", data=None
        # ).model_dump()
        # raise TokenRevoked(token)
        raise HTTPException(status_code=401, detail="Token has been revoked")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        user_id = payload.get("sub")
        if user_id is None:
            # return APIResponse(
            #     status_code=200, success=False, message="User ID missing in token", data=None
            # ).model_dump()
            raise HTTPException(status_code=401, detail="User ID missing in token")

        return user_id
    except JWTError as ex:
        return APIResponse(
            status_code=200, success=False, message="Invalid token", data=None, errors=[str(ex)]
        ).model_dump()
        # raise HTTPException(status_code=401, detail="Invalid token")

# def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     if redis.get(f"blacklist:{token}") == b"revoked":
#         return APIResponse(
#             status_code=200, success=False, message="Token has been revoked", data=None
#         ).model_dump()
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
#         user_id = payload.get("sub")
#         # Fetch user from DB if needed
#         return user_id
#     except JWTError as ex:
#         return APIResponse(
#             status_code=200, success=False, message="Invalid token", data=None, errors=str(ex)
#         ).model_dump()
#         # raise HTTPException(status_code=401, detail="Invalid token")

    # try:
    #     payload = jwt.decode(
    #         rf"{token}",
    #         SECRET_KEY,
    #         algorithms=[ALGORITHM],
    #         options={"verify_signature": False},
    #     )
    #     print(f"payload: {payload}")  # Log this!
    #     return payload["sub"]
    # except JWTError as e:
    #     print("JWT decode error:", str(e))  # Log this!
    #     raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_doctor_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    token = credentials.credentials
    print(f"token in get_current_doctor_id: {token}")
    if not token:
        return APIResponse(
            status_code=200, success=False, message="Used id doesn't found", data=None
        ).model_dump()

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
        return APIResponse(
            status_code=200, success=False, message="Token decode failed", errors=e
        ).model_dump()


# redis_client = Redis(host="localhost", port=6379, decode_responses=True)

from redis import Redis

def blacklist_token(redis: Redis, token: str, expiry_seconds: int):
    redis.setex(f"blacklist:{token}", expiry_seconds, "revoked")


