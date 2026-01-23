from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.utility import save_data_to_db
from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.models.medicines import MedicineCreate, MedicineResponse, MedicineUpdate, MedicineDeleteIn
from src.models.response import APIResponse
from src.schemas.tables.medicines import Medicine

router = APIRouter(prefix="/medicines", tags=["Medicines"])


# Create Medicine
@router.post("/add", status_code=201)
def create_medicine(medicine: MedicineCreate, db: Session = Depends(get_db),
                    doctor_id: UUID = Depends(get_current_doctor_id)):
    # Check if medicine with same name already exists
    existing = db.query(Medicine).filter(Medicine.medicine_name == medicine.medicine_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Medicine with this name already exists")
    medicine_data = medicine.dict()
    medicine_data['doctor_id'] = str(doctor_id)
    save_data_to_db(data=medicine_data, db_model=Medicine, db_session=db)  # Example usage of utility function
    # medicine['doctor_id'] = str(doctor_id)
    # db_medicine = Medicine(**medicine.dict())
    # db.add(db_medicine)
    # db.commit()
    # db.refresh(db_medicine)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New Medicine created.",
        data=medicine.dict()
    ).model_dump()


# Get All Medicines (with pagination and filters)
@router.get("")
def get_medicines(
        # skip: int = Query(0, ge=0),
        # limit: int = Query(100, ge=1, le=100),
        search: Optional[str] = None,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1),
):
    query = db.query(Medicine)

    # Apply filters - now includes composition search
    if search:
        query = query.filter(Medicine.doctor_id == doctor_id).filter(
            (Medicine.medicine_name.ilike(f"%{search}%")) |
            # (Medicine.generic_name.ilike(f"%{search}%")) |
            (Medicine.composition.ilike(f"%{search}%"))  # NEW: Search in composition
        )

    # if is_active is not None:
    query = query.filter(Medicine.is_deleted == False)

    # medicines = query.offset(skip).limit(limit).all()
    total_records = query.count()
    # medicines = query.all()
    offset = (page - 1) * page_size
    query = query.order_by(Medicine.medicine_name).offset(offset).limit(page_size).all()

    return APIResponse(
        status_code=200,
        success=True,
        message="Medicines details fetched successfully.",
        data={"total_records": total_records,
              "medicines_list": [MedicineResponse.from_row(row) for row in query]}
        # Try with MedicineResponse.model_validate(db_medicine)
    ).model_dump()


# Update Medicine
@router.put("/update/{medicine_id}")
def update_medicine(
        medicine_id: str,
        medicine_update: MedicineUpdate,
        db: Session = Depends(get_db)
):
    db_medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    # Update only provided fields
    update_data = medicine_update.dict(exclude_unset=True)

    # # Check for name conflict if name is being updated
    # if "name" in update_data and update_data["name"] != db_medicine.name:
    #     existing = db.query(Medicine).filter(Medicine.name == update_data["name"]).first()
    #     if existing:
    #         raise HTTPException(status_code=400, detail="Medicine with this name already exists")

    for field, value in update_data.items():
        setattr(db_medicine, field, value)

    db.commit()
    db.refresh(db_medicine)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Appointment updated successfully.",
        data=MedicineUpdate.model_validate(db_medicine),
    ).model_dump()


@router.post("/delete")
def soft_delete_billing(
        ids_to_delete: MedicineDeleteIn,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Delete billing details on basis of billing id."""
    rows_updated = db.query(Medicine).filter(Medicine.id.in_(ids_to_delete.ids_to_delete)).update(
        {Medicine.is_deleted: True},
        synchronize_session=False)
    db.commit()
    if rows_updated == 0:
        raise HTTPException(status_code=404, detail="No billing records found for given IDs")
    return APIResponse(
        status_code=200,
        success=True,
        message=f"{rows_updated} billing records marked as deleted",
        data=f"Medicines {ids_to_delete} marked as deleted"
    ).model_dump()
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
