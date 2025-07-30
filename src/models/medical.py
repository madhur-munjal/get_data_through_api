from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Medical(Base):
    __tablename__ = "medical"

    id = Column(Integer, primary_key=True, index=True)