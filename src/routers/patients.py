from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, or_, func
from sqlalchemy.orm import Session, aliased

# from src.utility import get_subscription_active_status_by_doctor
from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.models.patients import (
    PatientRecord,
    PatientUpdate,
    PatientOut,
    PaginatedPatientResponse,
)
from src.models.response import APIResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.patients import Patient
from src.schemas.tables.visits import Visit

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
    responses={404: {"error": "Not found"}},
    # ,
    # dependencies=[Depends(require_owner)]
)


@router.post("/register", response_model=APIResponse)
def create_patient(
    request: PatientUpdate,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    """Sample API to register patient, We will create a patient in Appointment API."""
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
        success=True,
        message="Patient created successfully.",
        data={"id": patient.patient_id},
    ).model_dump()


@router.put("/{patient_id}", response_model=APIResponse[PatientOut])
def update_patent(
    patient_id: str,
    update_data: PatientUpdate,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    patient = db.query(Patient).filter_by(patient_id=patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return APIResponse(
        status_code=200,
        success=True,
        message="Patient updated successfully.",
        data=PatientOut.model_validate(
            patient
        ).model_dump(),  # None,  # return updated patient record
    ).model_dump()


@router.get("", response_model=APIResponse[PaginatedPatientResponse])
def get_patients_list(
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1),
    # page: int = Query(1, ge=1),
    # page_size: int = Query(20, ge=1),
    text: str = Query(
        None, description="Search by patient's first name, last name or mobile number"
    ),
    # month: str = Query(None, description="Filter by month "),
    minAge: int = Query(None, description="Filter by patient minimum age"),
    maxAge: int = Query(None, description="Filter by patient maximum age"),
    startDate: str = Query(
        None, description="Filter by start date in YYYY-MM-DD format"
    ),
    # these dates used for appointments
    endDate: str = Query(None, description="Filter by end date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    # offset = (page - 1) * page_size
    patient_query = db.query(Patient).filter_by(assigned_doctor_id=doctor_id)

    if text:
        patient_query = patient_query.filter(
            or_(
                Patient.firstName.ilike(f"%{text}%"),
                Patient.lastName.ilike(f"%{text}%"),
                Patient.mobile.ilike(f"%{text}%"),
            )
        )

    if minAge or maxAge:
        if minAge and maxAge:
            patient_query = patient_query.filter(Patient.age.between(minAge, maxAge))
        elif minAge:
            patient_query = patient_query.filter(Patient.age >= minAge)
        elif maxAge:
            patient_query = patient_query.filter(Patient.age <= maxAge)

    # 📆 Date range filter: match between startDate and endDate of their appointments
    if startDate and endDate:
        try:
            start_date_obj = datetime.strptime(startDate, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(endDate, "%Y-%m-%d").date()
            patient_query = patient_query.join(
                Appointment, Patient.patient_id == Appointment.patient_id
            ).filter(Appointment.scheduled_date.between(start_date_obj, end_date_obj))
        except ValueError:
            return APIResponse(
                status_code=200,
                success=True,
                message=f"ValueError wile filtering from startDate and EndDate.",
                data=None,
            ).model_dump()

    latest_date_subq = (
        db.query(
            Appointment.patient_id,
            func.max(Appointment.created_at).label("latest_date"),
        )
        .group_by(Appointment.patient_id)
        .subquery()
    )
    # Alias the Appointment table
    LatestAppointment = aliased(Appointment)

    # Subquery to get patient_id and type from latest appointment
    get_type = (
        db.query(LatestAppointment.patient_id, LatestAppointment.type)
        .join(
            latest_date_subq,
            (LatestAppointment.patient_id == latest_date_subq.c.patient_id)
            & (LatestAppointment.created_at == latest_date_subq.c.latest_date),
        )
        .subquery()
    )
    patient_query = patient_query.outerjoin(
        get_type, Patient.patient_id == get_type.c.patient_id
    ).add_columns(get_type.c.type.label("latest_appointment_type"))
    total_records = patient_query.count()
    results = patient_query.order_by(desc(Patient.created_at))
    if page is not None and page_size is not None:
        offset = (page - 1) * page_size
        final_query = results.offset(offset).limit(page_size).all()
    elif page_size is not None:
        # Only page_size provided (limit results but no offset)
        final_query = results.limit(page_size).all()
    else:
        final_query = results.all()
    # TODO need to add time as well
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched patient lists.",
        data={
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "patient_list": [PatientOut.from_row(p) for p in final_query],
        },
    ).model_dump()

    # patients = db.query(Patient).filter(Patient.assigned_doctor_id == doctor_id).all()
    # return APIResponse(
    #     status_code=200,
    #     success=True,
    #     message="Patients fetched successfully.",
    #     data=[PatientOut.model_validate(p) for p in patients],
    # ).model_dump()


@router.get("/{patient_id}", response_model=APIResponse[PatientRecord])
def get_patients_details_with_appointment_list(
    patient_id: str,
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    patient = (
        db.query(Patient)
        .filter_by(assigned_doctor_id=doctor_id, patient_id=patient_id)
        .first()
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # appointment_details = db.query(Appointment).filter_by(doctor_id=doctor_id, patient_id=patient_id).all()
    visit_details = (
        db.query(Visit).filter_by(doctor_id=doctor_id, patient_id=patient_id).all()
    )

    final_data = {
        column.name: getattr(patient, column.name)
        for column in patient.__table__.columns
    }
    final_data["list_of_appointments"] = [
        row.appointments.scheduled_date for row in visit_details
    ]

    return APIResponse(
        status_code=200,
        success=True,
        message="Patients fetched successfully.",
        data=PatientRecord.model_validate(final_data),
    ).model_dump()


@router.get(
    "/get_patients_list_on_basis_of_mobile/{mobile}", response_model=APIResponse
)
def get_patients_list_on_basis_of_mobile(
    mobile: str,  # = mobile_no,  # Query(None, description="Search by patient's mobile number"),
    db: Session = Depends(get_db),
    doctor_id: UUID = Depends(get_current_doctor_id),
):
    # get_subscription_active_status = get_subscription_active_status_by_doctor(
    #     db, doctor_id
    # )
    # if get_subscription_active_status is False:
    #     return APIResponse(
    #         status_code=200,
    #         success=False,
    #         message="Your subscription has expired. Please renew your subscription to access this feature.",
    #         data=None,
    #     ).model_dump()
    query = db.query(Patient).filter_by(assigned_doctor_id=doctor_id)

    if mobile:
        query = query.filter(or_(Patient.mobile.ilike(f"%{mobile}%")))
    results = query.all()
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched patients lists.",
        data={"patient_list": [PatientOut.model_validate(row) for row in results]},
    ).model_dump()
