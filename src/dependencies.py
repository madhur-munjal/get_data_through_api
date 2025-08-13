"""
Recheck the dependency, now using verify_token which is in auth_utils.py
"""

import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(rf"{token}", SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        print(payload)
        return payload["sub"]
    except JWTError as e:
        print("JWT decode error:", str(e))  # Log this!
        raise HTTPException(status_code=401, detail="Invalid or expired token")
