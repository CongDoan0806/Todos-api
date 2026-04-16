from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ColEnum(str, enum.Enum):
    todo = "todo"
    inprogress = "inprogress"
    done = "done"

class PriorityEnum(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    is_completed = Column(Boolean, default=False)
    col = Column(Enum(ColEnum), default=ColEnum.todo, nullable=False)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium, nullable=False)
    tag = Column(String(100), nullable=True)
    due_date = Column(DateTime, nullable=True)
    start_date = Column(DateTime, nullable=True)
    due_day = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())