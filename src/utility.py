import os
import random
import re
import smtplib
import string
from datetime import datetime, timezone
from email.mime.text import MIMEText
from typing import Optional
from sqlalchemy.orm import Session

import pytz
from dotenv import load_dotenv
from fastapi import HTTPException, status
from pydantic import ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError
from sqlalchemy.exc import IntegrityError

from src.models.enums import AppointmentStatus
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import File, UploadFile, Depends
from typing import Optional
from src.schemas.tables.appointments import Appointment
from src.database import SessionLocal

load_dotenv()

# Simulated temporary OTP store (for demo; use Redis or DB in prod)
otp_store = {}


def generate_otp(length=4):
    return "".join(random.choices(string.digits, k=length))


def send_otp_email(to_email, otp):
    message = MIMEText(f"Your OTP is: {otp}")
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
    message = MIMEText(f"{message}")
    from_email = os.getenv("from_email_id")
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = Subject
    smtp_server = "smtpout.secureserver.net"
    server = smtplib.SMTP_SSL(smtp_server, 465, timeout=30)
    status_code, response = server.ehlo()
    status_code, response = server.login(from_email, os.getenv("email_password"))
    server.sendmail(from_email, to_email, message.as_string())
    server.quit()


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
    if "email" in values and not values["email"].isalnum() and not EMAIL_REGEX.fullmatch(values.email): # cls.model_fields and not EMAIL_REGEX.fullmatch(values.email):
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError("value_error", "Invalid email format"),
                loc=("email",),
                input=values.email,
            )
        )

    # Username validation
    if "username" in values and not values["username"].isalnum() and not USERNAME_REGEX.fullmatch(values.username): #"username" in cls.model_fields and not USERNAME_REGEX.fullmatch(values.username):
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError("value_error", "Invalid username format"),
                loc=("username",),
                input=values.username,
            )
        )

    # Password validation
    # password can be NOne in setting page, as user onlu update mobile
    if "password" in values and values.password is None: # not values["password"].isalnum(): #"password" in cls.model_fields and values.password is None:
        return values
    elif "password" in values and not PASSWORD_REGEX.fullmatch(values.password):#"password" in cls.model_fields and not PASSWORD_REGEX.fullmatch(values.password):
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
            detail=str(e)  # IntegrityError will come for "Duplicate entry or validation error etc.",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


def get_appointment_status(appointment_date_time: datetime,
                           comparision_date_time: Optional[datetime] = None) -> str:
    if comparision_date_time is None:
        comparision_date_time = datetime.now(timezone.utc)
    if appointment_date_time.tzinfo is None or appointment_date_time.tzinfo.utcoffset(appointment_date_time) is None:
        # It's naive — localize it
        appointment_date_time = pytz.utc.localize(appointment_date_time)
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
                "appointment": {c.name: getattr(appointment, c.name) for c in appointment.__table__.columns},
                "patient": {c.name: getattr(patient, c.name) for c in patient.__table__.columns},
                "billings": [],
                "total_amount": 0
            }
            summary[appointment.id]["appointment"].pop("_sa_instance_state", None)
            summary[appointment.id]["patient"].pop("_sa_instance_state", None)

        if billing:  # .amount:
            summary[appointment.id]["billings"].append({
                "type": billing.type,
                "amount": billing.amount
            })
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


from datetime import date
from src.schemas.tables.subscription import Subscription


def update_subscription_data(doctor_id=None):
    db: Session = SessionLocal()
    today = date.today()

    # Step 1: Deactivate expired subscriptions
    if doctor_id:
        expired = db.query(Subscription).filter(Subscription.user_id == doctor_id, Subscription.end_date < today,
                                                Subscription.is_active == True).all()
    else:
        expired = db.query(Subscription).filter(Subscription.end_date < today, Subscription.is_active == True).all()
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
            .filter(Subscription.user_id == user_id, Subscription.id != latest.id if latest else True)
            .all()
        )
        for sub in others:
            sub.is_active = False

    db.commit()
    db.close()