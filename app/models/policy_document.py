from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User


class DocStatus(str, Enum):
    pending = "pending"    # 待审核
    approved = "approved"  # 已通过
    rejected = "rejected"  # 已拒绝


class PolicyDocumentBase(SQLModel):
    title: str
    content: str
    category: Optional[str] = Field(default=None)
    tags: Optional[str] = Field(default=None)  # 逗号分隔


class PolicyDocument(PolicyDocumentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uploader_id: int = Field(foreign_key="user.uid")
    status: DocStatus = Field(default=DocStatus.pending)
    file_path: Optional[str] = Field(default=None)
    view_count: int = Field(default=0)
    like_count: int = Field(default=0)
    created_time: datetime = Field(default_factory=datetime.now)
    reviewed_time: Optional[datetime] = Field(default=None)
    reject_reason: Optional[str] = Field(default=None)

    uploader: Optional["User"] = Relationship()
