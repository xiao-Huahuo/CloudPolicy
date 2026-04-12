from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.models.agent_conversation import AgentConversation
from app.models.chat_message import ChatMessage
from app.models.policy_document import DocStatus, PolicyDocument
from app.models.search_index_item import SearchIndexItem
from app.models.todo import TodoItem
from app.models.user import User
from app.services import search_service
from app.services.agent_tool_services.base import (
    compact_text,
    get_user_role,
    guess_empty_reason,
    ok_item_payload,
    ok_list_payload,
    role_allows,
)
from app.services.agent_tool_services.catalog import TOOL_CATALOG


def _tools_for_role(user_role: str) -> list[dict[str, Any]]:
    return [
        item
        for item in TOOL_CATALOG
        if role_allows(user_role, item.get("min_role", "normal"))
    ]


def get_permission_scope(session: Session, user_id: int) -> dict[str, Any]:
    user = session.get(User, user_id)
    role = get_user_role(session, user_id)
    scopes = {
        "can_use_agent_tools": True,
        "can_manage_workspace": True,
        "can_query_public_policy": True,
        "can_query_public_news": True,
        "can_view_personal_stats": True,
        "can_submit_policy_documents": role in {"certified", "admin"},
        "can_view_my_policy_feedback": role in {"certified", "admin"},
        "can_review_policy_documents": role == "admin",
        "can_view_admin_stats": role == "admin",
        "can_manage_users": role == "admin",
        "can_read_logs": role == "admin",
    }
    return {
        "user_id": user_id,
        "user_name": user.uname if user else None,
        "role": role,
        "scopes": scopes,
        "allowed_tool_categories": sorted({item["category"] for item in _tools_for_role(role)}),
    }


def list_available_tools_payload(session: Session, user_id: int) -> dict[str, Any]:
    scope = get_permission_scope(session, user_id)
    tools = _tools_for_role(scope["role"])
    items = [
        {
            "name": item["name"],
            "category": item["category"],
            "side_effect": bool(item.get("side_effect")),
            "description": item["description"],
        }
        for item in tools
    ]
    return ok_list_payload(
        items,
        total=len(items),
        source_total=len(TOOL_CATALOG),
        applied_filters={"role": scope["role"]},
        meta_extra={"group_count": len(scope["allowed_tool_categories"])},
    )


def inspect_agent_runtime_payload(
    session: Session,
    user_id: int,
    *,
    mode: str = "agent",
    conversation_id: int | None = None,
) -> dict[str, Any]:
    scope = get_permission_scope(session, user_id)
    tool_items = _tools_for_role(scope["role"])
    conversation = session.get(AgentConversation, conversation_id) if conversation_id else None
    item = {
        "user_id": user_id,
        "role": scope["role"],
        "mode": str(mode or "agent"),
        "conversation_id": conversation_id,
        "conversation_exists": bool(conversation),
        "available_tool_count": len(tool_items),
        "available_tool_names": [item["name"] for item in tool_items],
        "allowed_tool_categories": scope["allowed_tool_categories"],
        "scopes": scope["scopes"],
    }
    return ok_item_payload(item, meta={"conversation_title": conversation.title if conversation else None})


def debug_query_zero_results_payload(
    session: Session,
    user_id: int,
    *,
    tool_name: str,
    query: str = "",
    confirmed_only: bool | None = None,
    category: str = "",
    types: str = "",
) -> dict[str, Any]:
    user = session.get(User, user_id)
    if not user:
        return ok_item_payload(
            {
                "tool_name": tool_name,
                "query": query,
                "empty_reason": "permission_denied",
                "next_steps": ["用户不存在或已失效，需重新登录"],
            }
        )

    tool_name = str(tool_name or "").strip()
    lowered_query = str(query or "").strip()
    diagnosis: dict[str, Any] = {
        "tool_name": tool_name,
        "query": lowered_query,
        "empty_reason": "no_match",
        "input_filters": {
            "confirmed_only": confirmed_only,
            "category": category or None,
            "types": types or None,
        },
        "counts": {},
        "next_steps": [],
    }

    if tool_name in {"search_chat_history", "search_chat_messages_fulltext"}:
        base_stmt = select(ChatMessage).where(
            ChatMessage.user_id == user_id,
            ChatMessage.is_deleted == False,
        )
        total_messages = session.exec(
            select(func.count(ChatMessage.id)).where(
                ChatMessage.user_id == user_id,
                ChatMessage.is_deleted == False,
            )
        ).one()
        diagnosis["counts"]["source_total"] = total_messages
        hits = list(
            session.exec(
                base_stmt.where(
                    or_(
                        ChatMessage.original_text.contains(lowered_query),
                        ChatMessage.handling_matter.contains(lowered_query),
                        ChatMessage.required_materials.contains(lowered_query),
                        ChatMessage.handling_process.contains(lowered_query),
                        ChatMessage.precautions.contains(lowered_query),
                        ChatMessage.risk_warnings.contains(lowered_query),
                        ChatMessage.original_text_mapping.contains(lowered_query),
                        ChatMessage.chat_analysis.contains(lowered_query),
                    )
                )
            ).all()
        ) if lowered_query else list(session.exec(base_stmt).all())
        diagnosis["counts"]["matched_candidates"] = len(hits)
        diagnosis["empty_reason"] = guess_empty_reason(
            items_count=len(hits),
            source_total=int(total_messages or 0),
            query=lowered_query,
        )
        diagnosis["next_steps"] = [
            "尝试更短的关键词，或直接搜办理事项/材料/风险词",
            "如果要跨历史、政策、新闻一起搜，改用 unified_search_tool",
        ]
    elif tool_name in {"search_policy_documents", "search_policy_documents_by_query"}:
        total_approved = session.exec(
            select(func.count(PolicyDocument.id)).where(PolicyDocument.status == DocStatus.approved)
        ).one()
        diagnosis["counts"]["source_total"] = total_approved
        stmt = select(PolicyDocument).where(PolicyDocument.status == DocStatus.approved)
        if category:
            stmt = stmt.where(PolicyDocument.category == category)
        if lowered_query:
            stmt = stmt.where(
                or_(
                    PolicyDocument.title.contains(lowered_query),
                    PolicyDocument.category.contains(lowered_query),
                    PolicyDocument.tags.contains(lowered_query),
                    PolicyDocument.content.contains(lowered_query),
                )
            )
        hits = list(session.exec(stmt).all())
        diagnosis["counts"]["matched_candidates"] = len(hits)
        diagnosis["empty_reason"] = guess_empty_reason(
            items_count=len(hits),
            source_total=int(total_approved or 0),
            query=lowered_query,
            filters_applied=bool(category),
        )
        diagnosis["next_steps"] = [
            "政策搜索支持标题、分类、标签和正文片段匹配",
            "如果目标不明确，先用 unified_search_tool 再缩小来源",
        ]
    elif tool_name == "unified_search_tool":
        selected_types = search_service.normalize_source_types(types)
        candidates = search_service.collect_candidates(session, user, selected_types)
        results = search_service.unified_search(
            session,
            user,
            query=lowered_query,
            limit=12,
            types=selected_types,
        ) if lowered_query else []
        diagnosis["counts"]["source_total"] = len(candidates)
        diagnosis["counts"]["matched_candidates"] = len(results)
        diagnosis["empty_reason"] = guess_empty_reason(
            items_count=len(results),
            source_total=len(candidates),
            query=lowered_query,
            filters_applied=bool(selected_types),
        )
        diagnosis["next_steps"] = [
            "检查 types 过滤是否过严",
            "若要搜自己的解析记录，优先用 search_chat_messages_fulltext",
        ]
    elif tool_name == "get_my_todos":
        total_todos = session.exec(
            select(func.count(TodoItem.id)).where(TodoItem.user_id == user_id)
        ).one()
        confirmed_todos = session.exec(
            select(func.count(TodoItem.id)).where(
                TodoItem.user_id == user_id,
                TodoItem.is_confirmed == True,
            )
        ).one()
        diagnosis["counts"]["source_total"] = total_todos
        diagnosis["counts"]["confirmed_total"] = confirmed_todos
        diagnosis["empty_reason"] = guess_empty_reason(
            items_count=int(confirmed_todos if confirmed_only else total_todos),
            source_total=int(total_todos or 0),
            filters_applied=bool(confirmed_only),
        )
        diagnosis["next_steps"] = [
            "如果 confirmed_only=true 导致空结果，可改为 false 查看草稿",
            "也可以先让 Agent 从当前对话提取新的待办草稿",
        ]
    else:
        index_total = session.exec(select(func.count(SearchIndexItem.id))).one()
        diagnosis["counts"]["source_total"] = index_total
        diagnosis["empty_reason"] = "not_implemented"
        diagnosis["next_steps"] = [
            "该工具的专项诊断还未做深度适配",
            "可先检查入参或改用 unified_search_tool 做交叉检索",
        ]

    diagnosis["summary"] = compact_text(
        f"tool={tool_name} query={lowered_query or '空'} empty_reason={diagnosis['empty_reason']}",
        limit=220,
    )
    return ok_item_payload(diagnosis)
