import asyncio
import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, func, select

from app.api.deps import get_current_user, get_current_user_from_token_value
from app.core.config import GlobalConfig
from app.core.database import get_session
from app.models.chat_message import ChatMessage
from app.models.user import User, UserRole
from app.services import email_service, stats_service


router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user


@router.get("/users", response_model=List[dict])
def list_users(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    users = session.exec(select(User)).all()
    return [
        {
            "uid": u.uid,
            "uname": u.uname,
            "email": u.email,
            "role": u.role,
            "created_time": str(u.created_time),
            "last_login": str(u.last_login),
            "avatar_url": u.avatar_url,
            "email_verified": u.email_verified,
        }
        for u in users
    ]


@router.get("/stats")
def admin_stats(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    total_users = session.exec(select(func.count(User.uid))).one()
    total_messages = session.exec(
        select(func.count(ChatMessage.id)).where(ChatMessage.is_deleted == False)
    ).one()
    active_users = session.exec(
        select(func.count(func.distinct(ChatMessage.user_id))).where(ChatMessage.is_deleted == False)
    ).one()
    user_msg_counts = session.exec(
        select(ChatMessage.user_id, func.count(ChatMessage.id))
        .where(ChatMessage.is_deleted == False)
        .group_by(ChatMessage.user_id)
    ).all()
    return {
        "total_users": total_users,
        "total_messages": total_messages,
        "active_users": active_users,
        "user_message_counts": [
            {"user_id": uid, "count": cnt} for uid, cnt in user_msg_counts
        ],
    }


@router.patch("/users/{uid}/set-role", response_model=dict)
def set_user_role(
    uid: int,
    role: UserRole,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    user = session.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.uid == admin.uid:
        raise HTTPException(status_code=400, detail="Cannot modify yourself")
    user.role = role
    session.add(user)
    session.commit()
    role_names = {
        UserRole.normal: "普通用户",
        UserRole.certified: "认证主体",
        UserRole.admin: "管理员",
    }
    email_service.send_role_change_email(user, role_names[role])
    return {"uid": user.uid, "role": user.role}


@router.patch("/users/{uid}/toggle-admin", response_model=dict)
def toggle_admin(
    uid: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    user = session.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.uid == admin.uid:
        raise HTTPException(status_code=400, detail="Cannot modify yourself")
    user.role = UserRole.admin if user.role != UserRole.admin else UserRole.normal
    session.add(user)
    session.commit()
    email_service.send_role_change_email(
        user,
        "管理员" if user.role == UserRole.admin else "普通用户",
    )
    return {"uid": user.uid, "role": user.role}


@router.delete("/users/{uid}")
def delete_user(
    uid: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    user = session.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.uid == admin.uid:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    session.delete(user)
    session.commit()
    return {"ok": True}


@router.get("/analysis/all")
def admin_analysis_all(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    return stats_service.generate_all_users_stats(session)


@router.get("/stats/stream")
async def admin_stats_stream(
    token: str = Query(...),
    session: Session = Depends(get_session),
):
    admin = get_current_user_from_token_value(session, token)
    if admin.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin only")

    async def event_generator():
        while True:
            payload = admin_stats(session=session, admin=admin)
            payload["timestamp"] = asyncio.get_running_loop().time()
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            await asyncio.sleep(GlobalConfig.REALTIME_STREAM_INTERVAL_SECONDS)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/logs")
def read_logs(
    limit: int = Query(200, ge=20, le=1000),
    admin: User = Depends(require_admin),
):
    log_path = Path(GlobalConfig.APP_LOG_PATH)
    if not log_path.exists():
        return {"items": []}
    lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return {"items": lines[-limit:]}


@router.get("/rag/status")
def rag_status(admin: User = Depends(require_admin)):
    return {
        "backend": "disabled",
        "document_count": 0,
        "knowledge_base_path": str(GlobalConfig.KNOWLEDGE_BASE_PATH),
    }


@router.get("/rag/search")
def rag_search(
    q: str = Query("", description="RAG 查询关键词"),
    top_k: int = Query(5, ge=1, le=10),
    admin: User = Depends(require_admin),
):
    return {"items": []}

@router.get("/user-geo")
def admin_user_geo(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    import ipaddress
    users = session.exec(select(User)).all()
    # Simple heuristic: map last octet mod to provinces for demo
    provinces = [
        "广东", "北京", "上海", "浙江", "江苏", "四川", "湖北", "湖南",
        "山东", "河南", "福建", "陕西", "辽宁", "河北", "安徽", "重庆",
        "云南", "贵州", "江西", "黑龙江", "吉林", "内蒙古", "广西", "新疆",
        "甘肃", "山西", "天津", "海南", "宁夏", "青海", "西藏",
    ]
    dist = {}
    for u in users:
        ip = u.last_ip
        if not ip:
            continue
        try:
            addr = ipaddress.ip_address(ip)
            if addr.is_private or addr.is_loopback:
                # assign based on uid for demo variety
                prov = provinces[u.uid % len(provinces)]
            else:
                prov = provinces[int(ip.split(".")[-1]) % len(provinces)]
        except Exception:
            continue
        dist[prov] = dist.get(prov, 0) + 1
    return {"geo_dist": [{"name": k, "value": v} for k, v in dist.items()]}


@router.get("/opinion-stats")
def admin_opinion_stats(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    from app.models.opinion import Opinion
    from app.models.policy_document import PolicyDocument
    opinions = session.exec(select(Opinion)).all()
    type_dist = {}
    rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    word_freq = {}
    for op in opinions:
        type_dist[op.opinion_type] = type_dist.get(op.opinion_type, 0) + 1
        if op.rating:
            r = max(1, min(5, int(op.rating)))
            rating_dist[r] = rating_dist.get(r, 0) + 1
        for word in (op.content or "").split():
            if len(word) >= 2:
                word_freq[word] = word_freq.get(word, 0) + 1
    hot_words = sorted(word_freq.items(), key=lambda x: -x[1])[:30]
    total_docs = session.exec(select(func.count(PolicyDocument.id))).one()
    from app.models.policy_document import DocStatus
    approved_docs = session.exec(select(func.count(PolicyDocument.id)).where(PolicyDocument.status == DocStatus.approved)).one()
    pending_docs = session.exec(select(func.count(PolicyDocument.id)).where(PolicyDocument.status == DocStatus.pending)).one()
    return {
        "total_opinions": len(opinions),
        "type_dist": type_dist,
        "rating_dist": {str(k): v for k, v in rating_dist.items()},
        "hot_words": [{"word": w, "count": c} for w, c in hot_words],
        "total_docs": total_docs,
        "approved_docs": approved_docs,
        "pending_docs": pending_docs,
    }


@router.get("/user-role-dist")
def admin_user_role_dist(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    users = session.exec(select(User)).all()
    dist = {}
    for u in users:
        dist[u.role] = dist.get(u.role, 0) + 1
    return {"role_dist": dist}


@router.get("/users/{uid}/avatar")
def get_user_avatar(
    uid: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin),
):
    user = session.get(User, uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"uid": uid, "avatar_url": user.avatar_url}


