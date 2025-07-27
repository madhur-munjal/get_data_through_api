from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
import sys
import os

sys.path.append(os.path.join(os.getcwd(), ".."))
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.database import get_db, engine

router = APIRouter(prefix="/medical", tags=["medical", "doctor"], responses={404: {"error": "Not found"}}, )


class MedicalBase(BaseModel):
    """request payload to add/update data into database"""
    field_1: str = Field(None, max_length=30)  # , pattern="^$|^\S+$"


@router.get("/", status_code=status.HTTP_200_OK)  # , dependencies=[Depends(authenticate_application)]
async def read_data(db: Session = Depends(get_db)):
    # return "******"
    device = db.query(MedicalBase)
    return device


@router.put("/items/{item_id}", status_code=status.HTTP_200_OK)  # , dependencies=[Depends(authenticate_application)]
async def read_data(item_id: int, item: MedicalBase):
    return {"item_id": item_id, "item": item.field_1}


@router.get("/get_db")
def read_root():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DATABASE();"))
        db_name = result.scalar()  # Or result.fetchone()[0]
        return {"database": db_name}

        # return {"database": result.fetchone()}
