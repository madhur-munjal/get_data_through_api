from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.models.medicines import (
    MedicineCreate,
    MedicineResponse,
    MedicineUpdate,
    MedicineDeleteIn,
)
from src.models.response import APIResponse
from src.schemas.tables.medicines import Medicine
from src.utility import save_data_to_db

router = APIRouter(prefix="/medicines", tags=["Medicines"])


# Create Medicine
@router.post("/add", status_code=201)
def create_medicine(
    medicine: MedicineCreate,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    # Check if medicine with same name already exists
    existing = (
        db.query(Medicine)
        .filter(
            Medicine.doctor_id == doctor_id,
            Medicine.medicine_name == medicine.medicine_name,
        )
        .first()
    )
    if existing:
        # existing_deleted = existing.filter(Medicine.is_deleted == 1).first()
        if existing.is_deleted == 1:
            update_data = medicine.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing, field, value)
            existing.is_deleted = False
            db.commit()
            db.refresh(existing)
            return APIResponse(
                status_code=200,
                success=True,
                message=f"Medicine details updated successfully.",
                data=MedicineUpdate.model_validate(existing),
            ).model_dump()
        else:
            raise HTTPException(
                status_code=400, detail="Medicine with this name already exists"
            )
    medicine_data = medicine.dict()
    medicine_data["doctor_id"] = str(doctor_id)
    save_data_to_db(
        data=medicine_data, db_model=Medicine, db_session=db
    )  # Example usage of utility function
    return APIResponse(
        status_code=200,
        success=True,
        message=f"New Medicine created.",
        data=medicine.dict(),
    ).model_dump()


# Get All Medicines (with pagination and filters)
@router.get("")
def get_medicines(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1),
):
    query = db.query(Medicine).filter(
        Medicine.doctor_id == doctor_id, Medicine.is_deleted == 0
    )

    # Apply filters - now includes composition search
    if search:
        query = query.filter(
            (Medicine.medicine_name.ilike(f"%{search}%"))
            |
            # (Medicine.generic_name.ilike(f"%{search}%")) |
            (Medicine.composition.ilike(f"%{search}%"))  # NEW: Search in composition
        )

    # medicines = query.offset(skip).limit(limit).all()
    total_records = query.count()
    query = query.order_by(Medicine.medicine_name)
    if page is not None and page_size is not None:
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).all()
    elif page_size is not None:
        # Only page_size provided (limit results but no offset)
        query = query.limit(page_size).all()
    else:
        query = query.all()

    return APIResponse(
        status_code=200,
        success=True,
        message="Medicines details fetched successfully.",
        data={
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "medicines_list": [MedicineResponse.from_row(row) for row in query],
        },
    ).model_dump()


@router.get("/{medicine_id}")
def get_medicine_by_id(
    medicine_id: str,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    db_medicine = (
        db.query(Medicine)
        .filter(
            Medicine.doctor_id == doctor_id,
            Medicine.is_deleted == 0,
            Medicine.medicine_id == medicine_id,
        )
        .first()
    )
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found.")
    return APIResponse(
        status_code=200,
        success=True,
        message="Medicine details fetched successfully.",
        data=MedicineResponse.from_row(db_medicine),
    ).model_dump()


# Update Medicine
@router.put("/update")
def update_medicine(
    medicine_update: MedicineUpdate,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    medicine_id = medicine_update.medicine_id
    db_medicine = (
        db.query(Medicine)
        .filter(Medicine.doctor_id == doctor_id, Medicine.medicine_id == medicine_id)
        .first()
    )
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")

    # Update only provided fields
    update_data = medicine_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_medicine, field, value)

    db.commit()
    db.refresh(db_medicine)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Medicine details updated successfully.",
        data=MedicineUpdate.model_validate(db_medicine),
    ).model_dump()


@router.post("/delete")
def soft_delete_billing(
    ids_to_delete: MedicineDeleteIn,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Delete billing details on basis of billing id."""
    rows_updated = (
        db.query(Medicine)
        .filter(Medicine.doctor_id == doctor_id)
        .filter(Medicine.medicine_id.in_(ids_to_delete.ids_to_delete))
        .update({Medicine.is_deleted: True}, synchronize_session=False)
    )
    db.commit()
    if rows_updated == 0:
        raise HTTPException(
            status_code=404, detail="No medicines records found for given IDs"
        )
    return APIResponse(
        status_code=200,
        success=True,
        message=f"{rows_updated} billing records marked as deleted",
        data=f"Medicines {ids_to_delete.ids_to_delete} marked as deleted",
    ).model_dump()
