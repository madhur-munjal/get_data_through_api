from calendar import month_name
from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import desc
from sqlalchemy import or_, extract
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased

from src.database import get_db
from src.dependencies import get_current_doctor_id, get_current_user_payload
from src.models.appointments import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentResponse,
    AppointmentUpdate,
    PaginatedAppointmentResponse
)
from src.models.enums import AppointmentType, AppointmentStatus
from src.models.response import APIResponse
from src.models.visits import VisitAllResponse
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.billing import Billing
from src.schemas.tables.notifications import Notification
from src.schemas.tables.patients import Patient
from src.schemas.tables.visits import Visit
from src.utility import get_appointment_summary
from src.utility import save_data_to_db, get_appointment_status

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    responses={404: {"error": "Not found"}}
    # ,
    # dependencies=[Depends(require_owner)]
)

from sqlalchemy.orm import Session, joinedload

def build_appointments_query(db: Session):
    """Base query for appointments with patient preloaded."""
    return db.query(Appointment).options(joinedload(Appointment.patient))


@router.post("/create_appointment", response_model=APIResponse[AppointmentOut])
def create_appointment(
        appointment: AppointmentCreate,
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
        current_user=Depends(get_current_user_payload),
):
    """Register a new appointment.
    If enter new mobile number, then it will create under new patients record."""
    patient_data = appointment.patient.dict(exclude_unset=True)
    patient_id = patient_data.get("patient_id")
    valid_keys = {col.name for col in Patient.__table__.columns}
    filtered_data = {k: v for k, v in patient_data.items() if k in valid_keys}
    filtered_data["assigned_doctor_id"] = doctor_id

    if patient_id is None:
        type = AppointmentType.NEW.value
        patient_data["assigned_doctor_id"] = doctor_id
        # valid_keys = {col.name for col in Patient.__table__.columns}
        # filtered_data = {k: v for k, v in patient_data.items() if k in valid_keys}
        save_patient_data = save_data_to_db(filtered_data, Patient, db)
        patient_id = save_patient_data.patient_id
    else:
        type = AppointmentType.FOLLOW_UP.value
        patient = db.query(Patient).filter_by(patient_id=patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient not found with the id {patient_id}")
        for field, value in filtered_data.items():
            setattr(patient, field, value)
    data = appointment.dict()
    db_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        scheduled_date=datetime.strptime(data["scheduled_date"], "%m/%d/%Y").date(),
        scheduled_time=datetime.strptime(data["scheduled_time"], "%H:%M:%S").time(),
        type=type,
        status=get_appointment_status(
            datetime.strptime(f"{data.get('scheduled_date')} {data.get('scheduled_time')}", "%m/%d/%Y %H:%M:%S")
        ),
        bloodGroup=patient_data.get("bloodGroup"),
        weight=patient_data.get("weight"),
        bloodPressureUpper=patient_data.get("bloodPressureUpper"),
        bloodPressureLower=patient_data.get("bloodPressureLower"),
        temperature=patient_data.get("temperature"),
        temperatureType=patient_data.get("temperatureType"),
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    created_appointment_id = db_appointment.id
    updated_by = current_user.get('firstName') + " " + current_user.get('lastName') if current_user.get(
        'lastName') else current_user.get('firstName')
    notification_data = {'doctor_id': doctor_id, 'appointment_id': created_appointment_id,
                         'firstName': patient_data.get('firstName'),
                         'lastName': patient_data.get(
                             'lastName'),
                         'type': 'appointment', 'message': 'appointment created', 'updated_by': updated_by
                         }
    save_data_to_db(notification_data, Notification, db)

    return APIResponse(
        status_code=200,
        success=True,
        message=f"New Appointment created.",
        data=AppointmentOut.model_validate(db_appointment),
    ).model_dump()


@router.put("/update_appointment/{appointment_id}", response_model=APIResponse[AppointmentOut])
def update_appointment(appointment_id: str, update_data: AppointmentUpdate, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter_by(id=appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if update_data.scheduled_date:
        appointment.scheduled_date = datetime.strptime(update_data.scheduled_date, "%m/%d/%Y").date()

        # Update scheduled_time if provided
    if update_data.scheduled_time:
        appointment.scheduled_time = datetime.strptime(update_data.scheduled_time, "%H:%M:%S").time()

    # data = update_data.dict(exclude_unset=True)
    #
    # # Convert known fields
    # if "scheduled_date" in data:
    #     data["scheduled_date"] = datetime.strptime(data["scheduled_date"], "%m/%d/%Y").date()
    #
    # if "appointment_time" in data:
    #     data["scheduled_time"] = datetime.strptime(data["scheduled_time"], "%H:%M:%S").time()
    #
    # # Apply all fields
    # for key, value in data.items():
    #     print(key, value, sep="*****")
    #     setattr(appointment, key, value)
    # print(update_data.dict(exclude_unset=True))
    # print("*******")
    # print(appointment)
    # print("***********")
    # print(type(appointment))
    #
    # data = appointment.dict()
    # # data.update({"doctor_id": appointment.doctor_id})
    #
    # db_appointment = Appointment(
    #     patient_id=data.patient_id,
    #     doctor_id=data.doctor_id,
    #     scheduled_date=datetime.strptime(data.get("scheduled_date"), "%m/%d/%Y").date(),
    #     scheduled_time=datetime.strptime(data.get("scheduled_time"), "%H:%M:%S").time(),
    #     type=data.type,
    #     status=data.status
    # )
    #
    # # for key, value in update_data.dict(exclude_unset=True).items():
    # #     setattr(appointment, key, value)

    db.commit()
    db.refresh(appointment)
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Appointment updated successfully.",
        data=AppointmentOut.model_validate(appointment),
    ).model_dump()


@router.get("", response_model=APIResponse[PaginatedAppointmentResponse])
def get_appointment_data(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1),
        text: str = Query(None, description="Search by patient's first name, last name or mobile number"),
        month: str = Query(None, description="Filter by month "),
        status: str = Query(None, description="Filter by appointment status"),
        startDate: str = Query(None, description="Filter by start date in YYYY-MM-DD format"),
        endDate: str = Query(None, description="Filter by end date in YYYY-MM-DD format"),
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    query = build_appointments_query(db)

    # A = aliased(Appointment)
    # P = aliased(Patient)
    # B = aliased(Billing)
    #
    # # # query = db.query(Appointment).filter_by(doctor_id=doctor_id).outerjoin(Appointment.patient).outerjoin(Appointment.billing)
    #
    #
    # query = (
    #     db.query(
    #         A,
    #         P,
    #         B
    #         # A.id.label("appointment_id"),
    #         # A.scheduled_date,
    #         # A.scheduled_time,
    #         # A.type.label("appointment_type"),
    #         # A.status.label("appointment_status"),
    #         # A.payment_status,
    #         # P.patient_id,
    #         # P.mobile,
    #         # P.firstName,
    #         # P.lastName,
    #         # B.type.label("billing_type"),
    #         # B.amount
    #         # Appointment,
    #         # Patient,
    #         # Billing.type.label("billing_type"),
    #         # # # Billing.type,
    #         # Billing.amount
    #     )
    #     .outerjoin(P)  # , A.patient_id == P.patient_id)
    #     .outerjoin(B)  # , A.id == B.appointment_id)
    #     .filter(A.doctor_id == doctor_id, A.id.isnot(None))
    # )

    # 🔍 Text filter: match firstname, lastname, or mobile
    if text:
        query = query.filter(
            or_(
                Appointment.patient.firstName.ilike(f"%{text}%"),
                Appointment.patient.lastName.ilike(f"%{text}%"),
                Appointment.patient.mobile.ilike(f"%{text}%")
            )
        )

    # 📅 Month filter: convert month name to number and match against datetime column
    if month:
        try:
            month_number = list(month_name).index(month.capitalize())  # January = 1
            query = query.filter(extract("month", Appointment.scheduled_date) == month_number)
        except ValueError:
            pass  # Invalid month name, skip filter

    # 📌 Status filter: match against status column
    if status is not None:
        STATUS_LOOKUP = {
            "Upcoming": AppointmentStatus.UPCOMING,
            "Completed": AppointmentStatus.COMPLETED,
            "No Show": AppointmentStatus.NO_SHOW
        }
        status_enum = STATUS_LOOKUP.get(status)
        status_db_value = status_enum.value
        query = query.filter(Appointment.status == int(status_db_value))

    # 📆 Date range filter: match between startDate and endDate
    if startDate and endDate:
        try:
            start_date_obj = datetime.strptime(startDate, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(endDate, "%Y-%m-%d").date()
            query = query.filter(Appointment.scheduled_date.between(start_date_obj, end_date_obj))
        except ValueError:
            return APIResponse(
                status_code=200,
                success=True,
                message=f"ValueError wile filtering from startDate and EndDate.",
                data=None
            ).model_dump()

    # column_names = [col['name'] for col in query.column_descriptions]
    # print(column_names)
    # for row in query.all():
    #     row_dict = dict(zip(column_names, row))
    #     print(row_dict)
    offset = (page - 1) * page_size
    results = query.order_by(desc(Appointment.scheduled_date)).offset(offset).limit(page_size).all()
    # Appointment.scheduled_date.desc()

    total_records = len(results)
    appt_ids = [a.id for a in results]
    billing_data = (
        db.query(Billing.appointment_id, Billing.type, func.sum(Billing.amount).label("amt"))
        .filter(Billing.appointment_id.in_(appt_ids))
        .group_by(Billing.appointment_id, Billing.type)
        .all()
    )

    billing_map = {}
    for appointment_id, btype, amt in billing_data:
        if appointment_id not in billing_map:
            billing_map[appointment_id] = {"billing_summary": [], "total_amount": 0}
        billing_map[appointment_id]["billing_summary"].append({"type": btype, "amount": amt})
        billing_map[appointment_id]["total_amount"] += amt
        # billing_map.setdefault(appointment_id, []).append(
        #     {"type": btype, "amount": amt}
        # )
    # import pdb;pdb.set_trace()



    result = []
    for appt in results:
        patient = appt.patient
        result.append({
            "appointment": appt,
            "patient": patient,
            "billing": billing_map.get(appt.id, dict())
        })


    # pdb.set_trace()
    # results_with_group_billing = get_appointment_summary(results)
    # total_records = len(results_with_group_billing)

    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched appointment lists.",
        data={"page": page, "page_size": page_size, "total_records": total_records,
              "appointment_list": [AppointmentResponse.from_row(p) for p in result]}
    ).model_dump()


# @router.get("/{appointment_id}", response_model=APIResponse[AppointmentById])
# def get_patient_details_through_appointment_id(appointment_id: str, db: Session = Depends(get_db)):
#     appointment_details = db.query(Appointment).filter(Appointment.id == appointment_id).first()
#     if not appointment_details:
#         raise HTTPException(status_code=404, detail="Appointment not found")
#
#     # patient = db.query(Patient).filter(Patient.patient_id == appointment.patient_id).first()
#     # if not patient:
#     #     raise HTTPException(status_code=404, detail="Patient not found")
#     return APIResponse(
#         status_code=200,
#         success=True,
#         message=f"Successfully fetched appointment details.",
#         data=AppointmentById.from_row(appointment_details)
#         # PatientOut.from_row(appointment_details)  # [PatientOut.from_row(p) for p in appointment_details]
#     ).model_dump()

@router.get("/{appointment_id}", response_model=APIResponse[VisitAllResponse])
def get_patient_details_through_appointment_id(appointment_id: str, db: Session = Depends(get_db)):
    visit = db.query(Visit).filter_by(appointment_id=appointment_id).first()
    if not visit:
        appointment_details = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment_details:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return APIResponse(
            status_code=200,
            success=True,
            message=f"Successfully fetched appointment details.",
            data=VisitAllResponse.from_appointment_row(appointment_details)
        ).model_dump()
    else:
        return APIResponse(
            status_code=200,
            success=True,
            message="Successfully fetched visit details",
            data=VisitAllResponse.from_visit_row(visit),
        ).model_dump()


@router.get(
    "/get_appointment_by_date/{appointment_date}", response_model=APIResponse[list[AppointmentResponse]]
)
def get_appointment_by_date(
        appointment_date: str,  # date = Query(..., description="Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    results = (
        db.query(Appointment)
        .filter_by(doctor_id=doctor_id, scheduled_date=appointment_date)
        .all()
    )
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched appointment lists for date {appointment_date}.",
        data=[AppointmentResponse.from_row(row) for row in results],
    ).model_dump()


@router.get(
    "/booked_slots/get_date_wise_booked_slots")  # , response_model=APIResponse[list[AppointmentResponse]])
def get_date_wise_booked_slots(
        appointment_date: date = Query(..., description="Date in YYYY-MM-DD format"),
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id),
):
    results = (
        db.query(Appointment)
        .filter_by(doctor_id=doctor_id, scheduled_date=appointment_date)
        .all()
    )
    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched booked slots for {appointment_date}.",
        data=[row.scheduled_time.strftime("%H:%M") for row in results],
    ).model_dump()
