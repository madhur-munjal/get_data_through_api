import os
import random
import re
import smtplib
import string
from datetime import date
from datetime import datetime
from email.mime.text import MIMEText
from typing import Optional
from zoneinfo import ZoneInfo  # Python 3.9+, or use pytz for older versions

import pytz
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.constants import total_appointments_basic_plan, total_appointments_professional_plan, total_staff_basic_plans, \
    total_staff_professional_plan
from src.database import SessionLocal
from src.models.enums import AppointmentStatus
from src.schemas.tables.appointments import Appointment
from src.schemas.tables.staff import Staff
from src.schemas.tables.subscription import Subscription

load_dotenv()

# Simulated temporary OTP store (for demo; use Redis or DB in prod)
otp_store = {}
env = Environment(loader=FileSystemLoader("html_templates"))


def generate_otp(length=4):
    return "".join(random.choices(string.digits, k=length))


def send_otp_email(to_email, otp):
    template = env.get_template("otp_email.html")
    html_content = template.render(otp=otp)
    message = MIMEText(html_content, "html")
    print(message)

    # message = MIMEText(f"Your OTP is: {otp}")
    from_email = os.getenv("from_email_id")  # "support@smarthealapp.com"
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = "Smart-Heal, Password Reset OTP"
    smtp_server = "smtpout.secureserver.net"  # 'mail.firsttoothclinic.com'
    server = smtplib.SMTP_SSL(smtp_server, 465, timeout=30)
    status_code, response = server.ehlo()
    status_code, response = server.login(from_email, os.getenv("email_password"))
    server.sendmail(from_email, to_email, message.as_string())
    server.quit()


def send_msg_on_email(to_email, message, Subject="Smart-Heal"):
    """
    Send a message to the specified email address.
    :param to_email:
    :param message:
    :return:
    """

    message = Mail(
        from_email=os.getenv("from_email_id"),  # must be verified in SendGrid
        to_emails=to_email,
        subject=Subject,
        plain_text_content=message,
    )
    try:
        sg = SendGridAPIClient(os.getenv("SendGridAPI"))
        response = sg.send(message)
        return {"status": response.status_code, "message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# def send_msg_on_email(to_email, message, Subject="Smart-Heal"):
#     """
#     Send a message to the specified email address.
#     :param to_email:
#     :param message:
#     :return:
#     """
#     message = MIMEText(f"{message}")
#     from_email = os.getenv("from_email_id")
#     message["From"] = from_email
#     message["To"] = to_email
#     message["Subject"] = Subject
#     smtp_server = "smtpout.secureserver.net"
#     with smtplib.SMTP(smtp_server, 587, timeout=30) as server:
#         server.starttls()
#         server.login(from_email, os.getenv("email_password"))
#         server.sendmail(from_email, to_email, message.as_string())
#         server.quit()
#
#     # server = smtplib.SMTP_SSL(smtp_server, 465, timeout=30)
#     # status_code, response = server.ehlo()
#     # status_code, response = server.login(from_email, os.getenv("email_password"))
#     # server.sendmail(from_email, to_email, message.as_string())
#     # server.quit()


def validate_user_fields(values, cls):
    """
    Validate user fields based on the constraints defined in the User model.
    :param values: Dictionary of field values to validate.
    :param cls: Class type for which validation is being performed.
    :return: Validated values or raises ValueError if validation fails.
    """
    PASSWORD_REGEX = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
    )
    USERNAME_REGEX = re.compile(
        "^(?=[a-zA-Z])(?=.*[._-])(?!.*[._-]{2})[a-zA-Z][a-zA-Z0-9._-]{1,18}[a-zA-Z0-9]$"
    )
    EMAIL_REGEX = re.compile(
        "^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}$"
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

    # # Group by appointment
    # summary = {}
    # for appointment, patient, pay_type, amount in rows_as_query:
    #     if appointment.id not in summary:
    #         summary[appointment.id] = {
    #             "appointment": {c.name: getattr(appointment, c.name) for c in appointment.__table__.columns},
    #             "patient": {c.name: getattr(patient, c.name) for c in patient.__table__.columns},
    #             "billings": [],
    #             "total_amount": 0
    #         }
    #         summary[appointment.id]["appointment"].pop("_sa_instance_state", None)
    #         summary[appointment.id]["patient"].pop("_sa_instance_state", None)
    #
    #     if amount:
    #         summary[appointment.id]["billings"].append({
    #             "type": pay_type,
    #             "amount": amount
    #         })
    #         summary[appointment.id]["total_amount"] += amount

    return list(summary.values())


# def update_appointment_status():
#     db: Session = SessionLocal()
#     now = datetime.now()
#
#     appointments = db.query(Appointment).filter(Appointment.status == 0).all()  # 0 = UPCOMING
#
#     for appt in appointments:
#         scheduled_dt = datetime.combine(appt.scheduled_date, appt.scheduled_time)
#         if now >= scheduled_dt:
#             appt.status = AppointmentStatus.NO_SHOW.value  # 2 = NO_SHOW
#             db.add(appt)
#
#     db.commit()
#     db.close()


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


# def get_otp_session(token: str):
#     session = redis_client.hgetall(token)
#     return session if session else None
#
#
# def mark_otp_verified(token: str):
#     redis_client.hset(token, "verified", "true")


# def get_subscription_active_status_by_doctor(db: Session, doctor_id):
#     today = date.today()
#     active_subscription = (
#         db.query(Subscription)
#         .filter(
#             Subscription.user_id == doctor_id,
#             Subscription.start_date <= today,
#             Subscription.end_date >= today,
#             Subscription.is_active == True,
#         )
#         .order_by(Subscription.start_date.desc())
#         .first()
#     )
#     if not active_subscription:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Your subscription has expired. Please renew your subscription to access this feature."
#         )
#     return active_subscription is not None


def get_appointments_left_by_doctor(db: Session, doctor_id) -> int:
    today = date.today()

    active_subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == doctor_id,
            func.date(Subscription.start_date) <= today,
            func.date(Subscription.end_date) >= today,
            Subscription.is_active == True,
        )
        .order_by(Subscription.start_date.desc())
        .first()
    )
    appointment_left = 0
    if active_subscription:
        used_appointments = (
            db.query(Appointment)
            .filter(
                Appointment.doctor_id == str(doctor_id),
                Appointment.created_at.between(
                    active_subscription.start_date, active_subscription.end_date
                ),
            )
            .count()
        )
        if active_subscription.plan.name == "Professional":
            appointment_left = total_appointments_professional_plan - used_appointments
        elif active_subscription.plan.name == "Basic":
            appointment_left = total_appointments_basic_plan - used_appointments
        else:
            appointment_left = active_subscription.appointment_credits - used_appointments
    return appointment_left


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

    current_staff_count = db.query(Staff).filter_by(doc_id=doctor_id).count()  # Staff count for the doctor
    return limit - current_staff_count
    # return current_staff_count < limit if limit is not None else True
