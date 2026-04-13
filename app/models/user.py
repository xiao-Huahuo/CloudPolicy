from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.chat_message import ChatMessage
    from app.models.stats_analysis import StatsAnalysis
    from app.models.settings import Settings
    from app.models.favorite import Favorite
    from app.models.todo import TodoItem


class UserRole(str, Enum):
    normal = "normal"        # 普通用户
    certified = "certified"  # 认证主体
    admin = "admin"          # 管理员


class UserBase(SQLModel):
    uname: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    phone: Optional[str] = Field(default=None)
    login_phone: Optional[str] = Field(default=None, index=True)
    avatar_url: Optional[str] = Field(default=None)
    role: UserRole = Field(default=UserRole.normal)
    profession: Optional[str] = Field(default=None)

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.admin

    @property
    def is_certified(self) -> bool:
        return self.role == UserRole.certified


class User(UserBase, table=True):
    uid: Optional[int] = Field(default=None, primary_key=True)
    hashed_pwd: str
    created_time: datetime = Field(default_factory=datetime.now)
    last_login: datetime = Field(default_factory=datetime.now)
    email_verified: bool = Field(default=False)
    phone_verified: bool = Field(default=False)
    password_login_enabled: bool = Field(default=True)
    preferred_login_method: Optional[str] = Field(default=None)
    last_login_method: Optional[str] = Field(default=None)
    email_verification_code: Optional[str] = Field(default=None)
    email_verification_sent_at: Optional[datetime] = Field(default=None)
    last_ip: Optional[str] = Field(default=None)

    chat_messages: List["ChatMessage"] = Relationship(back_populates="user")
    stats_analyses: List["StatsAnalysis"] = Relationship(back_populates="user")
    settings: Optional["Settings"] = Relationship(back_populates="user")
    favorites: List["Favorite"] = Relationship(back_populates="user")
    todos: List["TodoItem"] = Relationship(back_populates="user")
