import os
from collections import defaultdict

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

failed_attempts = defaultdict(int)
SECRET_TOKEN = "sample"


def authenticate_application(app_name: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Middleware to authenticate application requests using a token.
    """
    excepted_app_name = os.getenv("app_name")
    excepted_app_token = os.getenv("app_token")
    if not excepted_app_name == app_name or not token.credentials == excepted_app_token:
        raise HTTPException(status_code=401, detail="Unauthorized (1)")
    return token.credentials
