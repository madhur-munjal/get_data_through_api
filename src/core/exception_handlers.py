from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.models.response import APIResponse


async def custom_validation_handler(request: Request, exc: RequestValidationError):
    simplified_errors = []

    for err in exc.errors():
        # Extract field name from loc
        field = err["loc"][-1] if len(err["loc"]) > 1 else err["loc"][0]
        simplified_errors.append(
            {"field": field, "msg": err["msg"], "input": err.get("input")}
        )
    return JSONResponse(
        status_code=422,
        content=APIResponse(
            status_code=422,
            success=False,
            message="Validation failed",
            errors=simplified_errors,
        ).model_dump(),
    )


async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        response = APIResponse(
            status_code=404,
            success=False,
            message="The resource you are looking for does not exist."
        )
        return JSONResponse(status_code=404, content=response.dict())
    # For other status codes, fall back to default
    if exc.status_code == 405:
        response = APIResponse(
            status_code=405,
            success=False,
            message=f"The method {request.method} is not supported for this endpoint."
        )
        return JSONResponse(status_code=405, content=response.dict())
    # print(f"request in custom_validation_handler: {request}")
    # print(f"exc.status_code in custom_validation_handler: {exc.status_code}")
    # print(f"message in custom_validation_handler: {exc}")
    # print(f"type of message in custom_validation_handler: {type(exc)}")
    response = APIResponse(
        status_code=exc.status_code,
        success=False,
        message=exc.detail
    )
    return JSONResponse(status_code=exc.status_code, content=response.dict())
