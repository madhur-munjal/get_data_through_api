from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from datetime import datetime


class MedicalResource(BaseModel):
    """
    Medical resource schema for patient medical records.
    """
    patient_id: int = Field(..., description="Unique identifier for the patient", example=1)
    medical_history: Dict[str, Any] = Field(..., description="Medical history of the patient",
                                            example={"allergies": "None", "conditions": "Diabetes"})
    medications: Dict[str, Any] = Field(..., description="Current medications of the patient",
                                        example={"insulin": "10 units daily"})
    allergies: Optional[str] = Field(None, description="Allergies of the patient", example="Peanuts")
    last_checkup_date: datetime = Field(..., description="Date of the last checkup", example="2023-10-01T12:00:00Z")
    followup_date: datetime = Field(..., description="Date of the next checkup", example="2023-10-01T12:00:00Z")
    notes: Optional[str] = Field(None, description="Additional notes about the patient",
                                 example="Patient is responding well to treatment")
    created_at: datetime = Field(default_factory=datetime.datetime.utcnow,
                                 description="Timestamp when the record was created")
    updated_at: datetime = Field(default_factory=datetime.datetime.utcnow,
                                 description="Timestamp when the record was last updated")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data of the patient",
                                      example="iVBORw0KGgoAAAANSUhEUgAAAAUA...")
    image_url: Optional[str] = Field(None, description="URL of the image of the patient",
                                     example="https://example.com/image.jpg")
