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
            message=f"Validation failed for {len(simplified_errors)} field(s).",
            errors=simplified_errors,
        ).model_dump(),
    )


async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    response = APIResponse(
        status_code=exc.status_code, success=False, message=exc.detail
    )
    return JSONResponse(status_code=exc.status_code, content=response.dict())
