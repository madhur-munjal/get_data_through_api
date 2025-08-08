from typing import Generic, TypeVar, Type
from typing import Union, Optional
from pydantic.generics import GenericModel

T = TypeVar("T")


class APIResponse(GenericModel, Generic[T]):
    status_code: int
    status: str
    message: str
    data: Optional[Union[T, str]] = None
