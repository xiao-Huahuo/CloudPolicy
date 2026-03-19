from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.models.user import UserBase

class UserCreate(UserBase):
    pwd: str

class UserRead(UserBase):
    uid: int
    created_time: datetime
    last_login: datetime
    is_admin: bool = False

class UserUpdate(SQLModel):
    uname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    pwd: Optional[str] = None
    avatar_url: Optional[str] = None
