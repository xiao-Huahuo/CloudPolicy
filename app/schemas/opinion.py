from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.models.opinion import OpinionType


class OpinionCreate(SQLModel):
    doc_id: int
    opinion_type: OpinionType = OpinionType.review
    content: str
    rating: Optional[int] = None


class OpinionOut(SQLModel):
    id: int
    doc_id: int
    user_id: int
    user_name: Optional[str] = None
    opinion_type: OpinionType
    content: str
    rating: Optional[int] = None
    like_count: int
    created_time: datetime
