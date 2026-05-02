from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel


class TodoRead(SQLModel):
    id: int
    user_id: int
    source_chat_id: Optional[int] = None
    title: str
    detail: Optional[str] = None
    deadline: Optional[str] = None
    is_done: bool = False
    is_confirmed: bool = True
    created_time: datetime
    updated_time: datetime
