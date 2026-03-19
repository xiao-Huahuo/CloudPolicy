from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User

class TodoItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.uid", index=True)
    # 关联来源对话（可选，从对话生成时填入）
    source_chat_id: Optional[int] = Field(default=None, foreign_key="chatmessage.id")
    title: str = Field(description="待办事项标题")
    detail: Optional[str] = Field(default=None, description="详细说明")
    deadline: Optional[str] = Field(default=None, description="截止时间（字符串，来自AI提取）")
    is_done: bool = Field(default=False)
    is_confirmed: bool = Field(default=True, description="用户已确认保存（False=待确认草稿）")
    created_time: datetime = Field(default_factory=datetime.now)
    updated_time: datetime = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship(back_populates="todos")
