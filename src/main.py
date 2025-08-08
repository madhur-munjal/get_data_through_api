import os
import sys
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.join(os.getcwd(), ".."))
from src.routers import api_router
from src.database import engine, Base
from src.core.exception_handlers import custom_validation_handler
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="api_to_get_data",
              description="",
              version="0.0.1",
              contact={
                  "name": "Madhur Munjal",
                  # "url": "",
                  # "email": ""
              },
              root_path="/src")
app.include_router(api_router.router)


@app.on_event("startup")
def on_startup():
    """
    Startup event handler to create database tables.
    """
    # Create all tables in the database
    Base.metadata.drop_all(engine)  # Don't use this in production, it will drop all tables, use alembic
    Base.metadata.create_all(bind=engine)
    print(Base.metadata.tables.keys())
    print("Database tables created successfully.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # ["*"],  # Or ["GET", "POST", "OPTIONS"]
    allow_headers=["*"],  # Or ["Authorization", "Content-Type"]
)

app.add_exception_handler(RequestValidationError, custom_validation_handler)

@app.get("/")
async def status():
    """

    :return:
    """
    return {"status": "online"}


