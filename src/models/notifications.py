from pydantic import BaseModel

from .enums import BillingTypeEnum
from typing import Optional, Literal, List


class NotificationUpdateRequest(BaseModel):
    mark_all_as_read: bool
    id: Optional[List[int]] = []

    model_config = {"from_attributes": True}