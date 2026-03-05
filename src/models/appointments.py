from datetime import date, time
from typing import Optional, Literal, List

from pydantic import BaseModel, Field, field_validator

from src.models.patients import PatientUpdateWhileAppointment
from .enums import AppointmentStatus, PaymentStatus, Gender, TemperatureUnit


class AppointmentCreate(BaseModel):
    patient: PatientUpdateWhileAppointment  # Nested patient data
    bloodGroup: Optional[Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]] = (
        None
    )
    weight: Optional[float] = None
    bloodPressureUpper: Optional[int] = None
    bloodPressureLower: Optional[int] = None
    temperature: Optional[float] = None
    temperatureType: Optional[TemperatureUnit] = None
    pulseRate: Optional[int] = None
    bloodSugar: Optional[float] = None

    scheduled_date: str  # "08/25/2025"
    scheduled_time: str  # "16:00:00"

    @field_validator("bloodGroup", mode="before")
    def normalize_case(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    model_config = {"from_attributes": True}


class AppointmentOut(BaseModel):
    """Schema for appointment output, used in response of create_appointment and update appointment API"""

    patient_id: str
    doctor_id: str
    # scheduled_date_time: datetime
    scheduled_date: date
    scheduled_time: time
    status: int = Field(default=AppointmentStatus.UPCOMING)  # AppointmentStatus

    model_config = {"from_attributes": True}


class AppointmentResponse(BaseModel):
    """Schema for appointment output., used in get_appointment_list API"""

    appointment_id: str
    scheduled_date: str
    scheduled_time: str
    patient_id: str
    mobile: str
    type: int  # New Patient, Follow-up
    status: int  # Completed, Upcoming, Cancelled
    paymentStatus: int = Field(default=PaymentStatus.UNPAID.value)  # Paid, Unpaid
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    paymentDetails: Optional[list] = None
    amount: Optional[float] = None
    pulseRate: Optional[int] = None
    bloodSugar: Optional[float] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            appointment_id=row["appointment"].id,
            scheduled_date=row["appointment"].scheduled_date.strftime("%m/%d/%Y"),
            scheduled_time=row["appointment"].scheduled_time.strftime(
                "%H:%M:%S"
            ),  # datetime.strptime( "%H:%M"),
            patient_id=row["appointment"].patient_id,
            mobile=row["patient"].mobile,
            firstName=row["patient"].firstName,
            lastName=row["patient"].lastName,
            type=row["appointment"].type,
            status=row["appointment"].status,
            paymentStatus=row["appointment"].payment_status,
            paymentDetails=row["billing"].get("billing_summary"),
            amount=row["billing"].get("total_amount"),
            pulseRate=row["appointment"].extra_fields.get("pulseRate") if row["appointment"].extra_fields else None,
            bloodSugar=row["appointment"].extra_fields.get("bloodSugar") if row["appointment"].extra_fields else None,
            # get_appointment_status(
            #     datetime.strptime(f"{row.scheduled_date} {row.scheduled_time}", "%Y-%m-%d %H:%M:%S")
            #     ) if str(row.status) != AppointmentStatus.COMPLETED.value else row.status
            #     # status=get_appointment_status(datetime.combine(row.scheduled_date, row.scheduled_time)) if str(
            #     row.status) != AppointmentStatus.COMPLETED.value else row.status
        )


class AppointmentUpdate(BaseModel):
    patient: PatientUpdateWhileAppointment  # Nested patient data
    bloodGroup: Optional[Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]] = (
        None
    )
    weight: Optional[float] = None
    bloodPressureUpper: Optional[int] = None
    bloodPressureLower: Optional[int] = None
    temperature: Optional[float] = None
    temperatureType: Optional[TemperatureUnit] = None
    pulseRate: Optional[int] = None
    bloodSugar: Optional[float] = None
    scheduled_date: str  # "08/25/2025"
    scheduled_time: str  # "16:00:00"

    @field_validator("bloodGroup", mode="before")
    def normalize_case(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v


class AppointmentById(BaseModel):
    """Schema to get patient and appointment details by appointment id"""

    patient_id: str
    firstName: str  # Required
    lastName: Optional[str] = None
    age: Optional[int] = None
    mobile: str  # Required
    gender: Optional[Gender] = None
    address: Optional[str] = None
    lastVisit: Optional[date] = None
    bloodGroup: Optional[Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]] = (
        None
    )
    weight: Optional[float] = None
    bloodPressureUpper: Optional[int] = None
    bloodPressureLower: Optional[int] = None
    temperature: Optional[float] = None
    temperatureType: Optional[TemperatureUnit] = None
    # patient: PatientOut
    type: int
    status: int
    paymentStatus: int = Field(default=PaymentStatus.UNPAID.value)
    pulseRate: Optional[int] = None
    bloodSugar: Optional[float] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row):
        return cls(
            patient_id=row.patient_id,
            firstName=row.patient.firstName,
            lastName=row.patient.lastName,
            age=row.patient.age,
            mobile=row.patient.mobile,
            gender=row.patient.gender,
            address=row.patient.address,
            lastVisit=row.patient.lastVisit,
            bloodGroup=row.extra_fields.get("bloodGroup"),
            weight=row.extra_fields.get("weight"),
            bloodPressureUpper=row.extra_fields.get("bloodPressureUpper"),
            bloodPressureLower=row.extra_fields.get("bloodPressureLower"),
            temperature=row.extra_fields.get("temperature"),
            temperatureType=row.extra_fields.get("temperatureType"),
            type=row.type,
            status=row.status,
            paymentStatus=row.payment_status,
            pulseRate=row.extra_fields.get("pulseRate"),
            bloodSugar=row.extra_fields.get("bloodSugar"),
        )


class PaginatedAppointmentResponse(BaseModel):
    page: Optional[int] = None
    page_size: Optional[int] = None
    total_records: int
    appointment_list: List[AppointmentResponse]
