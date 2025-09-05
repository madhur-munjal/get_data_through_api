
from datetime import datetime
from fastapi import FastAPI
from sqlalchemy.orm import Session
from src.schemas.tables.appointments import Appointment  # your SQLAlchemy model
from database import SessionLocal  # your DB session
from src.models.enums import AppointmentStatus  # your enum for statuses

app = FastAPI()


def update_appointment_status():
    db: Session = SessionLocal()
    now = datetime.now()

    appointments = db.query(Appointment).filter(Appointment.status == 0).all()  # 0 = UPCOMING

    for appt in appointments:
        scheduled_dt = datetime.combine(appt.scheduled_date, appt.scheduled_time)
        if now >= scheduled_dt:
            appt.status = AppointmentStatus.NO_SHOW.value  # 2 = NO_SHOW
            db.add(appt)

    db.commit()
    db.close()

