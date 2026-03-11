# DTOs

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.models.user import UserBase

#注册DTO
class UserCreate(UserBase):
    pwd:str  #明文密码

#响应DTO
class UserRead(UserBase):
    uid:int
    created_time:datetime
    last_login:datetime

#修改DTO
# 不需要继承UserBase
class UserUpdate(SQLModel):
    uname:Optional[str]=None
    email:Optional[str]=None
    phone:Optional[str]=None
    pwd:Optional[str]=None
