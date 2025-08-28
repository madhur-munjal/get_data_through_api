import uuid

from sqlalchemy import (
    Column,
    Text,
    String,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from src.database import Base


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "length(firstName) >= 3", name="check_first_name_min_length_v2"
        ),
        CheckConstraint("length(lastName) >= 3", name="check_last_name_min_length_v2"),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firstName = Column(String(15), nullable=False)
    lastName = Column(String(15), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    country = Column(String(255), nullable=False)
    mobile = Column(Text, nullable=False)
    username = Column(String(255), nullable=False, unique=True)  # index=True)
    password = Column(Text, nullable=False)
    role = Column(String(50), nullable=False, default="admin")  # e.g., 'owner'(Madhur & Akash), 'admin'('doctor'), 'nurse'
    visits = relationship("Visit", back_populates="user")
    appointments = relationship("Appointment", back_populates="user")


# class PasswordResetToken(Base):
#     __tablename__ = "reset_tokens"
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     token = Column(String(255), unique=True, default=lambda: str(uuid.uuid64()))
#     expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=30))
#     user = relationship("User")
