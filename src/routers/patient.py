from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from pydantic import BaseModel, Field
from src.models.patient import Patient
from src.schemas.patient import PatentBase, PatentCreate, PatentUpdate, PatentOut
# from . import models, schemas
from src.database import get_db  # assuming you have a get_db dependency

# from . import crud  # assuming you have crud methods for patents


router = APIRouter(
    prefix="/patients",
    tags=["patients"],
    responses={404: {"error": "Not found"}}
)

class PatientBase(BaseModel):
    """Base schema for patient data."""
    name: str = Field(None, description="Full name of the patient", example="John Doe")
    address: str = Field(None, description="Address of the patient", example="123 Main St, City, Country")
    phone: str = Field(None, description="Phone number of the patient", example="+1234567890")
    email: str = Field(None,description="email")
    description: str = Field(None, description="Description of the patient", example="Patient with a history of diabetes")

@router.post("/", response_model=PatentOut)
def create_patient(patent: PatentCreate, db: Session = Depends(get_db)):
    pass
    # return crud.create_patent(db, patent)


@router.get("/") #, dependencies=Depends()
def read_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Patient).offset(skip).limit(limit).all()
    # return crud.get_patents(db, skip=skip, limit=limit)


@router.get("/{patient_id}", response_model=PatentOut)
def read_patent(patent_id: int, db: Session = Depends(get_db)):
    pass
    # db_patent = crud.get_patent(db, patent_id)
    # if not db_patent:
    #     raise HTTPException(status_code=404, detail="Patent not found")
    # return db_patent


@router.put("/{patent_id}", response_model=PatentOut)
def update_patent(patent_id: int, patent: PatentUpdate, db: Session = Depends(get_db)):
    pass
    # return crud.update_patent(db, patent_id, patent)


@router.delete("/{patent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patent(patent_id: int, db: Session = Depends(get_db)):
    pass
    # return crud.delete_patent(db, patent_id)
