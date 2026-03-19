from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User

class Favorite(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.uid", index=True)
    chat_message_id: int = Field(foreign_key="chatmessage.id", index=True)
    note: Optional[str] = Field(default=None, description="用户备注")
    created_time: datetime = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship(back_populates="favorites")
