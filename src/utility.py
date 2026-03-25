import os
import random
import re
import string
import subprocess
from datetime import date
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo  # Python 3.9+, or use pytz for older versions

import httpx
import pytz
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.constants import (
    total_appointments_basic_plan,
    total_appointments_professional_plan,
    total_staff_basic_plans,
    total_staff_professional_plan,
    mysql_backup_dir,
total_staff_doctor_professional_plan
)
from src.database import SessionLocal
from src.database import hostname, mysql_username, mysql_password, database
from src.models.enums import AppointmentStatus
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.staff import Staff
from src.schemas.tables.subscription import Subscription
from src.schemas.tables.users import User
from src.schemas.tables.patients import Patient

load_dotenv()

# Simulated temporary OTP store (for demo; use Redis or DB in prod)
otp_store = {}
env = Environment(loader=FileSystemLoader("html_templates"))


def generate_otp(length=4):
    return "".join(random.choices(string.digits, k=length))


async def send_otp_email(to_email, otp):
    template = env.get_template("otp_email.html")
    html_content = template.render(otp=otp)
    await send_msg_on_email(
        to_email, html_message=html_content, Subject="SmartHeal App, Password Reset OTP"
    )


async def send_msg_on_email(
    to_email,
    text_message: str = None,
    html_message: str = None,
    Subject="SmartHeal App",
):
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    BREVO_URL = "https://api.brevo.com/v3/smtp/email"
    from_email = os.getenv("SMTP_USER")

    # def send_email(to_email: str, subject: str, text_content: str):
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    payload = {
        "sender": {"name": "SmartHeal App", "email": from_email},
        "to": [{"email": to_email}],
        "subject": Subject,
    }
    if text_message:
        payload["textContent"] = text_message
    if html_message:
        payload["htmlContent"] = html_message

    async with httpx.AsyncClient() as client:
        response = await client.post(BREVO_URL, headers=headers, json=payload)
        return {"status": response.status_code, "message": "Email sent successfully"}


def validate_user_fields(values, cls):
    """
    Validate user fields based on the constraints defined in the User model.
    :param values: Dictionary of field values to validate.
    :param cls: Class type for which validation is being performed.
    :return: Validated values or raises ValueError if validation fails.
    """
    PASSWORD_REGEX = re.compile(r"^.*$")
    USERNAME_REGEX = re.compile("^[a-zA-Z][a-zA-Z0-9._-]{2,19}$")
    EMAIL_REGEX = re.compile(
        "^[a-zA-Z0-9]+[a-zA-Z0-9._%+-]*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
    )  # Indian mobile numbers

    errors: list[InitErrorDetails] = []

    # Email validation
    if "email" in cls.model_fields and not EMAIL_REGEX.fullmatch(
        values.email
    ):  # "email" in values and not values["email"].isalnum() and not EMAIL_REGEX.fullmatch(values.email): #
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError("value_error", "Invalid email format"),
                loc=("email",),
                input=values.email,
            )
        )

    # Username validation
    if "username" in cls.model_fields and not USERNAME_REGEX.fullmatch(
        values.username
    ):  # "username" in values and not values["username"].isalnum() and not USERNAME_REGEX.fullmatch(values.username): #
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError("value_error", "Invalid username format"),
                loc=("username",),
                input=values.username,
            )
        )

    # Password validation
    # password can be NOne in setting page, as user only update mobile
    if (
        "password" in cls.model_fields and values.password is None
    ):  # "password" in values and values.password is None: # :
        return values
    elif "password" in cls.model_fields and not PASSWORD_REGEX.fullmatch(
        values.password
    ):  # "password" in values and not PASSWORD_REGEX.fullmatch(values.password):#"password" in cls.model_fields and not PASSWORD_REGEX.fullmatch(values.password):
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError(
                    "value_error",
                    "Invalid password format, Password must be at least 8 characters long and include uppercase, lowercase, digit, and special character",
                ),
                loc=("password",),
                input=values.password,
            )
        )
    if errors:
        raise ValidationError.from_exception_data(cls, errors)

    return values


def save_data_to_db(data: dict, db_model, db_session):
    """
    Save data to the database.
    :param data: Data to save.
    :param db_model: SQLAlchemy model class.
    :param db_session: SQLAlchemy session.
    :return: Saved database object.
    """
    try:
        db_object = db_model(**data)
        db_session.add(db_object)
        db_session.commit()
        db_session.refresh(db_object)
        return db_object
    except IntegrityError as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(
                e
            ),  # IntegrityError will come for "Duplicate entry or validation error etc.",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


def get_appointment_status(
    appointment_date_time: datetime, comparision_date_time: Optional[datetime] = None
) -> str:
    if comparision_date_time is None:
        comparision_date_time = datetime.now(pytz.timezone("Asia/Kolkata"))
    if (
        appointment_date_time.tzinfo is None
        or appointment_date_time.tzinfo.utcoffset(appointment_date_time) is None
    ):
        # It's naive — localize it
        appointment_date_time = pytz.timezone("Asia/Kolkata").localize(
            appointment_date_time
        )
    if appointment_date_time > comparision_date_time:
        return AppointmentStatus.UPCOMING.value
    else:
        return AppointmentStatus.NO_SHOW.value


def get_appointment_summary(rows_as_query):
    # Group by appointment
    summary = {}
    for appointment, patient, billing in rows_as_query:
        if appointment.id not in summary:
            summary[appointment.id] = {
                "appointment": {
                    c.name: getattr(appointment, c.name)
                    for c in appointment.__table__.columns
                },
                "patient": {
                    c.name: getattr(patient, c.name) for c in patient.__table__.columns
                },
                "billings": [],
                "total_amount": 0,
            }
            summary[appointment.id]["appointment"].pop("_sa_instance_state", None)
            summary[appointment.id]["patient"].pop("_sa_instance_state", None)

        if billing:  # .amount:
            summary[appointment.id]["billings"].append(
                {"type": billing.type, "amount": billing.amount}
            )
            # {"3a65d550-1612-4913-8819-4bb42f916744":{"billings":[{"type":"Cash"}]}}
            summary[appointment.id]["total_amount"] += billing.amount

    return list(summary.values())


def update_appointment_status():
    db: Session = SessionLocal()
    try:
        # Use timezone-aware datetime (adjust timezone as needed)
        now = datetime.now(ZoneInfo("Asia/Kolkata"))  # or your timezone
        # OR if your database stores naive datetime:
        # now = datetime.now()

        appointments = (
            db.query(Appointment)
            .filter(
                Appointment.status == AppointmentStatus.UPCOMING.value  # Use enum value
            )
            .all()
        )

        for appt in appointments:
            # Combine date and time
            scheduled_dt = datetime.combine(appt.scheduled_date, appt.scheduled_time)

            # Make scheduled_dt timezone-aware if needed
            if now.tzinfo is not None and scheduled_dt.tzinfo is None:
                scheduled_dt = scheduled_dt.replace(tzinfo=ZoneInfo("Asia/Kolkata"))

            print(
                f"Appointment {appt.id}: Now={now}, Scheduled={scheduled_dt}, Now >= Scheduled: {now >= scheduled_dt}"
            )

            if now >= scheduled_dt:
                appt.status = AppointmentStatus.NO_SHOW.value
                # No need to db.add() for existing objects being updated

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error updating appointment status: {e}")
    finally:
        db.close()


def update_subscription_data(doctor_id=None):
    db: Session = SessionLocal()
    today = date.today()

    # Step 1: Deactivate expired subscriptions
    if doctor_id:
        expired = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == doctor_id,
                Subscription.end_date < today,
                Subscription.is_active == True,
            )
            .all()
        )
    else:
        expired = (
            db.query(Subscription)
            .filter(Subscription.end_date < today, Subscription.is_active == True)
            .all()
        )
    for sub in expired:
        sub.is_active = False

    # Step 2: For each doc_id, activate only the latest valid subscription
    user_ids = db.query(Subscription.user_id).distinct().all()
    for (user_id,) in user_ids:
        latest = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id, Subscription.end_date >= today)
            .order_by(Subscription.end_date.desc())
            .first()
        )
        if latest:
            latest.is_active = True

        # Deactivate others for this doc_id
        others = (
            db.query(Subscription)
            .filter(
                Subscription.user_id == user_id,
                Subscription.id != latest.id if latest else True,
            )
            .all()
        )
        for sub in others:
            sub.is_active = False

    db.commit()
    db.close()


def get_appointments_left_by_doctor(db: Session, doctor_id) -> int:
    # today = date.today()
    #
    # active_subscription = (
    #     db.query(Subscription)
    #     .filter(
    #         Subscription.user_id == doctor_id,
    #         func.date(Subscription.start_date) <= today,
    #         func.date(Subscription.end_date) >= today,
    #         Subscription.is_active == True,
    #     )
    #     .order_by(Subscription.start_date.desc())
    #     .first()
    # )
    # appointment_left = 0
    # if active_subscription:
    #     used_appointments = (
    #         db.query(Appointment)
    #         .filter(
    #             Appointment.doctor_id == str(doctor_id),
    #             Appointment.created_at.between(
    #                 active_subscription.start_date, active_subscription.end_date
    #             ),
    #         )
    #         .count()
    #     )
    #     if active_subscription.plan.name == "Professional":
    #         appointment_left = total_appointments_professional_plan - used_appointments
    #     elif active_subscription.plan.name == "Basic":
    #         appointment_left = total_appointments_basic_plan - used_appointments
    #     else:
    #         appointment_left = (
    #             active_subscription.appointment_credits - used_appointments
    #         )
    # return appointment_left
    return -1  # as we are not using appointment credit for now, so returning -1 as unlimited appointments


def get_staff_left_count(db: Session, doctor_id) -> bool:
    # plan_name: str, current_staff_count: int

    today = date.today()
    active_subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == doctor_id,
            Subscription.start_date <= today,
            Subscription.end_date >= today,
            Subscription.is_active == True,
        )
        .order_by(Subscription.start_date.desc())
        .first()
    )
    if active_subscription:
        if active_subscription.plan.name == "Professional":
            limit = total_staff_professional_plan
        elif active_subscription.plan.name == "Basic":
            limit = total_staff_basic_plans
        else:
            limit = None
    else:
        limit = 0

    current_staff_count = (
        db.query(Staff).filter_by(doc_id=doctor_id).count()
    )  # Staff count for the doctor
    return limit - current_staff_count


def get_staff_left_doctor_count(db: Session, doctor_id) -> bool:
    # plan_name: str, current_staff_count: int
    today = date.today()
    active_subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == doctor_id,
            Subscription.start_date <= today,
            Subscription.end_date >= today,
            Subscription.is_active == True,
        )
        .order_by(Subscription.start_date.desc())
        .first()
    )
    if active_subscription:
        if active_subscription.plan.name == "Professional":
            limit = total_staff_doctor_professional_plan
        else:
            # return 0
            limit = 0
    else:
        # return 0
        limit = 0

    current_staff_doctor_count = (
        db.query(Staff).filter_by(doc_id=doctor_id, role="doctor").count()
    )  # Staff count for the doctor
    return limit - current_staff_doctor_count

def backup_mysql():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(mysql_backup_dir, f"db_{timestamp}.sql")
    os.makedirs(mysql_backup_dir, exist_ok=True)  # ensures /backups exists

    cmd = [
        "mysqldump",
        "--ssl=0",  # disables SSL
        f"-h{hostname}",
        f"-u{mysql_username}",
        f"-p{mysql_password}",
        database,
    ]

    with open(backup_file, "w") as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Backup failed: {result.stderr.decode()}")
    else:
        print(f"Backup created: {backup_file}")


def generate_patient_code(doctor_id: str, db: Session) -> str:
    """
    Generate a human-friendly patient code unique per doctor.
    Example format: PAT-STR-26-000002
    """
    doctor = db.query(User).filter(User.id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str("Doctor not found")
        )

    # Count existing patients for this doctor
    count = db.query(Patient).filter(Patient.assigned_doctor_id == doctor_id).count()
    # Increment count for new patient
    new_number = count + 1

    # doctor_short = doctor.firstName[:3].upper() if doctor.firstName else "DOC"
    # year = datetime.now().strftime("%y")
    return f"SHA{new_number:06d}"
