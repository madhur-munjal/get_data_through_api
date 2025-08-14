from typing import Generic, TypeVar, Union, Optional, Any, List

from pydantic import Field
from pydantic.generics import GenericModel

T = TypeVar("T")


class APIResponse(GenericModel, Generic[T]):
    status_code: int
    status: str
    message: str
    data: Optional[Union[T, str]] = None #Field(default=None, exclude_none=True)
    errors: Optional[List[Any]] = None  # Field(default=None, exclude=True)

    model_config = {"exclude_none": True}
    # def model_dump(self, **kwargs):
    #     kwargs.setdefault("exclude_none", True)
    #     return super().model_dump(**kwargs)
