from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel
from app.models.chat_message import ChatMessageBase

# 新增 DTO (前端传入要解析的原文，其他字段由后端 AI 填充)
class ChatMessageCreate(SQLModel):
    original_text: str

# 响应 DTO (返回给前端的结构化数据)
# 我们在这里重新定义字段，将 chat_analysis 由 str 转换为 Dict 以方便前端调用
class ChatMessageRead(SQLModel):
    id: int
    created_time: datetime
    original_text: str
    target_audience: Optional[str] = None
    handling_matter: Optional[str] = None
    time_deadline: Optional[str] = None
    location_entrance: Optional[str] = None
    required_materials: Optional[str] = None
    handling_process: Optional[str] = None
    precautions: Optional[str] = None
    risk_warnings: Optional[str] = None
    original_text_mapping: Optional[str] = None
    chat_analysis: Dict[str, str] = {}
    user_id: int

# 修改 DTO (通过改变 target_audience 来重新调用 AI 并修改当前记录的各种信息)
class ChatMessageUpdate(SQLModel):
    target_audience: str
