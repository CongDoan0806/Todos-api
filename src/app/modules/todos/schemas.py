from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    due_day: Optional[datetime] = None

class TodoCreate(TodoBase):
    pass

# class TodoUpdate(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     is_completed: Optional[bool] = None
#     due_date: Optional[datetime] = None
#     start_date: Optional[datetime] = None
#     due_day: Optional[datetime] = None

class TodoUpdate(TodoBase):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    due_day: Optional[datetime] = None

class Todo(TodoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
