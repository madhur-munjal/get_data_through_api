import os
import uuid
from datetime import UTC
from datetime import datetime, timedelta

from fastapi import Request

# from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.tables.users import User
from src.dependencies import get_current_user

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY = os.getenv("SECRET_KEY")  # Load from environment in production!

ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30

# In-memory store for refresh tokens (replace with DB or Redis)
refresh_token_store = {}

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, request: Request):
    to_encode = data.copy()
    expire_minutes = request.app.state.ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode["exp"] = datetime.now(UTC) + timedelta(minutes=expire_minutes)
    s_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return s_token


def create_refresh_token(username: str):
    token_id = str(uuid.uuid4())
    to_encode = {
        "sub": username,
        "jti": token_id,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token_store[token_id] = username  # Store token ID
    return token


# def verify_refresh_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         token_id = payload.get("jti")
#         user_id = payload.get("sub")
#         if refresh_token_store.get(token_id) != user_id:
#             return None
#         return user_id
#     except Exception:
#         return None


def revoke_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_id = payload.get("jti")
        refresh_token_store.pop(token_id, None)
    except Exception as ex:
        print(f"Getting exception while revoking refresh token as: {ex}")


# def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         user = db.query(User).filter(User.username == username).first()
#         if user is None:
#             raise HTTPException(status_code=401, detail="User not found")
#         return user
#     except JWTError as e:
#         raise HTTPException(status_code=401, detail=f"Token verification failed : {str(e)}")
