from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.patients import PatientDTO
from src.models.response import APIResponse
from src.schemas.tables.patients import Patient
from src.dependencies import get_current_doctor_id


router = APIRouter(
    prefix="/patients", tags=["patients"], responses={404: {"error": "Not found"}}
)


@router.post("/register", response_model=APIResponse)
def create_patient(
    request: PatientDTO,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    if db.query(Patient).filter_by(email=request.email).first():
        return APIResponse(
            status_code=200, success=False, message="Email already exists", data=None
        ).model_dump()
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
        success=False,
        message="Patient created successfully.",
        data={"id": patient.patient_id},
    ).model_dump()


# @router.get("/")  # , dependencies=Depends()
# def read_patients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     return db.query(Patient).offset(skip).limit(limit).all()
# return crud.get_patents(db, skip=skip, limit=limit)


# @router.get("/{patient_id}", response_model=PatentOut)
# def read_patent(patent_id: int, db: Session = Depends(get_db)):
#     pass
#     # db_patent = crud.get_patent(db, patent_id)
#     # if not db_patent:
#     #     raise HTTPException(status_code=404, detail="Patent not found")
#     # return db_patent
#
#
# @router.put("/{patent_id}", response_model=PatentOut)
# def update_patent(patent_id: int, patent: PatentUpdate, db: Session = Depends(get_db)):
#     pass
#     # return crud.update_patent(db, patent_id, patent)
#
#
# @router.delete("/{patent_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_patent(patent_id: int, db: Session = Depends(get_db)):
#     pass
#     # return crud.delete_patent(db, patent_id)
