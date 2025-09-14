from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from src.database import get_db
from src.dependencies import get_current_doctor_id
from src.models.response import APIResponse
from src.schemas.tables.patients import Patient
from src.schemas.tables.staff import Staff

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"error": "Not found"}}
    # ,
    # dependencies=[Depends(require_owner)]
)


@router.post("/search")  # , response_model=APIResponse[AppointmentOut]
def get_patient_staff_details(
        text: str = Query(...),
        db: Session = Depends(get_db),
        doctor_id: UUID = Depends(get_current_doctor_id)
):
    """
    Used to filter patients and staff details through name and mobile.
    """
    """
    
    Sample: [
              {
                firstName: 'Akash',
                lastName: 'Tewari',
                id: 'asdasd-asdas-dasd-asd-asd',
                mobile : '9876543210',
                type: 'patient'
              },
              {
                firstName: 'Sam',
                lastName: 'Tewari',
                id: 'asdasd-asdas-dasd-asd-asd',
                type:'staff',
                mobile: '9876543210'
                }
            ]
    """
    # Search Patients
    print(text)
    print("*****")
    patient_results = db.query(Patient).filter(
        and_(Patient.assigned_doctor_id == doctor_id,
        or_(
            Patient.firstName.ilike(f"%{text}%"),
            Patient.lastName.ilike(f"%{text}%"),
            Patient.mobile.ilike(f"%{text}%")
        )
             )
    ).all()

    # Search Staff
    staff_results = db.query(Staff).filter(
        and_(Staff.doc_id == doctor_id,
             or_(
            Staff.firstName.ilike(f"%{text}%"),
            Staff.lastName.ilike(f"%{text}%"),
            Staff.mobile.ilike(f"%{text}%")
        )
             )
    ).all()

    # Format Patient Results
    patients = []
    for p in patient_results:
        # first, *last = p.name.split(" ", 1)
        patients.append({
            "firstName": p.firstName,
            "lastName": p.lastName,  # last[0] if last else "",
            "id": p.patient_id,  # str(
            "mobile": p.mobile,
            "type": "patient"
        })

    # Format Staff Results
    staff = []
    for s in staff_results:
        # first, *last = s.name.split(" ", 1)
        staff.append({
            "firstName": s.firstName,
            "lastName": s.lastName,  # [0] if last else "",
            "id": s.id,
            "mobile": s.mobile,
            "type": "staff"
        })

    merge_results = patients + staff

    return APIResponse(
        status_code=200,
        success=True,
        message=f"Successfully fetched the combined details of patient and staff.",
        data=merge_results
    ).model_dump()
