from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MedicineBase(BaseModel):
    medicine_name: str = Field(..., min_length=1, max_length=255)
    # generic_name: Optional[str] = Field(None, max_length=255)
    composition: Optional[str] = None  # NEW: e.g., "Paracetamol 500mg, Caffeine 65mg"
    manufacturer: Optional[str] = Field(None, max_length=255)
    # description: Optional[str] = None
    # dosage_form: Optional[str] = Field(None, max_length=100)
    # strength: Optional[str] = Field(None, max_length=100)
    # price: float = Field(..., gt=0)
    # stock_quantity: int = Field(default=0, ge=0)
    # is_prescription_required: bool = False
    # is_active: bool = True
    is_deleted: bool = False

    model_config = {"from_attributes": True}


class MedicineCreate(MedicineBase):
    medicine_name: str = Field(..., min_length=1, max_length=255)
    composition: Optional[str] = None  # NEW: e.g., "Paracetamol 500mg, Caffeine 65mg"
    manufacturer: Optional[str] = Field(None, max_length=255)

    model_config = {"from_attributes": True}


class MedicineUpdate(BaseModel):
    medicine_id: str
    medicine_name: str = Field(..., min_length=1, max_length=255)
    composition: Optional[str] = None  # NEW: e.g., "Paracetamol 500mg, Caffeine 65mg"
    manufacturer: Optional[str] = Field(None, max_length=255)

    model_config = {"from_attributes": True}


class MedicineResponse(MedicineBase):
    medicine_id: str
    medicine_name: str = Field(..., min_length=1, max_length=255)
    composition: Optional[str] = None  # NEW: e.g., "Paracetamol 500mg, Caffeine 65mg"
    manufacturer: Optional[str] = Field(None, max_length=255)
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            medicine_id=row.medicine_id,
            medicine_name=row.medicine_name,
            composition=row.composition,
            manufacturer=row.manufacturer,
            created_at=row.created_at,
            updated_at=row.updated_at
        )


class MedicineDeleteIn(BaseModel):
    ids_to_delete: list[str]

    model_config = {"from_attributes": True}
