from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlmodel import Session

from app.core.config import GlobalConfig
from app.core.database import get_session
from app.models.user import User
from app.schemas.token import TokenPayload


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/")
optional_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/", auto_error=False)


def _decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            GlobalConfig.SECRET_KEY,
            algorithms=[GlobalConfig.ALGORITHM],
        )
        return TokenPayload(**payload)
    except (JWTError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from exc


def _resolve_user(session: Session, token_data: TokenPayload) -> User:
    if token_data.sub is None:
        raise HTTPException(status_code=404, detail="User not found")

    user = session.get(User, int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(reusable_oauth2),
) -> User:
    token_data = _decode_token(token)
    return _resolve_user(session, token_data)


def get_current_user_from_token_value(session: Session, token: str) -> User:
    token_data = _decode_token(token)
    return _resolve_user(session, token_data)


def get_optional_current_user(
    session: Session = Depends(get_session),
    token: Optional[str] = Depends(optional_oauth2),
) -> Optional[User]:
    if not token:
        return None
    try:
        token_data = _decode_token(token)
    except HTTPException:
        return None
    try:
        return _resolve_user(session, token_data)
    except HTTPException:
        return None
