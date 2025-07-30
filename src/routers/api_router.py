from fastapi import APIRouter

from . import medical, patient

router = APIRouter(prefix="/api", responses={404: {"error": "Not found"}}, )

# List of routers
routers = [medical.router, patient.router]

# Include all routers
for r in routers:
    router.include_router(r)


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.user import UserOut, UserCreate, Token
from src.models.user import User
from src import auth
from src.database import get_db

router = APIRouter(tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pw = auth.hash_password(user.password)
    db_user = User(username=user.username, password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(username=user.username).first()
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}