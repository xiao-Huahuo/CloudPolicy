import json
from pathlib import Path
from typing import Any

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from sqlmodel import Session, select

from app.agent_plugin.agent.memory import get_long_term_memory
from app.core.database import engine
from app.models.chat_message import ChatMessage
from app.models.favorite import Favorite
from app.models.policy_document import DocStatus, PolicyDocument
from app.models.settings import Settings
from app.models.todo import TodoItem
from app.models.user import User
from app.services import chat_message_service, stats_service
from app.services.agent_tool_services import (
    admin_tool_service,
    diagnostic_tool_service,
    file_tool_service,
    search_tool_service,
    stats_tool_service,
)
from app.services.agent_tool_services.base import (
    ok_item_payload,
    ok_list_payload,
)
from app.services.news_crawler import get_daily_gov_summary, search_news


def _uid(user_id: str) -> int:
    return int(str(user_id))


def _ok(payload: dict[str, Any]) -> str:
    payload.setdefault("ok", True)
    return json.dumps(payload, ensure_ascii=False)


def _err(code: str, message: str) -> str:
    return json.dumps(
        {"ok": False, "error": {"code": code, "message": message}},
        ensure_ascii=False,
    )


def _todo_to_dict(item: TodoItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "title": item.title,
        "detail": item.detail,
        "deadline": item.deadline,
        "is_done": item.is_done,
        "is_confirmed": item.is_confirmed,
        "source_chat_id": item.source_chat_id,
        "created_time": item.created_time.isoformat() if item.created_time else None,
        "updated_time": item.updated_time.isoformat() if item.updated_time else None,
    }


def _doc_to_dict(doc: PolicyDocument, uploader_name: str | None = None) -> dict[str, Any]:
    return {
        "id": doc.id,
        "title": doc.title,
        "category": doc.category,
        "tags": doc.tags,
        "status": str(doc.status),
        "view_count": doc.view_count,
        "like_count": doc.like_count,
        "created_time": doc.created_time.isoformat() if doc.created_time else None,
        "uploader_id": doc.uploader_id,
        "uploader_name": uploader_name,
    }


def _message_to_dict(msg: ChatMessage) -> dict[str, Any]:
    return {
        "id": msg.id,
        "original_text": msg.original_text,
        "file_url": msg.file_url,
        "target_audience": msg.target_audience,
        "handling_matter": msg.handling_matter,
        "time_deadline": msg.time_deadline,
        "required_materials": msg.required_materials,
        "handling_process": msg.handling_process,
        "precautions": msg.precautions,
        "risk_warnings": msg.risk_warnings,
        "created_time": msg.created_time.isoformat() if msg.created_time else None,
    }


def _favorite_to_dict(fav: Favorite) -> dict[str, Any]:
    return {
        "id": fav.id,
        "chat_message_id": fav.chat_message_id,
        "note": fav.note,
        "created_time": fav.created_time.isoformat() if fav.created_time else None,
    }


@tool
def query_long_term_memory(query: str, user_id: str):
    """当需要检索用户长期记忆（偏好、背景、历史事实）时调用。"""
    long_term_memory = get_long_term_memory()
    results = long_term_memory.rag_query_top_k(query=query, user_id=user_id)
    return _ok(
        ok_list_payload(
            results,
            query=query,
            total=len(results),
            source_total=None,
            suggested_tools=["unified_search_tool"],
        )
    )


@tool
def parse_local_file(file_name: str, user_id: str = ""):
    """读取本地文本文件内容（受项目目录约束）并返回前 3000 字符。"""
    candidate = Path(file_name)
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate

    candidate = candidate.resolve()
    root = Path.cwd().resolve()
    if root not in candidate.parents and candidate != root:
        return _err("OUTSIDE_PROJECT", "文件路径不在当前项目目录下，拒绝读取。")

    if not candidate.exists() or not candidate.is_file():
        return _err("FILE_NOT_FOUND", f"未找到文件: {candidate}")

    if candidate.suffix.lower() not in {".txt", ".md", ".json", ".log", ".py", ".yaml", ".yml"}:
        return _err("UNSUPPORTED_FILE_TYPE", f"暂不支持该类型: {candidate.suffix}")

    try:
        content = candidate.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        return _err("FILE_READ_FAILED", f"读取失败: {exc}")

    return _ok(
        {
            "item": {
                "file": str(candidate),
                "content_preview": content[:3000],
            }
        }
    )


@tool
def get_my_todos(user_id: str, confirmed_only: bool = True):
    """查询当前用户待办列表。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            all_items = list(session.exec(select(TodoItem).where(TodoItem.user_id == uid)).all())
            stmt = select(TodoItem).where(TodoItem.user_id == uid)
            if confirmed_only:
                stmt = stmt.where(TodoItem.is_confirmed == True)
            stmt = stmt.order_by(TodoItem.created_time.desc())
            items = list(session.exec(stmt).all())
            return _ok(
                ok_list_payload(
                    [_todo_to_dict(item) for item in items],
                    total=len(items),
                    source_total=len(all_items),
                    applied_filters={"confirmed_only": confirmed_only},
                    suggested_tools=["debug_query_zero_results", "create_todos_from_chat"],
                )
            )
    except Exception as exc:
        return _err("TODO_QUERY_FAILED", str(exc))


@tool
def create_todos_from_chat(
    user_id: str,
    items: list[dict[str, Any]],
    source_chat_id: int | None = None,
    confirm: bool = False,
):
    """批量从聊天内容创建待办。confirm=false 时仅返回草稿，不写库。"""
    if not items:
        return _err("EMPTY_ITEMS", "items 不能为空。")
    try:
        uid = _uid(user_id)
        if not confirm:
            drafts = []
            for item in items[:20]:
                drafts.append(
                    {
                        "title": str(item.get("title", "")).strip(),
                        "detail": item.get("detail"),
                        "deadline": item.get("deadline"),
                        "source_chat_id": source_chat_id,
                        "is_confirmed": False,
                    }
                )
            return _ok({"items": drafts, "pending_confirm": True})

        created: list[dict[str, Any]] = []
        with Session(engine) as session:
            for item in items[:20]:
                title = str(item.get("title", "")).strip()
                if not title:
                    continue
                todo = TodoItem(
                    user_id=uid,
                    title=title,
                    detail=item.get("detail"),
                    deadline=item.get("deadline"),
                    source_chat_id=source_chat_id,
                    is_confirmed=False,
                )
                session.add(todo)
                created.append(todo)
            session.commit()
            for todo in created:
                session.refresh(todo)
            return _ok(
                {
                    "items": [_todo_to_dict(item) for item in created],
                    "pending_confirm": False,
                }
            )
    except Exception as exc:
        return _err("TODO_CREATE_FAILED", str(exc))


@tool
def confirm_todo(user_id: str, todo_id: int, confirm: bool = False):
    """确认单条待办草稿。confirm=false 时仅提示需确认。"""
    if not confirm:
        return _ok({"pending_confirm": True, "todo_id": todo_id})
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            todo = session.get(TodoItem, todo_id)
            if not todo or todo.user_id != uid:
                return _err("TODO_NOT_FOUND", "Todo not found")
            todo.is_confirmed = True
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return _ok({"item": _todo_to_dict(todo), "pending_confirm": False})
    except Exception as exc:
        return _err("TODO_CONFIRM_FAILED", str(exc))


@tool
def search_policy_documents(
    user_id: str,
    query: str = "",
    category: str = "",
    skip: int = 0,
    limit: int = 20,
):
    """检索已审核通过的政策文档。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                search_tool_service.search_policy_documents_payload(
                    session,
                    uid,
                    query=query,
                    category=category,
                    skip=skip,
                    limit=limit,
                    approved_only=True,
                )
            )
    except Exception as exc:
        return _err("POLICY_SEARCH_FAILED", str(exc))


@tool
def recommend_policy_documents(
    user_id: str,
    for_me: bool = True,
    skip: int = 0,
    limit: int = 10,
):
    """推荐政策文档。for_me=true 时尽量按用户职业偏好推荐。"""
    try:
        uid = _uid(user_id)
        limit = max(1, min(limit, 50))
        skip = max(skip, 0)
        with Session(engine) as session:
            base_q = select(PolicyDocument).where(PolicyDocument.status == DocStatus.approved)
            docs: list[PolicyDocument] = []
            if for_me:
                user = session.get(User, uid)
                matched_cat = None
                if user and user.profession:
                    category_map = {
                        "医": "医疗卫生",
                        "教": "教育",
                        "农": "乡村振兴",
                        "企": "惠企政策",
                        "环": "环境保护",
                        "交": "交通建设",
                    }
                    matched_cat = next((v for k, v in category_map.items() if k in user.profession), None)
                if matched_cat:
                    prio = list(
                        session.exec(
                            base_q.where(PolicyDocument.category == matched_cat)
                            .order_by(PolicyDocument.view_count.desc())
                            .limit(max(1, limit // 2))
                        ).all()
                    )
                    rest = list(
                        session.exec(
                            base_q.where(PolicyDocument.category != matched_cat)
                            .order_by(PolicyDocument.view_count.desc())
                            .offset(skip)
                            .limit(limit)
                        ).all()
                    )
                    docs = (prio + rest)[:limit]
            if not docs:
                docs = list(
                    session.exec(
                        base_q.order_by(PolicyDocument.view_count.desc())
                        .offset(skip)
                        .limit(limit)
                    ).all()
                )
            result = []
            for doc in docs:
                uploader = session.get(User, doc.uploader_id)
                result.append(_doc_to_dict(doc, uploader.uname if uploader else None))
            return _ok({"items": result})
    except Exception as exc:
        return _err("POLICY_RECOMMEND_FAILED", str(exc))


@tool
def get_user_settings(user_id: str):
    """获取当前用户设置。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            settings = session.exec(select(Settings).where(Settings.user_id == uid)).first()
            if not settings:
                settings = Settings(user_id=uid)
                session.add(settings)
                session.commit()
                session.refresh(settings)
            return _ok({"item": settings.model_dump()})
    except Exception as exc:
        return _err("SETTINGS_QUERY_FAILED", str(exc))


@tool
def update_user_settings(
    user_id: str,
    default_audience: str = "",
    theme_mode: str = "",
    color_scheme: str = "",
    system_notifications: bool | None = None,
    confirm: bool = False,
):
    """更新当前用户设置。confirm=false 时只返回待确认变更。"""
    patch = {}
    if default_audience:
        patch["default_audience"] = default_audience
    if theme_mode:
        patch["theme_mode"] = theme_mode
    if color_scheme:
        patch["color_scheme"] = color_scheme
    if system_notifications is not None:
        patch["system_notifications"] = bool(system_notifications)

    if not patch:
        return _err("EMPTY_PATCH", "没有可更新字段。")

    if not confirm:
        return _ok({"pending_confirm": True, "patch": patch})

    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            settings = session.exec(select(Settings).where(Settings.user_id == uid)).first()
            if not settings:
                settings = Settings(user_id=uid)
            settings.sqlmodel_update(patch)
            session.add(settings)
            session.commit()
            session.refresh(settings)
            return _ok({"item": settings.model_dump(), "pending_confirm": False})
    except Exception as exc:
        return _err("SETTINGS_UPDATE_FAILED", str(exc))


@tool
def search_chat_history(
    user_id: str,
    query: str = "",
    skip: int = 0,
    limit: int = 20,
    handling_only: bool = False,
):
    """检索当前用户历史解析消息。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                search_tool_service.search_chat_messages_fulltext_payload(
                    session,
                    uid,
                    query=query,
                    skip=skip,
                    limit=limit,
                    handling_only=handling_only,
                )
            )
    except Exception as exc:
        return _err("CHAT_HISTORY_SEARCH_FAILED", str(exc))


@tool
def get_chat_message_detail(user_id: str, message_id: int):
    """获取单条历史解析消息详情。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            message = session.get(ChatMessage, message_id)
            if not message or message.user_id != uid or message.is_deleted:
                return _err("MESSAGE_NOT_FOUND", "Message not found")
            return _ok({"item": _message_to_dict(message)})
    except Exception as exc:
        return _err("CHAT_MESSAGE_DETAIL_FAILED", str(exc))


@tool
def get_news_digest(user_id: str = ""):
    """获取政务热点日报摘要。"""
    try:
        summary = get_daily_gov_summary()
        return _ok({"item": summary})
    except Exception as exc:
        return _err("NEWS_DIGEST_FAILED", str(exc))


@tool
def search_news_tool(query: str, limit: int = 10, user_id: str = ""):
    """按关键词检索新闻。"""
    try:
        limit = max(1, min(limit, 30))
        items = search_news(query, limit=limit)
        return _ok({"items": items, "meta": {"query": query, "limit": limit}})
    except Exception as exc:
        return _err("NEWS_SEARCH_FAILED", str(exc))


@tool
def list_favorites(user_id: str):
    """查询当前用户收藏列表。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            stmt = (
                select(Favorite)
                .where(Favorite.user_id == uid)
                .order_by(Favorite.created_time.desc())
            )
            items = list(session.exec(stmt).all())
            return _ok(
                ok_list_payload(
                    [_favorite_to_dict(item) for item in items],
                    total=len(items),
                    source_total=len(items),
                    suggested_tools=["get_chat_message_detail"],
                )
            )
    except Exception as exc:
        return _err("FAVORITE_LIST_FAILED", str(exc))


@tool
def add_favorite(
    user_id: str,
    chat_message_id: int,
    note: str = "",
    confirm: bool = False,
):
    """收藏解析记录。confirm=false 时仅返回待确认动作。"""
    if not confirm:
        return _ok(
            {
                "pending_confirm": True,
                "chat_message_id": chat_message_id,
                "note": note or None,
            }
        )
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            msg = session.get(ChatMessage, chat_message_id)
            if not msg or msg.user_id != uid or msg.is_deleted:
                return _err("MESSAGE_NOT_FOUND", "Message not found")

            existing = session.exec(
                select(Favorite).where(
                    Favorite.user_id == uid,
                    Favorite.chat_message_id == chat_message_id,
                )
            ).first()
            if existing:
                return _ok({"item": _favorite_to_dict(existing), "pending_confirm": False})

            fav = Favorite(
                user_id=uid,
                chat_message_id=chat_message_id,
                note=(note or None),
            )
            session.add(fav)
            session.commit()
            session.refresh(fav)
            return _ok({"item": _favorite_to_dict(fav), "pending_confirm": False})
    except Exception as exc:
        return _err("FAVORITE_ADD_FAILED", str(exc))


@tool
def get_my_stats(user_id: str):
    """获取当前用户解析统计。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            stats = stats_service.generate_user_stats(session, uid)
            return _ok(ok_item_payload(stats))
    except Exception as exc:
        return _err("STATS_QUERY_FAILED", str(exc))


@tool
def rewrite_for_audience(
    user_id: str,
    message_id: int,
    target_audience: str,
    confirm: bool = False,
):
    """按人群改写历史消息。confirm=false 时仅返回待确认动作。"""
    if not target_audience:
        return _err("EMPTY_TARGET_AUDIENCE", "target_audience 不能为空。")
    if not confirm:
        return _ok(
            {
                "pending_confirm": True,
                "message_id": message_id,
                "target_audience": target_audience,
            }
        )
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            updated = chat_message_service.update_message_audience_via_ai(
                session=session,
                user_id=uid,
                message_id=message_id,
                new_audience=target_audience,
            )
            if not updated:
                return _err("MESSAGE_NOT_FOUND", "Message not found")
            return _ok({"item": _message_to_dict(updated), "pending_confirm": False})
    except Exception as exc:
        return _err("REWRITE_FAILED", str(exc))


@tool
def inspect_agent_runtime(
    user_id: str,
    mode: str = "agent",
    conversation_id: int | None = None,
):
    """检查当前 Agent 运行模式、用户权限范围和可用工具集合。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                diagnostic_tool_service.inspect_agent_runtime_payload(
                    session,
                    uid,
                    mode=mode,
                    conversation_id=conversation_id,
                )
            )
    except Exception as exc:
        return _err("AGENT_RUNTIME_INSPECT_FAILED", str(exc))


@tool
def list_available_tools(user_id: str):
    """列出当前用户在本轮 Agent 运行中可用的工具。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(diagnostic_tool_service.list_available_tools_payload(session, uid))
    except Exception as exc:
        return _err("AVAILABLE_TOOLS_QUERY_FAILED", str(exc))


@tool
def get_user_permission_scope(user_id: str):
    """查看当前用户权限范围，用于判断是否可以使用高级分析或管理员工具。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(ok_item_payload(diagnostic_tool_service.get_permission_scope(session, uid)))
    except Exception as exc:
        return _err("PERMISSION_SCOPE_QUERY_FAILED", str(exc))


@tool
def debug_query_zero_results(
    user_id: str,
    tool_name: str,
    query: str = "",
    confirmed_only: bool | None = None,
    category: str = "",
    types: str = "",
):
    """当查询工具返回 0 个结果时，诊断空结果的原因并给出下一步建议。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                diagnostic_tool_service.debug_query_zero_results_payload(
                    session,
                    uid,
                    tool_name=tool_name,
                    query=query,
                    confirmed_only=confirmed_only,
                    category=category,
                    types=types,
                )
            )
    except Exception as exc:
        return _err("QUERY_ZERO_DEBUG_FAILED", str(exc))


@tool
def unified_search_tool(
    user_id: str,
    query: str,
    limit: int = 12,
    types: str = "",
):
    """执行全局统一搜索，跨历史记录、Agent 会话、政策和新闻联合检索。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                search_tool_service.unified_search_payload(
                    session,
                    uid,
                    query=query,
                    limit=limit,
                    types=types,
                )
            )
    except Exception as exc:
        return _err("UNIFIED_SEARCH_FAILED", str(exc))


@tool
def search_chat_messages_fulltext(
    user_id: str,
    query: str,
    skip: int = 0,
    limit: int = 20,
    handling_only: bool = False,
):
    """按原文、办理事项、材料、流程、风险和图谱字段全文检索历史解析消息。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                search_tool_service.search_chat_messages_fulltext_payload(
                    session,
                    uid,
                    query=query,
                    skip=skip,
                    limit=limit,
                    handling_only=handling_only,
                )
            )
    except Exception as exc:
        return _err("CHAT_FULLTEXT_SEARCH_FAILED", str(exc))


@tool
def search_policy_documents_by_query(
    user_id: str,
    query: str,
    category: str = "",
    skip: int = 0,
    limit: int = 20,
):
    """按关键词检索政策文档，覆盖标题、分类、标签和正文内容。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                search_tool_service.search_policy_documents_payload(
                    session,
                    uid,
                    query=query,
                    category=category,
                    skip=skip,
                    limit=limit,
                    approved_only=True,
                )
            )
    except Exception as exc:
        return _err("POLICY_QUERY_SEARCH_FAILED", str(exc))


@tool
def list_user_uploaded_files(user_id: str, limit: int = 20):
    """列出当前用户最近上传的文档、OCR 文件和会话导出快照。"""
    try:
        uid = _uid(user_id)
        return _ok(file_tool_service.list_user_uploaded_files_payload(uid, limit=limit))
    except Exception as exc:
        return _err("USER_FILES_LIST_FAILED", str(exc))


@tool
def parse_uploaded_document(user_id: str, file_ref: str):
    """解析当前用户已上传的文档文件，支持 PDF、Word、Excel、TXT 和 JSON 快照。"""
    try:
        uid = _uid(user_id)
        return _ok(file_tool_service.parse_uploaded_document_payload(uid, file_ref=file_ref))
    except PermissionError:
        return _err("FILE_ACCESS_DENIED", "无权访问该文件")
    except FileNotFoundError:
        return _err("FILE_NOT_FOUND", "未找到该文件")
    except ValueError as exc:
        code = str(exc)
        if code == "IMAGE_FILE_REQUIRES_OCR":
            return _err("IMAGE_FILE_REQUIRES_OCR", "图片文件请改用 parse_uploaded_image_ocr")
        return _err("DOCUMENT_PARSE_FAILED", code)
    except Exception as exc:
        return _err("DOCUMENT_PARSE_FAILED", str(exc))


@tool
def parse_uploaded_image_ocr(user_id: str, file_ref: str):
    """对当前用户上传的图片执行 OCR，提取可读文本。"""
    try:
        uid = _uid(user_id)
        return _ok(file_tool_service.parse_uploaded_image_ocr_payload(uid, file_ref=file_ref))
    except PermissionError:
        return _err("FILE_ACCESS_DENIED", "无权访问该文件")
    except FileNotFoundError:
        return _err("FILE_NOT_FOUND", "未找到该文件")
    except ValueError as exc:
        return _err("IMAGE_OCR_FAILED", str(exc))
    except Exception as exc:
        return _err("IMAGE_OCR_FAILED", str(exc))


@tool
def build_document_knowledge_graph(user_id: str, original_text: str, title: str = ""):
    """从输入文本构建知识图谱，并返回可直接展示的小窗图谱数据。"""
    try:
        uid = _uid(user_id)
        return _ok(
            file_tool_service.build_document_knowledge_graph_payload(
                uid,
                original_text=original_text,
                title=title,
            )
        )
    except Exception as exc:
        return _err("KNOWLEDGE_GRAPH_BUILD_FAILED", str(exc))


@tool
def get_message_knowledge_graph(user_id: str, message_id: int):
    """读取某条历史解析消息中的知识图谱和原文映射数据。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                file_tool_service.get_message_knowledge_graph_payload(
                    session,
                    uid,
                    message_id=message_id,
                )
            )
    except PermissionError:
        return _err("MESSAGE_NOT_FOUND", "未找到该消息或无权访问")
    except Exception as exc:
        return _err("MESSAGE_KNOWLEDGE_GRAPH_FAILED", str(exc))


@tool
def show_knowledge_graph_modal(
    user_id: str,
    message_id: int | None = None,
    original_text: str = "",
    title: str = "",
):
    """生成知识图谱小窗展示卡片，可基于历史消息或直接输入文本。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                file_tool_service.show_knowledge_graph_modal_payload(
                    session,
                    uid,
                    message_id=message_id,
                    original_text=original_text,
                    title=title,
                )
            )
    except PermissionError:
        return _err("GRAPH_SOURCE_DENIED", "无权访问该图谱来源")
    except ValueError as exc:
        return _err("GRAPH_SOURCE_REQUIRED", str(exc))
    except Exception as exc:
        return _err("GRAPH_MODAL_BUILD_FAILED", str(exc))


@tool
def build_metric_cards(user_id: str):
    """把当前用户统计结果转换为指标卡展示数据。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(stats_tool_service.build_metric_cards_payload(session, uid))
    except Exception as exc:
        return _err("METRIC_CARDS_BUILD_FAILED", str(exc))


@tool
def get_admin_analysis_overview(user_id: str):
    """获取管理员全局分析总览，包含用户统计、RAG 命中和高活跃用户。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(admin_tool_service.get_admin_analysis_overview_payload(session, uid))
    except PermissionError:
        return _err("ADMIN_REQUIRED", "该工具需要管理员权限")
    except Exception as exc:
        return _err("ADMIN_ANALYSIS_OVERVIEW_FAILED", str(exc))


@tool
def build_admin_metric_cards(user_id: str):
    """生成管理员专用的系统指标卡，用于综合数据分析展示。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(admin_tool_service.build_admin_metric_cards_payload(session, uid))
    except PermissionError:
        return _err("ADMIN_REQUIRED", "该工具需要管理员权限")
    except Exception as exc:
        return _err("ADMIN_METRIC_CARDS_BUILD_FAILED", str(exc))


@tool
def get_admin_user_role_distribution(user_id: str):
    """查看管理员视角下的用户角色分布统计。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(admin_tool_service.get_admin_user_role_distribution_payload(session, uid))
    except PermissionError:
        return _err("ADMIN_REQUIRED", "该工具需要管理员权限")
    except Exception as exc:
        return _err("ADMIN_ROLE_DISTRIBUTION_FAILED", str(exc))


@tool
def get_admin_policy_review_overview(user_id: str, limit: int = 10):
    """查看管理员视角下的政策文档审核分布和最近文档列表。"""
    try:
        uid = _uid(user_id)
        with Session(engine) as session:
            return _ok(
                admin_tool_service.get_admin_policy_review_overview_payload(
                    session,
                    uid,
                    limit=limit,
                )
            )
    except PermissionError:
        return _err("ADMIN_REQUIRED", "该工具需要管理员权限")
    except Exception as exc:
        return _err("ADMIN_POLICY_REVIEW_OVERVIEW_FAILED", str(exc))


tools = [
    query_long_term_memory,
    parse_local_file,
    get_my_todos,
    create_todos_from_chat,
    confirm_todo,
    search_policy_documents,
    recommend_policy_documents,
    get_user_settings,
    update_user_settings,
    search_chat_history,
    get_chat_message_detail,
    get_news_digest,
    search_news_tool,
    list_favorites,
    add_favorite,
    get_my_stats,
    rewrite_for_audience,
    inspect_agent_runtime,
    list_available_tools,
    get_user_permission_scope,
    debug_query_zero_results,
    unified_search_tool,
    search_chat_messages_fulltext,
    search_policy_documents_by_query,
    list_user_uploaded_files,
    parse_uploaded_document,
    parse_uploaded_image_ocr,
    build_document_knowledge_graph,
    get_message_knowledge_graph,
    show_knowledge_graph_modal,
    build_metric_cards,
    get_admin_analysis_overview,
    build_admin_metric_cards,
    get_admin_user_role_distribution,
    get_admin_policy_review_overview,
]
tool_node = ToolNode(tools)
