from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ColEnum(str, Enum):
    todo = "todo"
    inprogress = "inprogress"
    done = "done"

class PriorityEnum(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    col: ColEnum = ColEnum.todo
    priority: PriorityEnum = PriorityEnum.medium
    tag: Optional[str] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    due_day: Optional[datetime] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    col: Optional[ColEnum] = None
    priority: Optional[PriorityEnum] = None
    tag: Optional[str] = None
    due_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    due_day: Optional[datetime] = None

class Todo(TodoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
