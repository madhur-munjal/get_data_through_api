from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.models.patients import PatientRecord, PatientUpdate
from src.models.response import APIResponse
from src.schemas.tables.patients import Patient

router = APIRouter(
    prefix="/patients", tags=["patients"], responses={404: {"error": "Not found"}}
)


@router.post("/register", response_model=APIResponse)
def create_patient(
    request: PatientRecord,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Sample API to register patient, We will create a patient in Appointment API."""
    if db.query(Patient).filter_by(mobile=request.mobile).first():
        return APIResponse(
            status_code=200,
            success=False,
            message="Mobile number already exists",
            data=None,
        ).model_dump()

    patient = Patient(**request.model_dump(), assigned_doctor_id=doctor_id)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return APIResponse(
        status_code=200,
        success=True,
        message="Patient created successfully.",
        data={"id": patient.patient_id},
    ).model_dump()


@router.put("/{patent_id}", response_model=APIResponse[PatientRecord])
def update_patent(
    patient_id: str,
    update_data: PatientUpdate,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return APIResponse(
        status_code=200,
        success=True,
        message="Patient updated successfully.",
        data=None,  # return updated patient record
    ).model_dump()


@router.get("/get_patients_list", response_model=APIResponse[List[PatientRecord]]) #  #APIResponse[PatientRecord]
def get_patients_list(
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    patients = db.query(Patient).filter(Patient.assigned_doctor_id == doctor_id).all()
    return APIResponse(
        status_code=200,
        success=True,
        message="Patients fetched successfully.",
        data=[PatientRecord.model_validate(p) for p in patients],
    ).model_dump()