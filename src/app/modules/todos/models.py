from sqlalchemy import Column, Integer, String, Boolean, DateTime,ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)

    is_completed = Column(Boolean, default=False)

    due_date = Column(DateTime, nullable=True)        
    start_date = Column(DateTime, nullable=True)  
    due_day = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())