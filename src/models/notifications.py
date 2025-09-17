from pydantic import BaseModel

from typing import Optional, Literal, List


class NotificationUpdateRequest(BaseModel):
    mark_all_as_read: bool
    id: Optional[List[str]] = []

    model_config = {"from_attributes": True}