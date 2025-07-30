import os
import sys

from fastapi import FastAPI

sys.path.append(os.path.join(os.getcwd(), ".."))
from src.routers import api_router
from src.database import engine, Base

app = FastAPI(title="api_to_get_data",
              description="",
              version="0.0.1",
              contact={
                  "name": "Madhur Munjal",
                  # "url": "",
                  # "email": ""
              },
              root_path="/src", )

app.include_router(api_router.router)


@app.on_event("startup")
def on_startup():
    """
    Startup event handler to create database tables.
    """
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


@app.get("/")
async def status():
    """

    :return:
    """
    return {"status": "online"}
