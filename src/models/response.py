from typing import Generic, TypeVar, Union, Optional, Any, List

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    model_config = {"exclude_none": True}

    def __init__(self, **data):
        filtered = {k: v for k, v in data.items() if v is not None}
        super().__init__(**filtered)

    def model_dump(self, *args, **kwargs):
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(*args, **kwargs)


class APIResponse(BaseResponse[T]):
    status_code: int
    success: bool
    message: str
    data: Optional[Union[T, str]] = None  # Field(default=None, exclude_none=True)
    errors: Any = Field(default=None, exclude=True)
    # errors: Optional[List[Any]] = None  # Field(default=None, exclude=True)

    @classmethod
    def error(cls, message: str, code: int = 400):
        return cls(
            status_code=code, success=False, message=message, data=None, errors=None
        )


class TokenRevoked(Exception):
    def __init__(self, message: str = "Token revoked", code: int = 401):
        self.response = APIResponse.error(message, code)
