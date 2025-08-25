import os
import random
import re
import smtplib
import string
from email.mime.text import MIMEText
from dotenv import load_dotenv
from pydantic import ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError
from sqlalchemy.exc import IntegrityError

from fastapi import HTTPException, status

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
    print(f"Sending OTP {otp} to {to_email}")
    smtp_server = "smtpout.secureserver.net"  # 'mail.firsttoothclinic.com'
    server = smtplib.SMTP_SSL(smtp_server, 465, timeout=30)
    status_code, response = server.ehlo()
    print(f"SMTP server response: {status_code} {response.decode()}")
    status_code, response = server.login(from_email, os.getenv("email_password"))
    print(f"Login response: {status_code} {response.decode()}")
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
    if "email" in cls.model_fields and not EMAIL_REGEX.fullmatch(values.email):
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError("value_error", "Invalid email format"),
                loc=("email",),
                input=values.email,
            )
        )

    # Username validation
    if "username" in cls.model_fields and not USERNAME_REGEX.fullmatch(values.username):
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError("value_error", "Invalid username format"),
                loc=("username",),
                input=values.username,
            )
        )

    # Password validation
    if "password" in cls.model_fields and not PASSWORD_REGEX.fullmatch(values.password):
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


def save_data_to_db(data, db_model, db_session):
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
        print(f"db_object.id before refresh: {db_object.patient_id}")
        db_session.refresh(db_object)
        print(f"db_object.id: {db_object.patient_id}")
        return db_object
    except IntegrityError as e:
        db_session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate entry: user with this phone already exists",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
