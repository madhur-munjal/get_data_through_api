from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Visits(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
