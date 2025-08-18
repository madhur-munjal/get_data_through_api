"""
Recheck the dependency, now using verify_token which is in auth_utils.py
"""

import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from uuid import UUID
from src.models.response import APIResponse

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            rf"{token}",
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_signature": False},
        )
        print(f"payload: {payload}")  # Log this!
        return payload["sub"]
    except JWTError as e:
        print("JWT decode error:", str(e))  # Log this!
        raise HTTPException(status_code=401, detail="Invalid or expired token")


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
