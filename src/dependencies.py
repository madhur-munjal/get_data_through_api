import os
from collections import defaultdict

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from src.auth import ALGORITHM, SECRET_KEY
from src.database import get_db
from src.models.users import User

failed_attempts = defaultdict(int)
SECRET_TOKEN = "sample"


# def authenticate_application(app_name: str, token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
#     """
#     Middleware to authenticate application requests using a token.
#     """
#     excepted_app_name = os.getenv("app_name")
#     excepted_app_token = os.getenv("app_token")
#     if not excepted_app_name == app_name or not token.credentials == excepted_app_token:
#         raise HTTPException(status_code=401, detail="Unauthorized (1)")
#     return token.credentials


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        current_user = db.query(User).filter_by(username=username).first()
        return current_user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token decode error")
