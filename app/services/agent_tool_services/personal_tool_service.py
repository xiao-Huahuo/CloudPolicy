from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from app.models.settings import Settings
from app.models.user import User
from app.services.agent_tool_services.base import normalize_role_value, ok_item_payload


def _verified_contacts(user: User) -> list[str]:
    contacts: list[str] = []
    if user.email and user.email_verified:
        contacts.append("email")
    if (user.phone or user.login_phone) and user.phone_verified:
        contacts.append("phone")
    return contacts


def get_personal_profile_payload(session: Session, user_id: int) -> dict[str, Any]:
    user = session.get(User, user_id)
    if not user:
        return ok_item_payload(
            {
                "user": None,
                "settings": None,
                "personal_profile": {
                    "label": "未登录用户",
                    "verified_contacts": [],
                    "recommendation_basis": [],
                },
            }
        )

    settings = session.exec(select(Settings).where(Settings.user_id == user_id)).first()
    role = normalize_role_value(user.role)
    profession = str(user.profession or "").strip()
    audience = settings.default_audience if settings else "none"
    recommendation_basis = [item for item in [role, profession, audience] if item and item != "none"]

    item = {
        "user": {
            "uid": user.uid,
            "uname": user.uname,
            "email": user.email,
            "phone": user.phone or user.login_phone,
            "avatar_url": user.avatar_url,
            "role": role,
            "profession": user.profession,
            "email_verified": bool(user.email_verified),
            "phone_verified": bool(user.phone_verified),
            "preferred_login_method": user.preferred_login_method,
            "last_login_method": user.last_login_method,
        },
        "settings": settings.model_dump() if settings else None,
        "personal_profile": {
            "label": f"{role} / {profession}" if profession else role,
            "verified_contacts": _verified_contacts(user),
            "recommendation_basis": recommendation_basis,
        },
    }
    return ok_item_payload(item)
