from __future__ import annotations

import json
from typing import Any

from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.models.agent_conversation import AgentConversation
from app.models.agent_message import AgentMessage
from app.models.chat_message import ChatMessage
from app.models.policy_document import DocStatus, PolicyDocument
from app.models.user import User
from app.services import history_service, search_service
from app.services.agent_tool_services.base import (
    compact_text,
    ok_item_payload,
    ok_list_payload,
    table_display,
)


def _parse_chat_analysis(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _message_search_item(message: ChatMessage) -> dict[str, Any]:
    analysis = _parse_chat_analysis(message.chat_analysis)
    return {
        "id": message.id,
        "created_time": message.created_time.isoformat() if message.created_time else None,
        "original_text": compact_text(message.original_text, limit=180),
        "handling_matter": compact_text(message.handling_matter, limit=120),
        "required_materials": compact_text(message.required_materials, limit=140),
        "risk_warnings": compact_text(message.risk_warnings, limit=140),
        "target_audience": message.target_audience,
        "notice_type": analysis.get("notice_type"),
        "parse_mode": analysis.get("parse_mode"),
        "file_url": message.file_url,
    }


def _policy_item(doc: PolicyDocument, uploader_name: str | None) -> dict[str, Any]:
    return {
        "id": doc.id,
        "title": doc.title,
        "category": doc.category,
        "tags": doc.tags,
        "status": doc.status.value if hasattr(doc.status, "value") else str(doc.status),
        "uploader_name": uploader_name,
        "view_count": doc.view_count,
        "like_count": doc.like_count,
        "created_time": doc.created_time.isoformat() if doc.created_time else None,
        "content_preview": compact_text(doc.content, limit=220),
    }


def unified_search_payload(
    session: Session,
    user_id: int,
    *,
    query: str,
    limit: int = 12,
    types: str = "",
) -> dict[str, Any]:
    user = session.get(User, user_id)
    selected_types = search_service.normalize_source_types(types)
    items = search_service.unified_search(
        session,
        current_user=user,
        query=query,
        limit=max(1, min(limit, 30)),
        types=selected_types,
    )
    display = []
    if items:
        display.append(
            table_display(
                title="统一搜索结果",
                columns=[
                    {"key": "source_type", "label": "来源"},
                    {"key": "title", "label": "标题"},
                    {"key": "subtitle", "label": "副标题"},
                    {"key": "score", "label": "分数"},
                ],
                rows=items[:12],
            )
        )
    return ok_list_payload(
        items,
        query=query,
        total=len(items),
        source_total=len(search_service.collect_candidates(session, user, selected_types)),
        applied_filters={"types": selected_types},
        suggested_tools=["search_chat_messages_fulltext", "search_policy_documents_by_query"],
        display=display,
    )


def search_chat_messages_fulltext_payload(
    session: Session,
    user_id: int,
    *,
    query: str,
    skip: int = 0,
    limit: int = 20,
    handling_only: bool = False,
) -> dict[str, Any]:
    base_stmt = select(ChatMessage).where(
        ChatMessage.user_id == user_id,
        ChatMessage.is_deleted == False,
    )
    total_source = session.exec(
        select(func.count(ChatMessage.id)).where(
            ChatMessage.user_id == user_id,
            ChatMessage.is_deleted == False,
        )
    ).one()

    if query:
        base_stmt = base_stmt.where(
            or_(
                ChatMessage.original_text.contains(query),
                ChatMessage.target_audience.contains(query),
                ChatMessage.handling_matter.contains(query),
                ChatMessage.time_deadline.contains(query),
                ChatMessage.location_entrance.contains(query),
                ChatMessage.required_materials.contains(query),
                ChatMessage.handling_process.contains(query),
                ChatMessage.precautions.contains(query),
                ChatMessage.risk_warnings.contains(query),
                ChatMessage.original_text_mapping.contains(query),
                ChatMessage.chat_analysis.contains(query),
            )
        )
    candidates = list(session.exec(base_stmt.order_by(ChatMessage.created_time.desc())).all())
    if handling_only:
        candidates = [item for item in candidates if (item.handling_matter or "").strip()]

    items = [_message_search_item(item) for item in candidates[skip : skip + max(1, min(limit, 50))]]
    display = []
    if items:
        display.append(
            table_display(
                title="历史解析命中",
                columns=[
                    {"key": "id", "label": "ID"},
                    {"key": "handling_matter", "label": "办理事项"},
                    {"key": "target_audience", "label": "对象"},
                    {"key": "created_time", "label": "时间"},
                ],
                rows=items[:12],
            )
        )
    return ok_list_payload(
        items,
        query=query,
        total=len(candidates),
        source_total=int(total_source or 0),
        applied_filters={"handling_only": handling_only, "skip": max(skip, 0), "limit": max(1, min(limit, 50))},
        suggested_tools=["get_chat_message_detail", "get_message_knowledge_graph", "unified_search_tool"],
        display=display,
    )


def search_policy_documents_payload(
    session: Session,
    user_id: int,
    *,
    query: str = "",
    category: str = "",
    skip: int = 0,
    limit: int = 20,
    approved_only: bool = True,
) -> dict[str, Any]:
    user = session.get(User, user_id)
    total_source_stmt = select(func.count(PolicyDocument.id))
    if approved_only:
        total_source_stmt = total_source_stmt.where(PolicyDocument.status == DocStatus.approved)
    total_source = session.exec(total_source_stmt).one()

    stmt = select(PolicyDocument)
    if approved_only:
        stmt = stmt.where(PolicyDocument.status == DocStatus.approved)
    elif not user or getattr(user.role, "value", "normal") != "admin":
        stmt = stmt.where(
            or_(
                PolicyDocument.status == DocStatus.approved,
                PolicyDocument.uploader_id == user_id,
            )
        )

    if category:
        stmt = stmt.where(PolicyDocument.category == category)
    if query:
        stmt = stmt.where(
            or_(
                PolicyDocument.title.contains(query),
                PolicyDocument.category.contains(query),
                PolicyDocument.tags.contains(query),
                PolicyDocument.content.contains(query),
            )
        )
    docs = list(
        session.exec(
            stmt.order_by(PolicyDocument.created_time.desc())
            .offset(max(skip, 0))
            .limit(max(1, min(limit, 50)))
        ).all()
    )
    items = []
    for doc in docs:
        uploader = session.get(User, doc.uploader_id)
        items.append(_policy_item(doc, uploader.uname if uploader else None))

    display = []
    if items:
        display.append(
            table_display(
                title="政策文档命中",
                columns=[
                    {"key": "id", "label": "ID"},
                    {"key": "title", "label": "标题"},
                    {"key": "category", "label": "分类"},
                    {"key": "status", "label": "状态"},
                ],
                rows=items[:12],
            )
        )

    return ok_list_payload(
        items,
        query=query,
        total=len(items),
        source_total=int(total_source or 0),
        applied_filters={
            "category": category or None,
            "approved_only": approved_only,
            "skip": max(skip, 0),
            "limit": max(1, min(limit, 50)),
        },
        suggested_tools=["unified_search_tool", "recommend_policy_documents"],
        display=display,
    )


def history_feed_payload(
    session: Session,
    user_id: int,
    *,
    domain: str = "all",
    query: str = "",
    skip: int = 0,
    limit: int = 20,
) -> dict[str, Any]:
    events = history_service.list_events(
        session,
        user_id=user_id,
        domain=domain,
        q=query,
        skip=skip,
        limit=limit,
    )
    items = [history_service.serialize_event(item) for item in events]
    return ok_list_payload(
        items,
        query=query,
        total=len(items),
        source_total=None,
        applied_filters={"domain": domain, "skip": skip, "limit": limit},
        suggested_tools=["unified_search_tool"],
    )


def agent_conversation_messages_payload(
    session: Session,
    user_id: int,
    *,
    conversation_id: int,
) -> dict[str, Any]:
    conversation = session.get(AgentConversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        return ok_item_payload(
            {
                "conversation_id": conversation_id,
                "messages": [],
                "empty_reason": "permission_denied",
            }
        )

    messages = list(
        session.exec(
            select(AgentMessage).where(AgentMessage.conversation_id == conversation_id).order_by(AgentMessage.created_time)
        ).all()
    )
    items = [
        {
            "id": item.id,
            "role": item.role,
            "content": compact_text(item.content, limit=360),
            "created_time": item.created_time.isoformat() if item.created_time else None,
        }
        for item in messages
    ]
    return ok_list_payload(
        items,
        total=len(items),
        source_total=len(items),
        applied_filters={"conversation_id": conversation_id},
    )
