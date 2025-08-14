from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    tg_name: str | None = None
    role: str
    high_school: str | None = None
    year: int | None = None

class UserCreate(UserBase):
    tg_user_id: int

class UserResponse(UserBase):
    tg_user_id: int
    id: int
    class Config:
        from_attributes = True

class User(UserBase):
    class Config:
        from_attributes = True