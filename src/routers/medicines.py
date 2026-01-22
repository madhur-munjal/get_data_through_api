from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.models.medicines import MedicineCreate, MedicineResponse
from src.models.response import APIResponse
from src.schemas.tables.medicines import Medicine

router = APIRouter(prefix="/medicines", tags=["Medicines"])


# Create Medicine
@router.post("/", response_model=APIResponse[MedicineResponse], status_code=201)
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db),
                    doctor_id: UUID = Depends(get_current_doctor_id)):
    # Check if medicine with same name already exists
    existing = db.query(Medicine).filter(Medicine.medicine_name == medicine.medicine_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Medicine with this name already exists")

    db_medicine = Medicine(**medicine.dict())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New Medicine created.",
        data=MedicineResponse.model_validate(db_medicine)
    ).model_dump()


# Get All Medicines (with pagination and filters)
@router.get("/")
def get_medicines(
        # skip: int = Query(0, ge=0),
        # limit: int = Query(100, ge=1, le=100),
        search: Optional[str] = None,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id)
):
    query = db.query(Medicine)

    # Apply filters - now includes composition search
    if search:
        query = query.filter(
            (Medicine.medicine_name.ilike(f"%{search}%")) |
            # (Medicine.generic_name.ilike(f"%{search}%")) |
            (Medicine.composition.ilike(f"%{search}%"))  # NEW: Search in composition
        )

    # if is_active is not None:
    query = query.filter(Medicine.is_deleted == False)

    # medicines = query.offset(skip).limit(limit).all()
    total_records = query.count()
    # medicines = query.all()
    return APIResponse(
        status_code=200,
        success=True,
        message="Medicines details fetched successfully.",
        data={"total_records": total_records,
                  "medicines_list": [MedicineResponse.from_row(row) for row in query]}
        # Try with MedicineResponse.model_validate(db_medicine)
    ).model_dump()

# # Update Medicine
# @router.put("/{medicine_id}", response_model=MedicineResponse)
# def update_medicine(
#         medicine_id: int,
#         medicine_update: MedicineUpdate,
#         db: Session = Depends(get_db)
# ):
#     db_medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
#     if not db_medicine:
#         raise HTTPException(status_code=404, detail="Medicine not found")
#
#     # Update only provided fields
#     update_data = medicine_update.dict(exclude_unset=True)
#
#     # Check for name conflict if name is being updated
#     if "name" in update_data and update_data["name"] != db_medicine.name:
#         existing = db.query(Medicine).filter(Medicine.name == update_data["name"]).first()
#         if existing:
#             raise HTTPException(status_code=400, detail="Medicine with this name already exists")
#
#     for field, value in update_data.items():
#         setattr(db_medicine, field, value)
#
#     db.commit()
#     db.refresh(db_medicine)
#     return db_medicine
#
#
# # Delete Medicine (soft delete by setting is_active to False)
# @router.delete("/{medicine_id}", status_code=204)
# def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
#     db_medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
#     if not db_medicine:
#         raise HTTPException(status_code=404, detail="Medicine not found")
#
#     # Soft delete
#     db_medicine.is_active = False
#     db.commit()
#     return None
#
