import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlmodel import Session
from app.core.database import get_session
from app.models.user import User
from app.models.chat_message import ChatMessage
from app.schemas.chat_message import ChatMessageCreate, ChatMessageRead, ChatMessageUpdate
from app.api.deps import get_current_user
from app.ai.document_parser import parse_document
from app.services import chat_message_service

router = APIRouter()

@router.post("", response_model=ChatMessageRead)
def create_chat_message(
    chat_in: ChatMessageCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    新增解析记录：接收原文，调用 AI 解析，保存到数据库并返回
    """
    parsed_base = parse_document(chat_in.original_text, current_user.uid)
    
    # 根据解析出的内容进行通知难度评级
    analysis_json_str = chat_message_service.evaluate_notice_difficulty(
        original_text=parsed_base.original_text,
        handling_matter=parsed_base.handling_matter,
        time_deadline=parsed_base.time_deadline,
        required_materials=parsed_base.required_materials,
        risk_warnings=parsed_base.risk_warnings
    )
    parsed_base.chat_analysis = analysis_json_str
    
    db_message = ChatMessage.model_validate(parsed_base)
    session.add(db_message)
    session.commit()
    session.refresh(db_message)
    
    # 将 JSON 字符串转换回字典返回给前端
    response_data = db_message.model_dump()
    response_data["chat_analysis"] = json.loads(db_message.chat_analysis)
    
    return ChatMessageRead(**response_data)

@router.get("", response_model=List[ChatMessageRead])
def read_chat_messages(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    id: Optional[int] = None,
    original_text: Optional[str] = None,
    target_audience: Optional[str] = None,
    handling_matter: Optional[str] = None,
    time_deadline: Optional[str] = None,
    location_entrance: Optional[str] = None,
    required_materials: Optional[str] = None,
    handling_process: Optional[str] = None,
    precautions: Optional[str] = None,
    risk_warnings: Optional[str] = None,
    original_text_mapping: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    查询解析记录：支持根据各个字段模糊查询，或按 id 精确查询
    只能查询当前登录用户的数据，且未被标记为删除的。
    """
    messages = chat_message_service.get_messages(
        session=session,
        user_id=current_user.uid,
        id=id,
        original_text=original_text,
        target_audience=target_audience,
        handling_matter=handling_matter,
        time_deadline=time_deadline,
        location_entrance=location_entrance,
        required_materials=required_materials,
        handling_process=handling_process,
        precautions=precautions,
        risk_warnings=risk_warnings,
        original_text_mapping=original_text_mapping,
        skip=skip,
        limit=limit
    )
    
    # 将 JSON 字符串转换回字典返回给前端
    results = []
    for msg in messages:
        msg_data = msg.model_dump()
        msg_data["chat_analysis"] = json.loads(msg.chat_analysis) if msg.chat_analysis else {}
        results.append(ChatMessageRead(**msg_data))
        
    return results

@router.patch("/{message_id}", response_model=ChatMessageRead)
def update_chat_message_audience(
    message_id: int,
    chat_in: ChatMessageUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    修改记录：通过前端指定的 target_audience (如 老人版, 学生版) 重新调用 AI 改写该记录的字段
    """
    updated_message = chat_message_service.update_message_audience_via_ai(
        session, current_user.uid, message_id, chat_in.target_audience
    )
    
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found or you don't have permission")
        
    # 将 JSON 字符串转换回字典返回给前端
    response_data = updated_message.model_dump()
    response_data["chat_analysis"] = json.loads(updated_message.chat_analysis) if updated_message.chat_analysis else {}
    
    return ChatMessageRead(**response_data)

@router.delete("/{message_id}")
def delete_chat_message(
    message_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    删除单条解析记录 (软删除)
    """
    message = chat_message_service.delete_message_by_id(session, current_user.uid, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"message": "Message deleted successfully"}

@router.post("/batch-delete")
def delete_chat_messages(
    message_ids: List[int] = Body(..., embed=True),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    批量删除解析记录 (软删除)
    请求体示例: {"message_ids": [1, 2, 3]}
    """
    count = chat_message_service.delete_messages_by_ids(session, current_user.uid, message_ids)
    return {"message": f"{count} messages deleted successfully"}
