from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src import auth
from src.database import get_db
from src.models.users import User
from src.schemas.users import UserOut, UserCreate, UserLogin, Token

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = db.query(User).filter_by(username=user.username).first()
    if db_user:
        return Token(status_code=200, status="success", message="Username already exists", data=None)
        # raise Now username is unique. Need to rethink if duplicate username should be allowed or not
    hashed_pw = auth.hash_password(user.password)
    db_user = User(username=user.username, password=hashed_pw, address=user.address, contact_number=user.contact_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(username=user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        return Token(status_code=200, status="success", message="Invalid credentials", data=None)
        # raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": db_user.username})
    user_details = {column.name: getattr(db_user, column.name) for column in User.__table__.columns}
    return Token(
        status_code=200,
        status="Success",
        message="User logged in successfully",
        data={"access_token": token, "token_type": "bearer", "user_details": user_details} # Get Sign_up class and pass all details
    )
