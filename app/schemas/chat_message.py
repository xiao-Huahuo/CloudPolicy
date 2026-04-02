from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field
from sqlmodel import SQLModel


class ChatMessageCreate(SQLModel):
    original_text: str
    file_url: Optional[str] = None


class KGNode(SQLModel):
    id: str
    label: str
    type: str = "实体"
    importance: float = Field(default=0.5, ge=0, le=1)
    layer: Optional[str] = None
    group: Optional[str] = None
    parent_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class KGLink(SQLModel):
    source: str
    target: str
    relation: str = "关联"
    logic_type: str = "positive"
    strength: float = Field(default=0.5, ge=0, le=1)
    evidence: Optional[str] = None


class VisualConfig(SQLModel):
    focus_node: Optional[str] = None
    initial_zoom: float = 1.0
    text_mapping: Dict[str, List[int]] = Field(default_factory=dict)


class ChatMessageRead(SQLModel):
    id: int
    created_time: datetime
    original_text: str
    file_url: Optional[str] = None
    content: str = ""
    nodes: List[KGNode] = Field(default_factory=list)
    links: List[KGLink] = Field(default_factory=list)
    dynamic_payload: Dict[str, Any] = Field(default_factory=dict)
    visual_config: Optional[VisualConfig] = None
    target_audience: Optional[str] = None
    handling_matter: Optional[str] = None
    time_deadline: Optional[str] = None
    location_entrance: Optional[str] = None
    required_materials: Optional[str] = None
    handling_process: Optional[str] = None
    precautions: Optional[str] = None
    risk_warnings: Optional[str] = None
    original_text_mapping: Optional[str] = None
    chat_analysis: Dict[str, Any] = Field(default_factory=dict)
    user_id: int
    source_chat_id: Optional[int] = None
    session_json_path: Optional[str] = None
    estimated_time_saved_minutes: int = 0


class ChatMessageUpdate(SQLModel):
    target_audience: str
