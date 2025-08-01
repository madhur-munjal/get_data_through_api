# from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
# from pydantic import BaseModel, Field
# import sys
# import os
#
# from datetime import datetime
# sys.path.append(os.path.join(os.getcwd(), ".."))
# from sqlalchemy import text
# from sqlalchemy.orm import Session
# from src.database import get_db, engine
# from src.models.patients import Patient
# from src.models.visits import Visits
#
# router = APIRouter(prefix="/medical", tags=["medical", "doctor"], responses={404: {"error": "Not found"}}, )
#
#
# class MedicalBase(BaseModel):
#     """request payload to add/update medical data into database"""
#     patient_id: int = Field(..., description="Unique identifier for the patient", example=1)
#     medical_history: str = Field(None, description="Medical history of the patient",
#                                             example={"allergies": "None", "conditions": "Diabetes"})
#     medications: str = Field(..., description="Current medications of the patient",
#                                         example={"insulin": "10 units daily"})
#     allergies: str = Field(None, description="Allergies of the patient", example="Peanuts")
#     last_checkup_date: str = Field(None, description="Date of the last checkup", example="2023-10-01T12:00:00Z")
#     followup_date: str = Field(None, description="Date of the next checkup", example="2023-10-01T12:00:00Z")
#     notes: str = Field(None, description="Additional notes about the patient",
#                                  example="Patient is responding well to treatment")
#     created_at: datetime = Field(default_factory=datetime.utcnow,
#                                  description="Timestamp when the record was created")
#     updated_at: datetime = Field(default_factory=datetime.utcnow,
#                                  description="Timestamp when the record was last updated")
#     image_data: str = Field(None, description="Base64 encoded image data of the patient",
#                                       example="iVBORw0KGgoAAAANSUhEUgAAAAUA...")
#     image_url: str = Field(None, description="URL of the image of the patient",
#                                      example="https://example.com/image.jpg")
#
#
# @router.get("/", status_code=status.HTTP_200_OK)  # , dependencies=[Depends(authenticate_application)]
# async def read_data(db: Session = Depends(get_db)):
#     # item = db.query(Item).filter(Item.id == item_id).first()
#     # return item
#     # return {"name": "dummy_data"}
#     device = db.query(Visits).all()
#     return device
#
#
# # @router.put("/items/{item_id}", status_code=status.HTTP_200_OK)  # , dependencies=[Depends(authenticate_application)]
# # async def read_data(item_id: int, item: Medical):
# #     return {"item_id": item_id, "item": item.field_1}
#
#
# @router.get("/get_db")
# def read_root():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT DATABASE();"))
#         db_name = result.scalar()  # Or result.fetchone()[0]
#         return {"database": db_name}
#
#         # return {"database": result.fetchone()}
