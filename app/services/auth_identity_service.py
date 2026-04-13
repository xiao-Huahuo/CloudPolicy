import re
import secrets
from typing import Optional

from sqlmodel import Session, select

from app.models.user import User
from app.schemas.user import UserRead


PLACEHOLDER_EMAIL_DOMAIN = "phone-auth.local.invalid"
MAINLAND_PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def normalize_login_phone(phone: str) -> str:
    digits = "".join(ch for ch in (phone or "") if ch.isdigit())
    if digits.startswith("86") and len(digits) == 13:
        digits = digits[2:]
    return digits


def is_valid_login_phone(phone: str) -> bool:
    return bool(MAINLAND_PHONE_RE.fullmatch(normalize_login_phone(phone)))


def build_placeholder_email(phone: str) -> str:
    normalized = normalize_login_phone(phone)
    salt = secrets.token_hex(3)
    return f"phone-{normalized}-{salt}@{PLACEHOLDER_EMAIL_DOMAIN}"


def is_placeholder_email(email: Optional[str]) -> bool:
    normalized = normalize_email(email or "")
    return normalized.endswith(f"@{PLACEHOLDER_EMAIL_DOMAIN}")


def get_public_email(email: Optional[str]) -> Optional[str]:
    normalized = normalize_email(email or "")
    if not normalized or is_placeholder_email(normalized):
        return None
    return normalized


def has_public_email(user: User) -> bool:
    return bool(get_public_email(user.email))


def mask_phone(phone: Optional[str]) -> str:
    normalized = normalize_login_phone(phone or "")
    if len(normalized) != 11:
        return phone or ""
    return f"{normalized[:3]}****{normalized[-4:]}"


def mask_email(email: Optional[str]) -> str:
    public_email = get_public_email(email)
    if not public_email or "@" not in public_email:
        return ""
    local, domain = public_email.split("@", 1)
    if len(local) <= 1:
        masked_local = "*"
    elif len(local) == 2:
        masked_local = f"{local[0]}*"
    else:
        masked_local = f"{local[0]}***{local[-1]}"
    return f"{masked_local}@{domain}"


def password_login_allowed(user: User) -> bool:
    return bool(user.password_login_enabled and user.hashed_pwd)


def verification_allows_password_login(user: User) -> bool:
    if user.phone_verified:
        return True
    public_email = get_public_email(user.email)
    if public_email:
        return user.email_verified
    return True


def detect_identity_kind(identity: str) -> str:
    normalized = (identity or "").strip()
    if "@" in normalized:
        return "email"
    if is_valid_login_phone(normalized):
        return "phone"
    return "username"


def resolve_user_for_password_identity(session: Session, identity: str) -> Optional[User]:
    normalized = (identity or "").strip()
    if not normalized:
        return None
    if "@" in normalized:
        return session.exec(select(User).where(User.email == normalize_email(normalized))).first()
    normalized_phone = normalize_login_phone(normalized)
    if is_valid_login_phone(normalized_phone):
        user = session.exec(select(User).where(User.login_phone == normalized_phone)).first()
        if user:
            return user
    return session.exec(select(User).where(User.uname == normalized)).first()


def resolve_user_for_identifier(session: Session, identifier: str) -> Optional[User]:
    raw = (identifier or "").strip()
    if not raw:
        return None
    normalized_phone = normalize_login_phone(raw)
    if is_valid_login_phone(normalized_phone):
        user = session.exec(select(User).where(User.login_phone == normalized_phone)).first()
        if user:
            return user
    if "@" in raw:
        return session.exec(select(User).where(User.email == normalize_email(raw))).first()
    return session.exec(select(User).where(User.uname == raw)).first()


def to_user_read(user: User) -> UserRead:
    return UserRead(
        uid=user.uid,
        uname=user.uname,
        email=get_public_email(user.email),
        phone=user.phone,
        login_phone=user.login_phone,
        avatar_url=user.avatar_url,
        role=user.role,
        profession=user.profession,
        created_time=user.created_time,
        last_login=user.last_login,
        email_verified=user.email_verified,
        phone_verified=user.phone_verified,
        password_login_enabled=user.password_login_enabled,
        preferred_login_method=user.preferred_login_method,
        last_login_method=user.last_login_method,
    )
