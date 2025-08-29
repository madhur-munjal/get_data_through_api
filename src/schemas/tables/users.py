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
    firstName = Column(String(15), nullable=False)  # mandatory
    lastName = Column(String(15), nullable=True)
    email = Column(String(255), unique=True, nullable=False)  # mandatory
    country = Column(String(255), nullable=True)
    mobile = Column(Text, nullable=False)  # mandatory
    username = Column(String(255), nullable=False, unique=True)  # mandatory
    password = Column(Text, nullable=False)  # mandatory
    role = Column(String(50), nullable=False,
                  default="admin")  # mandatory e.g., 'owner'(Madhur & Akash), 'admin'('doctor'), 'nurse'
    visits = relationship("Visit", back_populates="user")
    appointments = relationship("Appointment", back_populates="user")
    staff = relationship("Staff", back_populates="doctor")
