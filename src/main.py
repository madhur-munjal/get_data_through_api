import os
import sys

import redis
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.append(os.path.join(os.getcwd(), ".."))
from src.routers import api_router
from src.database import engine, Base
from src.core.exception_handlers import (
    custom_validation_handler,
    custom_http_exception_handler,
)
from src.models.response import APIResponse
from src.models.response import TokenRevoked
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
    redoc_url="/redoc-ui",
)
app.include_router(api_router.router)


@app.on_event("startup")
def on_startup():
    """
    Startup event handler to create database tables.
    """
    app.state.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    # Create all tables in the database
    # Base.metadata.drop_all(engine)  # Don't use this in production, it will drop all tables, use alembic
    Base.metadata.create_all(bind=engine)
    print(Base.metadata.tables.keys())
    print("Database tables created successfully.")


@app.on_event("startup")
def check_redis():
    r = redis.Redis(host="localhost", port=6379)
    try:
        r.ping()
        print("✅ Redis is up!")
    except redis.exceptions.ConnectionError:
        print("❌ Redis is not reachable.")


origins = [
    "http://localhost:4200",
    "http://api.smarthealapp.com",
]  # "https://www.smarthealapp.com/auth/login", "https://smarthealapp.com/auth/login", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or specify your frontend URL
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],  # ["*"],  # Or ["GET", "POST", "OPTIONS"]
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


# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.environ.get("PORT", 8000))
#     uvicorn.run("main:app", host="0.0.0.0", port=port)
