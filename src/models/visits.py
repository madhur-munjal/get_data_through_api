from datetime import date, time
from typing import Literal, Union, Optional, List, Any

from pydantic import BaseModel, Field

from .enums import Gender, TemperatureUnit, PaymentStatus


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
    notes: Optional[str] = ""  # Field(default="")


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
    type: Optional[int] = None  # e.g., "new", "follow-up"
    analysis: Optional[str] = None
    advice: Optional[str] = None
    tests: Optional[str] = None  # or define a TestDetails model if structured
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


class VisitAllResponse(BaseModel):
    """Schema to get patient and appointment and visits details by appointment id"""
    patient_id: str
    firstName: str  # Required
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str  # Required
    gender: Optional[Gender] = None
    address: Optional[str] = None
    lastVisit: Optional[date] = None
    bloodGroup: Optional[
        Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    ] = None
    weight: Optional[float] = None
    bloodPressureUpper: Optional[int] = None
    bloodPressureLower: Optional[int] = None
    temperature: Optional[float] = None
    temperatureType: Optional[TemperatureUnit] = None
    type: int
    status: int
    paymentStatus: int = Field(default=PaymentStatus.UNPAID.value)
    paymentType: Optional[str] = None
    amount: Optional[float] = None
    analysis: Optional[str] = None
    advice: Optional[str] = None
    tests: Optional[str] = None  # or define a TestDetails model if structured
    followUpVisit: Optional[str] = None
    medicationDetails: Optional[
        Any] = None  # Optional[List[MedicationDetails]] = None  # Optional[List[MedicationDetails]] = None
    paymentDetails: Optional[list] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_appointment_row(cls, row):
        return cls(
            patient_id=row.patient_id,
            firstName=row.patient.firstName,
            lastName=row.patient.lastName,
            age=row.patient.age,
            mobile=row.patient.mobile,
            gender=row.patient.gender,
            address=row.patient.address,
            lastVisit=row.patient.lastVisit,
            bloodGroup=row.patient.bloodGroup,
            weight=row.patient.weight,
            bloodPressureUpper=row.patient.bloodPressureUpper,
            bloodPressureLower=row.patient.bloodPressureLower,
            temperature=row.patient.temperature,
            temperatureType=row.patient.temperatureType,
            type=row.type,
            status=row.status,
            paymentDetails=row.payment_details,
            scheduled_date=row.scheduled_date,
            scheduled_time=row.scheduled_time,
            # analysis=row.analysis,
            # advice=row.advice,
            # tests=row.tests,
            # followUpVisit=row.followUpVisit,
            # medicationDetails=row.medicationDetails,
            paymentStatus=row.payment_status,
            paymentType=row.billing.type if row.billing else None,
            amount=row.billing.amount if row.billing else None
        )

    @classmethod
    def from_visit_row(cls, row):
        return cls(
            patient_id=row.patient.patient_id,
            firstName=row.patient.firstName,
            lastName=row.patient.lastName,
            age=row.patient.age,
            mobile=row.patient.mobile,
            gender=row.patient.gender,
            address=row.patient.address,
            lastVisit=row.patient.lastVisit,
            bloodGroup=row.patient.bloodGroup,
            weight=row.patient.weight,
            bloodPressureUpper=row.patient.bloodPressureUpper,
            bloodPressureLower=row.patient.bloodPressureLower,
            temperature=row.patient.temperature,
            temperatureType=row.patient.temperatureType,
            type=row.appointments.type,
            status=row.appointments.status,
            analysis=row.analysis,
            advice=row.advice,
            tests=row.tests,
            followUpVisit=row.followUpVisit,
            medicationDetails=row.medicationDetails,
            paymentStatus=row.appointments.payment_status,
            paymentType=row.appointments.billing.type if row.appointments.billing else None,
            amount=row.appointments.billing.amount if row.appointments.billing else None,
            paymentDetails=row.payment_details,
            scheduled_date=row.appointments.scheduled_date,
            scheduled_time=row.appointments.scheduled_time,
        )
