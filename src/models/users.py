from sqlalchemy import Column, Integer, Text, String, ForeignKey, DateTime
from src.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

# from sqlalchemy.ext.declarative import declarative_base
#
# Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)  # index=True)
    password = Column(Text, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    contact_number = Column(Text, nullable=True)

class PasswordResetToken(Base):
    __tablename__ = "reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String(255), unique=True, default=lambda :str(uuid.uuid64()))
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=30))
    user = relationship("User")

