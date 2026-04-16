from pydantic import BaseModel
from typing import Optional
class NotificationBase(BaseModel):
    title: str
    message: str
    is_read: bool = False

class NotificationCreate(NotificationBase):
    pass
