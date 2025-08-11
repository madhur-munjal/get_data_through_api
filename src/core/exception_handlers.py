from typing import List

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.models.response import APIResponse


def sanitize_errors(errors: List[dict]) -> List[dict]:
    for err in errors:
        if "ctx" in err:
            err["ctx"] = {k: str(v) for k, v in err["ctx"].items()}
            errors = [{"error": err.get("ctx", None)}]
            return errors
    return errors


async def custom_validation_handler(request: Request, exc: RequestValidationError):
    sanitized = sanitize_errors(exc.errors())
    return JSONResponse(
        status_code=422,
        content=APIResponse(status_code=422, status="error", message="Validation failed",
                            data=sanitized).dict()
    )
