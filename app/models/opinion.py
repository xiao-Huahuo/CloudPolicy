from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.policy_document import PolicyDocument


class OpinionType(str, Enum):
    review = "review"    # 落地评价
    correction = "correction"  # 智能解析纠错
    message = "message"  # 办事留言


class Opinion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doc_id: int = Field(foreign_key="policydocument.id")
    user_id: int = Field(foreign_key="user.uid")
    opinion_type: OpinionType = Field(default=OpinionType.review)
    content: str
    rating: Optional[int] = Field(default=None)  # 1-5 评分，仅 review 类型
    like_count: int = Field(default=0)
    created_time: datetime = Field(default_factory=datetime.now)

    user: Optional["User"] = Relationship()
    document: Optional["PolicyDocument"] = Relationship()
