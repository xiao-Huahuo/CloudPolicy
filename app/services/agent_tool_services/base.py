from __future__ import annotations

import asyncio
import json
import mimetypes
from pathlib import Path
from typing import Any

from sqlmodel import Session

from app.core.config import GlobalConfig
from app.models.user import User, UserRole


ROLE_LEVELS = {
    "normal": 0,
    "certified": 1,
    "admin": 2,
}


def json_dumps(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def normalize_role_value(role: Any) -> str:
    if isinstance(role, UserRole):
        return role.value
    raw = str(role or "").strip().lower()
    if raw.endswith(".admin") or raw == "admin":
        return "admin"
    if raw.endswith(".certified") or raw == "certified":
        return "certified"
    return "normal"


def role_allows(role: Any, minimum_role: str = "normal") -> bool:
    current = ROLE_LEVELS.get(normalize_role_value(role), 0)
    required = ROLE_LEVELS.get(normalize_role_value(minimum_role), 0)
    return current >= required


def get_user_or_none(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_role(session: Session, user_id: int) -> str:
    user = get_user_or_none(session, user_id)
    return normalize_role_value(user.role if user else "normal")


def compact_text(value: Any, limit: int = 240) -> str:
    text = " ".join(str(value or "").split()).strip()
    if not text:
        return ""
    return text if len(text) <= limit else f"{text[: limit - 3]}..."


def guess_empty_reason(
    *,
    items_count: int,
    source_total: int | None = None,
    query: str = "",
    filters_applied: bool = False,
    permission_denied: bool = False,
) -> str | None:
    if items_count > 0:
        return None
    if permission_denied:
        return "permission_denied"
    if source_total == 0:
        return "data_source_empty"
    if query:
        return "no_match"
    if filters_applied:
        return "filter_too_strict"
    return "no_match"


def ok_list_payload(
    items: list[Any],
    *,
    query: str = "",
    total: int | None = None,
    source_total: int | None = None,
    applied_filters: dict[str, Any] | None = None,
    empty_reason: str | None = None,
    suggested_tools: list[str] | None = None,
    fallback_used: bool = False,
    display: list[dict[str, Any]] | None = None,
    meta_extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    filters = applied_filters or {}
    meta = {
        "query": query,
        "total": len(items) if total is None else total,
        "source_total": source_total,
        "applied_filters": filters,
        "empty_reason": empty_reason
        if empty_reason is not None
        else guess_empty_reason(
            items_count=len(items),
            source_total=source_total,
            query=query,
            filters_applied=bool(filters),
        ),
        "fallback_used": fallback_used,
        "suggested_tools": suggested_tools or [],
    }
    if meta_extra:
        meta.update(meta_extra)
    return {
        "ok": True,
        "items": items,
        "meta": meta,
        "display": display or [],
    }


def ok_item_payload(
    item: Any,
    *,
    meta: dict[str, Any] | None = None,
    display: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "item": item,
        "meta": meta or {},
        "display": display or [],
    }


def ok_action_payload(
    item: Any,
    *,
    confirmed: bool,
    required: bool = True,
    meta: dict[str, Any] | None = None,
    display: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "item": item,
        "confirm": {
            "required": required,
            "confirmed": confirmed,
        },
        "meta": meta or {},
        "display": display or [],
    }


def error_payload(code: str, message: str, *, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "ok": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if meta:
        payload["meta"] = meta
    return payload


def display_card(
    card_type: str,
    title: str,
    payload: dict[str, Any],
    *,
    placement: str = "modal",
    subtitle: str | None = None,
) -> dict[str, Any]:
    card = {
        "type": card_type,
        "title": title,
        "placement": placement,
        "payload": payload,
    }
    if subtitle:
        card["subtitle"] = subtitle
    return card


def knowledge_graph_display(
    *,
    title: str,
    content: str,
    nodes: list[dict[str, Any]],
    links: list[dict[str, Any]],
    dynamic_payload: dict[str, Any],
    visual_config: dict[str, Any],
    placement: str = "modal",
) -> dict[str, Any]:
    return display_card(
        "knowledge_graph",
        title,
        {
            "content": content,
            "nodes": nodes,
            "links": links,
            "dynamic_payload": dynamic_payload,
            "visual_config": visual_config,
        },
        placement=placement,
    )


def original_text_display(
    *,
    title: str,
    content: str,
    file_url: str | None = None,
    placement: str = "right_drawer",
) -> dict[str, Any]:
    payload: dict[str, Any] = {"content": content}
    if file_url:
        payload["file_url"] = file_url
    return display_card("original_text", title, payload, placement=placement)


def table_display(
    *,
    title: str,
    columns: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    placement: str = "right_drawer",
) -> dict[str, Any]:
    return display_card(
        "table",
        title,
        {
            "columns": columns,
            "rows": rows,
        },
        placement=placement,
    )


def metric_board_display(
    *,
    title: str,
    items: list[dict[str, Any]],
    placement: str = "right_drawer",
) -> dict[str, Any]:
    return display_card(
        "metric_board",
        title,
        {"items": items},
        placement=placement,
    )


def _path_in_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def media_url_for_path(path: Path) -> str | None:
    resolved = path.resolve()
    roots = {
        GlobalConfig.DOCS_UPLOAD_DIR.resolve(): "/media/docs",
        GlobalConfig.IMAGES_UPLOAD_DIR.resolve(): "/media/images",
        GlobalConfig.AVATAR_UPLOAD_DIR.resolve(): "/media/avatars",
    }
    for root, prefix in roots.items():
        if _path_in_root(resolved, root):
            return f"{prefix}/{resolved.name}"
    return None


def file_item_payload(path: Path, *, kind: str, file_url: str | None = None) -> dict[str, Any]:
    stat = path.stat()
    return {
        "name": path.name,
        "path": str(path),
        "kind": kind,
        "suffix": path.suffix.lower(),
        "size_bytes": stat.st_size,
        "modified_time": stat.st_mtime,
        "file_url": file_url,
        "content_type": mimetypes.guess_type(path.name)[0],
    }


def _docs_file_owned_by_user(path: Path, user_id: int) -> bool:
    name = path.name
    return name.startswith(f"doc_{user_id}_") or name.startswith(f"ocr_{user_id}_")


def _recent_user_doc_candidates(user_id: int, suffix: str | None = None) -> list[Path]:
    candidates = list(GlobalConfig.DOCS_UPLOAD_DIR.glob(f"doc_{user_id}_*")) + list(
        GlobalConfig.DOCS_UPLOAD_DIR.glob(f"ocr_{user_id}_*")
    )
    if suffix:
        suffix = suffix.lower()
        candidates = [item for item in candidates if item.suffix.lower() == suffix]
    return sorted(
        [item.resolve() for item in candidates if item.exists() and item.is_file()],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )


def resolve_user_file_reference(user_id: int, file_ref: str) -> Path:
    raw = str(file_ref or "").strip()
    if not raw:
        raise ValueError("FILE_REF_REQUIRED")

    if raw.startswith("http://") or raw.startswith("https://"):
        marker = "/media/"
        idx = raw.find(marker)
        if idx >= 0:
            raw = raw[idx:]

    if raw.startswith("/media/docs/"):
        candidate = (GlobalConfig.DOCS_UPLOAD_DIR / Path(raw).name).resolve()
        if candidate.exists() and _docs_file_owned_by_user(candidate, user_id):
            return candidate
        raise PermissionError("FILE_ACCESS_DENIED")

    if raw.startswith("/media/images/"):
        candidate = (GlobalConfig.IMAGES_UPLOAD_DIR / Path(raw).name).resolve()
        if candidate.exists():
            return candidate
        raise FileNotFoundError(raw)

    if raw.startswith("/media/avatars/"):
        candidate = (GlobalConfig.AVATAR_UPLOAD_DIR / Path(raw).name).resolve()
        if candidate.exists() and candidate.name.startswith(f"user_{user_id}_"):
            return candidate
        raise PermissionError("FILE_ACCESS_DENIED")

    chat_dir = (GlobalConfig.CHAT_EXPORT_DIR / f"user_{user_id}").resolve()
    if raw.startswith("chat_") and raw.endswith(".json"):
        candidate = (chat_dir / Path(raw).name).resolve()
        if candidate.exists():
            return candidate

    candidate = Path(raw)
    if not candidate.is_absolute():
        docs_candidate = (GlobalConfig.DOCS_UPLOAD_DIR / candidate.name).resolve()
        if docs_candidate.exists() and _docs_file_owned_by_user(docs_candidate, user_id):
            return docs_candidate
        chat_candidate = (chat_dir / candidate.name).resolve()
        if chat_candidate.exists():
            return chat_candidate
        # LLMs may pass the original upload filename instead of the internal /media/docs ref.
        # Fall back only when there is exactly one recent user upload with the same suffix.
        if candidate.name and not candidate.name.startswith(("doc_", "ocr_")):
            recent_candidates = _recent_user_doc_candidates(user_id, suffix=candidate.suffix or None)
            if len(recent_candidates) == 1:
                return recent_candidates[0]
        candidate = candidate.resolve()
    else:
        candidate = candidate.resolve()

    allowed_roots = [
        GlobalConfig.DOCS_UPLOAD_DIR.resolve(),
        chat_dir,
    ]
    for root in allowed_roots:
        if _path_in_root(candidate, root):
            if root == GlobalConfig.DOCS_UPLOAD_DIR.resolve() and not _docs_file_owned_by_user(candidate, user_id):
                raise PermissionError("FILE_ACCESS_DENIED")
            return candidate

    raise PermissionError("FILE_ACCESS_DENIED")


def run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
