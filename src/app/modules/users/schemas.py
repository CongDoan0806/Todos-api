# dtos for users
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    @field_validator("password")
    @classmethod
    def password_length(cls, v):
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password cannot be longer than 72 characters")
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None