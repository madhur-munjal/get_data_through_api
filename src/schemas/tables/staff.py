import uuid

from sqlalchemy import (
    Column,
    Text,
    String,
    ForeignKey,
    CheckConstraint,
)

from src.database import Base


class Staff(Base):
    __tablename__ = "staff"

    __table_args__ = (
        CheckConstraint(
            "length(firstName) >= 3", name="check_first_name_min_length_staff"
        ),
        CheckConstraint(
            "length(lastName) >= 3", name="check_last_name_min_length_staff"
        ),
    )

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    firstName = Column(String(15), nullable=False)
    lastName = Column(String(15), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    country = Column(String(255), nullable=False)
    mobile = Column(Text, nullable=False)
    username = Column(String(255), nullable=False, unique=True)  # index=True)
    password = Column(Text, nullable=False)
    doc_id = Column(String(36), ForeignKey("users.id"), nullable=False)
