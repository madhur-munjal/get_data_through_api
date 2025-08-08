from sqlalchemy import Column, Integer, String, Text
# from sqlalchemy.ext.declarative import declarative_base

from src.database import Base
# Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
