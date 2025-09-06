from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.dependencies import require_owner
from src.models.patients import PatientRecord, PatientUpdate, PatientOut, PaginatedPatientResponse
from src.models.response import APIResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.patients import Patient

router = APIRouter(
    prefix="/patients", tags=["patients"], responses={404: {"error": "Not found"}},
    dependencies=[Depends(require_owner)]

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


@router.put("/{patient_id}", response_model=APIResponse[PatientRecord])
def update_patent(
        patient_id: str,
        update_data: PatientUpdate,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
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
        data=None,  # return updated patient record
    ).model_dump()


@router.get("", response_model=APIResponse[PaginatedPatientResponse])
def get_patients_list(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1),
        text: str = Query(None, description="Search by patient's first name, last name or mobile number"),
        # month: str = Query(None, description="Filter by month "),
        age: int = Query(None, description="Filter by patient age"),
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    offset = (page - 1) * page_size
    query = db.query(Patient).filter_by(assigned_doctor_id=doctor_id)

    if text:
        query = query.filter(
            or_(
                Patient.firstName.ilike(f"%{text}%"),
                Patient.lastName.ilike(f"%{text}%"),
                Patient.mobile.ilike(f"%{text}%")
            )
        )
    total_records = db.query(Patient).filter_by(assigned_doctor_id=doctor_id).count()
    results = query.order_by(
        desc(Patient.created_at)).offset(offset).limit(page_size).all()

    # results = db.query(Appointment).filter_by(doctor_id=doctor_id).order_by(
    #     desc(Appointment.scheduled_date)).offset(offset).limit(page_size).all()
    # TODO need to add time as well
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched appointment lists.",
        data={"page": page, "page_size": page_size, "total_records": total_records,
              "patient_list": [PatientOut.model_validate(p) for p in results]}
    ).model_dump()

    # patients = db.query(Patient).filter(Patient.assigned_doctor_id == doctor_id).all()
    # return APIResponse(
    #     status_code=200,
    #     success=True,
    #     message="Patients fetched successfully.",
    #     data=[PatientOut.model_validate(p) for p in patients],
    # ).model_dump()


@router.get("/{patient_id}",
            response_model=APIResponse[PatientRecord])
def get_patients_details_with_appointment_list(
        patient_id: str,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    patient = db.query(Patient).filter_by(assigned_doctor_id=doctor_id, patient_id=patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointment_details = db.query(Appointment).filter_by(doctor_id=doctor_id, patient_id=patient_id).all()

    # def to_dict(obj):
    final_data = {column.name: getattr(patient, column.name) for column in patient.__table__.columns}
    final_data["list_of_appointments"] = [row.scheduled_date for row in appointment_details]

    return APIResponse(
        status_code=200,
        success=True,
        message="Patients fetched successfully.",
        data=PatientRecord.model_validate(final_data)
    ).model_dump()


@router.get("/get_patients_list_on_basis_of_mobile/{mobile}", response_model=APIResponse)
def get_patients_list_on_basis_of_mobile(
        mobile: str,  # = mobile_no,  # Query(None, description="Search by patient's mobile number"),
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id)
):
    query = db.query(Patient).filter_by(assigned_doctor_id=doctor_id)

    if mobile:
        query = query.filter(
            or_(
                Patient.mobile.ilike(f"%{mobile}%")
            )
        )
    results = query.all()
    # final_data = {column.name: getattr(Patient, column.name) for column in Patient.__table__.columns}
    # print(results)
    # print([PatientOut.model_validate(p) for p in results])
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched patients lists.",
        data={"patient_list": [PatientOut.model_validate(row) for row in results]}
    ).model_dump()
