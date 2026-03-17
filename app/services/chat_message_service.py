from typing import List, Optional
from sqlmodel import Session, select
from app.models.chat_message import ChatMessage
from app.ai.document_parser import rewrite_document
from app.ai.analysis_agent import analyze_complexity_and_type
import json

def get_messages(
    session: Session,
    user_id: int,
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
) -> List[ChatMessage]:
    """
    从数据库获取解析记录
    """
    statement = select(ChatMessage).where(
        ChatMessage.user_id == user_id,
        ChatMessage.is_deleted == False
    )

    if id is not None:
        statement = statement.where(ChatMessage.id == id)
    else:
        if original_text:
            statement = statement.where(ChatMessage.original_text.contains(original_text))
        if target_audience:
            statement = statement.where(ChatMessage.target_audience.contains(target_audience))
        if handling_matter:
            statement = statement.where(ChatMessage.handling_matter.contains(handling_matter))
        if time_deadline:
            statement = statement.where(ChatMessage.time_deadline.contains(time_deadline))
        if location_entrance:
            statement = statement.where(ChatMessage.location_entrance.contains(location_entrance))
        if required_materials:
            statement = statement.where(ChatMessage.required_materials.contains(required_materials))
        if handling_process:
            statement = statement.where(ChatMessage.handling_process.contains(handling_process))
        if precautions:
            statement = statement.where(ChatMessage.precautions.contains(precautions))
        if risk_warnings:
            statement = statement.where(ChatMessage.risk_warnings.contains(risk_warnings))
        if original_text_mapping:
            statement = statement.where(ChatMessage.original_text_mapping.contains(original_text_mapping))

    statement = statement.offset(skip).limit(limit)
    messages = session.exec(statement).all()
    
    # 因为 chat_analysis 存的是字符串，如果业务需要，可以在这里预处理，但为了性能通常直接返回
    return messages

def delete_message_by_id(session: Session, user_id: int, message_id: int) -> Optional[ChatMessage]:
    """
    通过 ID 软删除单条记录
    """
    message = session.get(ChatMessage, message_id)
    if not message or message.user_id != user_id:
        return None
    
    message.is_deleted = True
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

def delete_messages_by_ids(session: Session, user_id: int, message_ids: List[int]) -> int:
    """
    通过 ID 列表批量软删除记录
    """
    statement = select(ChatMessage).where(
        ChatMessage.user_id == user_id,
        ChatMessage.id.in_(message_ids)
    )
    messages_to_delete = session.exec(statement).all()
    
    if not messages_to_delete:
        return 0
        
    count = 0
    for message in messages_to_delete:
        message.is_deleted = True
        session.add(message)
        count += 1
        
    session.commit()
    return count

def update_message_audience_via_ai(session: Session, user_id: int, message_id: int, new_audience: str) -> Optional[ChatMessage]:
    """
    更新记录的目标受众，并调用 AI 重新改写所有字段
    """
    # 1. 查找现有记录
    message = session.get(ChatMessage, message_id)
    if not message or message.user_id != user_id or message.is_deleted:
        return None
        
    # 2. 调用 AI 重新生成针对新受众的内容
    # 传入原始文本和新的受众目标
    rewritten_base = rewrite_document(message.original_text, new_audience, user_id)
    
    # 3. 将新生成的数据更新到现有的数据库对象中
    # 提取所有不是 None 的字段并更新
    update_data = rewritten_base.model_dump(exclude_unset=True, exclude_none=True)
    
    # 确保 target_audience 是前端请求的那个，即使 AI 没返回
    if "target_audience" not in update_data or not update_data["target_audience"]:
        update_data["target_audience"] = new_audience
        
    message.sqlmodel_update(update_data)
    
    # 4. 保存到数据库
    session.add(message)
    session.commit()
    session.refresh(message)
    
    return message

def evaluate_notice_difficulty(original_text: str, handling_matter: str, time_deadline: str, required_materials: str, risk_warnings: str) -> str:
    """
    业务逻辑：调用大模型和算法结合，评估通知的难度分级和类型。
    依据：调用大模型获取 notice_type 和基础复杂度，并根据内容丰富度计算各个维度的复杂度。
    返回 JSON 格式的字符串。
    """
    # 1. 调用大模型获取通知类型和基础理解复杂度
    ai_analysis = analyze_complexity_and_type(original_text)
    notice_type = ai_analysis.get("notice_type", "其他通知")
    language_complexity = ai_analysis.get("complexity", "中")
        
    # 2. 评估办理复杂度：看所需材料和办理事项的复杂程度
    materials_count = len(str(required_materials).split('、')) + len(str(required_materials).split('，')) if required_materials else 0
    matter_length = len(str(handling_matter)) if handling_matter else 0
    
    if materials_count > 5 or matter_length > 50:
        handling_complexity = "高"
    elif materials_count > 2 or matter_length > 20:
        handling_complexity = "中"
    else:
        handling_complexity = "低"
        
    # 3. 评估风险等级：看风险提示的有无和长短
    risk_length = len(str(risk_warnings)) if risk_warnings and str(risk_warnings) != "无" else 0
    
    if risk_length > 50:
        risk_level = "高"
    elif risk_length > 10:
        risk_level = "中"
    else:
        risk_level = "低"
        
    # 构建分析结果字典并序列化
    analysis_dict = {
        "language_complexity": language_complexity,
        "handling_complexity": handling_complexity,
        "risk_level": risk_level,
        "notice_type": notice_type
    }
    
    return json.dumps(analysis_dict, ensure_ascii=False)
