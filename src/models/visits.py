from typing import Literal, Union
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class MedicationDetails(BaseModel):
    """
    Data to store for medicationDetails for  visit page, sample data:
        "medicationDetails": [
        {
            "medicine": "Dolo 500",
            "type": "tablet",
            "count": 1,
            "morning": true,
            "afternoon": false,
            "night": true,
            "beforeMeal": false,
            "duration": "5 days",
            "notes": ""
        },
        {
            "medicine": "Multivitamin Syrup",
            "type": "syrup",
            "count": "10ml",
            "morning": true,
            "afternoon": true,
            "night": true,
            "beforeMeal": "true",
            "duration": "5 days",
            "notes": "SOS"
}
]
    """
    medicine: str
    type: Literal["tablet", "syrup", "injection", "ointment", "capsule"]
    count: Union[int, str]
    morning: bool
    afternoon: bool
    night: bool
    beforeMeal: Union[bool, str]
    afterMeal: Union[bool, str]
    duration: str
    notes: str = Field(default="")


# class VisitDB(BaseModel):
#     id: str
#     patient_id: int
#     doctor_id: int
#     appointment_id: Optional[int] = None
#     analysis: str
#     advice: str
#     tests: List[str]
#     followUpVisit: str
#     medicationDetails: List[MedicationDetails]
#
#     model_config = {"from_attributes": True}


class PrescriptionData(BaseModel):
    medicines: list
    model_config = {"from_attributes": True}


class VisitIn(BaseModel):
    appointment_id: str
    analysis: str
    advice: str
    tests: List[str]
    followUpVisit: str
    medicationDetails: List[MedicationDetails]
    # id: int
    # patient_id: int
    # doctor_id: int
    # appointment_id: str
    # visit_time: datetime = None
    # notes: Optional[str] = None
    # diagnosis: Optional[str] = None
    # prescription: Optional[str] = None  # Need to changee to PrescriptionData
    # follow_up: Optional[str]
    model_config = {"from_attributes": True}


class VisitOut(BaseModel):
    # id: Optional[UUID] = Field(default_factory=uuid.uuid4)
    patient_id: str
    doctor_id: str
    appointment_id: str  # Optional[UUID] = None

    analysis: Optional[str] = None
    advice: Optional[str] = None
    tests: Optional[List[str]] = None  # or define a TestDetails model if structured
    followUpVisit: Optional[str] = None
    medicationDetails: Optional[List[MedicationDetails]] = None

    # patient_id:str
    # doctor_id: str
    # appointment_id: str
    # prescription: str
    # follow_up: str
    # patient: PatientOut
    # visit_time: datetime
    # notes: Optional[str]
    # diagnosis: Optional[str]
    # prescription: Optional[str]

    model_config = {"from_attributes": True}
