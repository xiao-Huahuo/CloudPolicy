from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.models.policy_document import PolicyDocumentBase, DocStatus


class PolicyDocumentCreate(PolicyDocumentBase):
    pass


class PolicyDocumentUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None


class PolicyDocumentOut(PolicyDocumentBase):
    id: int
    uploader_id: int
    uploader_name: Optional[str] = None
    status: DocStatus
    view_count: int
    like_count: int
    created_time: datetime
    reviewed_time: Optional[datetime] = None
    reject_reason: Optional[str] = None


class PolicyDocumentReview(SQLModel):
    status: DocStatus  # approved 或 rejected
    reject_reason: Optional[str] = None
