from datetime import date
from typing import Literal, Union, Optional, List, Any

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

    medicine: Optional[str] = None
    type: Optional[Literal["tablet", "syrup", "injection", "ointment", "capsule"]] = None
    count: Optional[Union[int, str]] = None  # int for tablets, str for ml or other units
    morning: Optional[bool] = None
    afternoon: Optional[bool] = None
    night: Optional[bool] = None
    beforeMeal: Optional[Union[bool, str]] = None
    afterMeal: Optional[Union[bool, str]] = None
    duration: Optional[str] = None
    notes: str = Field(default="")


class VisitCreate(BaseModel):
    appointment_id: str
    analysis: Optional[str] = None
    advice: Optional[str] = None
    tests: Optional[str] = None
    followUpVisit: Optional[str] = None
    medicationDetails: Optional[List[MedicationDetails]] = None

    model_config = {"from_attributes": True}


class VisitOut(BaseModel):
    # id: Optional[UUID] = Field(default_factory=uuid.uuid4)
    patient_id: str
    doctor_id: str
    appointment_id: str  # Optional[UUID] = None

    analysis: Optional[str] = None
    advice: Optional[str] = None
    tests: Optional[str] = None  # or define a TestDetails model if structured
    followUpVisit: Optional[str] = None
    medicationDetails: Optional[List[MedicationDetails]] = None

    model_config = {"from_attributes": True}


class VisitResponse(BaseModel):
    patient_id: str
    appointment_date: date
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    mobile: Optional[str] = None
    type: Optional[str] = None  # e.g., "new", "follow-up"
    analysis: Optional[str] = None
    advice: Optional[str] = None
    tests: Optional[List[str]] = None  # or define a TestDetails model if structured
    followUpVisit: Optional[str] = None
    medicationDetails: Any  # Optional[List[MedicationDetails]] = None  # Optional[List[MedicationDetails]] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            patient_id=row.patient_id,
            # doctor_id=row.doctor_id,
            # appointment_id=row.doctor_id,
            appointment_date=row.appointments.scheduled_date,
            firstName=row.patient.firstName,
            lastName=row.patient.lastName,
            mobile=row.patient.mobile,
            type=row.appointments.type,
            analysis=row.analysis,
            advice=row.analysis,
            tests=row.tests,
            followUpVisit=row.followUpVisit,
            medicationDetails=row.medicationDetails,
            # MedicationDetails(**json.loads(row.medicationDetails)) if row.medicationDetails else None,
        )

    model_config = {"from_attributes": True}
