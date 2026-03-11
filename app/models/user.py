from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

#通用模型,无需存入数据库
class UserBase(SQLModel):
    uname:str=Field(index=True) #用户名
    email:str=Field(unique=True,index=True)  #邮箱,不可重复,建立索引便于查找
    # 修改：手机号不再唯一，且可选
    phone:Optional[str]=Field(default=None)

#数据库模型
class User(UserBase,table=True):
    uid: Optional[int] = Field(default=None, primary_key=True)  #uid作为自增主键
    hashed_pwd:str #哈希加密后的密码
    created_time:datetime=Field(default_factory=datetime.now)  #账户创建时间
    last_login:datetime=Field(default_factory=datetime.now)  #最后登录时间
