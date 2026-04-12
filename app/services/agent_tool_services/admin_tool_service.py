from __future__ import annotations

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.chat_message import ChatMessage
from app.models.opinion import Opinion
from app.models.policy_document import DocStatus, PolicyDocument
from app.models.user import User
from app.services import stats_service
from app.services.agent_tool_services.base import (
    get_user_role,
    metric_board_display,
    ok_item_payload,
    role_allows,
    table_display,
)


def _ensure_admin(session: Session, user_id: int) -> None:
    if not role_allows(get_user_role(session, user_id), "admin"):
        raise PermissionError("ADMIN_REQUIRED")


def _collect_role_distribution(session: Session) -> dict[str, int]:
    rows = session.exec(
        select(User.role, func.count(User.uid)).group_by(User.role)
    ).all()
    result: dict[str, int] = {}
    for role, count in rows:
        key = getattr(role, "value", str(role))
        result[key] = int(count or 0)
    return result


def _collect_top_active_users(session: Session, *, limit: int = 10) -> list[dict[str, object]]:
    rows = session.exec(
        select(
            User.uid,
            User.uname,
            func.count(ChatMessage.id).label("message_count"),
        )
        .join(ChatMessage, ChatMessage.user_id == User.uid)
        .where(ChatMessage.is_deleted == False)
        .group_by(User.uid, User.uname)
        .order_by(func.count(ChatMessage.id).desc())
        .limit(max(1, min(limit, 20)))
    ).all()
    return [
        {
            "user_id": int(uid),
            "user_name": uname,
            "message_count": int(message_count or 0),
        }
        for uid, uname, message_count in rows
    ]


def build_admin_metric_cards_payload(session: Session, user_id: int) -> dict[str, object]:
    _ensure_admin(session, user_id)
    total_users = int(session.exec(select(func.count(User.uid))).one() or 0)
    total_messages = int(
        session.exec(
            select(func.count(ChatMessage.id)).where(ChatMessage.is_deleted == False)
        ).one()
        or 0
    )
    active_users = int(
        session.exec(
            select(func.count(func.distinct(ChatMessage.user_id))).where(
                ChatMessage.is_deleted == False
            )
        ).one()
        or 0
    )
    total_docs = int(session.exec(select(func.count(PolicyDocument.id))).one() or 0)
    pending_docs = int(
        session.exec(
            select(func.count(PolicyDocument.id)).where(
                PolicyDocument.status == DocStatus.pending
            )
        ).one()
        or 0
    )
    total_opinions = int(session.exec(select(func.count(Opinion.id))).one() or 0)
    items = [
        {"label": "注册用户", "value": total_users, "unit": "人"},
        {"label": "解析消息", "value": total_messages, "unit": "条"},
        {"label": "活跃用户", "value": active_users, "unit": "人"},
        {"label": "政策文档", "value": total_docs, "unit": "份"},
        {"label": "待审核文档", "value": pending_docs, "unit": "份"},
        {"label": "反馈意见", "value": total_opinions, "unit": "条"},
    ]
    return ok_item_payload(
        {"scope": "admin", "items": items},
        meta={"role": "admin", "total_metrics": len(items)},
        display=[metric_board_display(title="管理员系统指标", items=items)],
    )


def get_admin_user_role_distribution_payload(
    session: Session,
    user_id: int,
) -> dict[str, object]:
    _ensure_admin(session, user_id)
    role_dist = _collect_role_distribution(session)
    rows = [
        {"role": role, "user_count": count}
        for role, count in sorted(role_dist.items(), key=lambda item: item[0])
    ]
    return ok_item_payload(
        {"scope": "admin", "role_distribution": role_dist},
        meta={"role_count": len(role_dist)},
        display=[
            table_display(
                title="用户角色分布",
                columns=[
                    {"key": "role", "label": "角色"},
                    {"key": "user_count", "label": "人数"},
                ],
                rows=rows,
            )
        ],
    )


def get_admin_policy_review_overview_payload(
    session: Session,
    user_id: int,
    *,
    limit: int = 10,
) -> dict[str, object]:
    _ensure_admin(session, user_id)
    docs = list(
        session.exec(
            select(PolicyDocument)
            .order_by(PolicyDocument.created_time.desc())
            .limit(max(1, min(limit, 30)))
        ).all()
    )
    rows = []
    for doc in docs:
        uploader = session.get(User, doc.uploader_id)
        rows.append(
            {
                "id": doc.id,
                "title": doc.title,
                "status": getattr(doc.status, "value", str(doc.status)),
                "category": doc.category,
                "uploader_name": uploader.uname if uploader else None,
                "created_time": doc.created_time.isoformat() if doc.created_time else None,
                "reviewed_time": doc.reviewed_time.isoformat() if doc.reviewed_time else None,
            }
        )

    counts = {
        "pending": int(
            session.exec(
                select(func.count(PolicyDocument.id)).where(
                    PolicyDocument.status == DocStatus.pending
                )
            ).one()
            or 0
        ),
        "approved": int(
            session.exec(
                select(func.count(PolicyDocument.id)).where(
                    PolicyDocument.status == DocStatus.approved
                )
            ).one()
            or 0
        ),
        "rejected": int(
            session.exec(
                select(func.count(PolicyDocument.id)).where(
                    PolicyDocument.status == DocStatus.rejected
                )
            ).one()
            or 0
        ),
    }
    return ok_item_payload(
        {
            "scope": "admin",
            "policy_review_counts": counts,
            "recent_documents": rows,
        },
        meta={"recent_limit": max(1, min(limit, 30))},
        display=[
            metric_board_display(
                title="政策审核概览",
                items=[
                    {"label": "待审核", "value": counts["pending"], "unit": "份"},
                    {"label": "已通过", "value": counts["approved"], "unit": "份"},
                    {"label": "已驳回", "value": counts["rejected"], "unit": "份"},
                ],
            ),
            table_display(
                title="最近政策文档",
                columns=[
                    {"key": "id", "label": "ID"},
                    {"key": "title", "label": "标题"},
                    {"key": "status", "label": "状态"},
                    {"key": "uploader_name", "label": "上传者"},
                ],
                rows=rows[:12],
            ),
        ],
    )


def get_admin_analysis_overview_payload(
    session: Session,
    user_id: int,
) -> dict[str, object]:
    _ensure_admin(session, user_id)
    stats = stats_service.generate_all_users_stats(session)
    top_active_users = _collect_top_active_users(session, limit=10)
    role_dist = _collect_role_distribution(session)
    total_users = int(session.exec(select(func.count(User.uid))).one() or 0)
    active_users = int(
        session.exec(
            select(func.count(func.distinct(ChatMessage.user_id))).where(
                ChatMessage.is_deleted == False
            )
        ).one()
        or 0
    )
    display = [
        metric_board_display(
            title="平台分析总览",
            items=[
                {"label": "总用户", "value": total_users, "unit": "人"},
                {"label": "活跃用户", "value": active_users, "unit": "人"},
                {"label": "总解析量", "value": stats.get("total_parsed_count", 0), "unit": "条"},
                {
                    "label": "RAG 命中率",
                    "value": round(float((stats.get("rag_metrics", {}) or {}).get("hit_rate", 0) or 0) * 100, 1),
                    "unit": "%",
                },
            ],
        )
    ]
    if top_active_users:
        display.append(
            table_display(
                title="高活跃用户",
                columns=[
                    {"key": "user_id", "label": "用户ID"},
                    {"key": "user_name", "label": "用户名"},
                    {"key": "message_count", "label": "解析条数"},
                ],
                rows=top_active_users,
            )
        )
    return ok_item_payload(
        {
            "scope": "admin",
            "total_users": total_users,
            "active_users": active_users,
            "role_distribution": role_dist,
            "top_active_users": top_active_users,
            "stats": stats,
        },
        meta={"role_count": len(role_dist), "top_active_user_count": len(top_active_users)},
        display=display,
    )
