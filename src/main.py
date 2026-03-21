import os
import sys

import redis
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

sys.path.append(os.path.join(os.getcwd(), ".."))
from src.scheduler import start_scheduler, shutdown_scheduler
from src.routers import api_router
from src.database import engine, Base, SessionLocal
from src.schemas.tables.plans import Plan
from src.core.exception_handlers import (
    custom_validation_handler,
    custom_http_exception_handler,
)
from src.models.response import APIResponse
from src.models.response import TokenRevoked
from src.utility import (
    update_appointment_status,
    update_subscription_data,
    backup_mysql,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

load_dotenv()

app = FastAPI(
    title="api_to_get_data",
    description="",
    version="0.0.1",
    contact={
        "name": "Madhur Munjal",
        # "url": "",
        # "email": ""
    },
    # root_path="/src",
    docs_url="/api-docs",
    apenapi_url="/openapi.json",
    redoc_url="/redoc-ui",
)
app.include_router(api_router.router)

app.mount(
    "/images",
    StaticFiles(directory=os.path.join(os.getcwd(), "uploads")),
    name="images",
)


@app.on_event("startup")
def on_startup():
    """
    Startup event handler to create database tables.
    """
    app.state.ACCESS_TOKEN_EXPIRE_MINUTES = 1000
    # Create all tables in the database
    # Base.metadata.drop_all(engine)  # Don't use this in production, it will drop all tables, use alembic
    Base.metadata.create_all(bind=engine)
    print(Base.metadata.tables.keys())
    print("Database tables created successfully.")


@app.on_event("startup")
def startup_event():
    start_scheduler()


@app.on_event("shutdown")
def shutdown_event():
    shutdown_scheduler()


@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    try:
        existing_plan = db.query(Plan).first()
        if existing_plan is None:
            plans = [
                Plan(
                    s_no=1,
                    name="Basic",
                    price=1999,
                    description="""Appointment Management – Schedule, reschedule & cancel appointments with automated reminders. |
                    Patient Records (EMR/EHR) – Digital patient history, prescriptions & visit notes. |
                    Billing & Invoicing – Generate invoices, track payments & dues for patients. |
                    Prescription Builder – Digital prescription generation with drug templates. |
                    Basic Reports – Daily appointment & revenue summaries. |
                    Data Security – Encrypted patient data storage. |
                    Email Support – Response within 48 hours.
                """,
                    duration_months=1,
                ),
                Plan(
                    s_no=2,
                    name="Professional",
                    price=4999,
                    description="""Everything in basic, plus: |
                    Multi-Doctor Management – Separate schedules, queues & records per doctor |
Advanced Analytics & Reports – Revenue trends, doctor-wise performance, patient flow analysis |
Insurance & TPA Billing – Generate insurance claims and track reimbursements |
Lab & Investigation Orders – Order tests, receive reports & attach to patient records |
Staff Task Management – Assign tasks, track follow-ups & internal notes
Priority Support – Dedicated support with response within 24 hours + onboarding assistance""",
                    duration_months=1,
                ),
            ]
            db.add_all(plans)
            db.commit()
    finally:
        db.close()


@app.on_event("startup")
def check_redis():
    r = redis.Redis(host="localhost", port=6379)
    try:
        r.ping()
        print("✅ Redis is up!")
    except redis.exceptions.ConnectionError:
        print("❌ Redis is not reachable.")


origins = [
    "*",
    "http://localhost:4200",
    # "http://api.smarthealapp.com",
]  # "https://www.smarthealapp.com/auth/login", "https://smarthealapp.com/auth/login", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or specify your frontend URL
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
        "PUT",
    ],  # ["*"],  # Or ["GET", "POST", "OPTIONS"]
    allow_headers=["*"],  # Or ["Authorization", "Content-Type"]
)

app.add_exception_handler(RequestValidationError, custom_validation_handler)
app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)


@app.exception_handler(TokenRevoked)
def handle_token_revoked(request: Request, exc: TokenRevoked):
    return JSONResponse(
        status_code=exc.response.status_code, content=exc.response.dict()
    )


@app.get("/")
async def status():
    """

    :return:
    """
    return APIResponse(
        status_code=200, success=True, message="{'status': 'online'}", data=None
    ).model_dump()


@app.post("/run-scheduler", tags=["Scheduler"])
def run_scheduler_manually():
    update_appointment_status()
    update_subscription_data()
    return {"message": "Scheduler task executed successfully"}


@app.post("/run-mysql-scheduler", tags=["Scheduler"])
def run_mysql_scheduler_manually():
    backup_mysql()
    return {"message": "Scheduler task executed successfully"}

# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.environ.get("PORT", 8000))
#     uvicorn.run("main:app", host="0.0.0.0", port=port)
