from datetime import timedelta, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.config import GlobalConfig
from app.core.database import get_session
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User
from app.schemas.token import Token

router = APIRouter()


# 用户登录
@router.post("/", response_model=Token)
def login_access_token(
        session: Session = Depends(get_session),
        form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2兼容的access-token验证登录接口
    """
    print(f"Login attempt: username={form_data.username}")
    print(f"Received password repr: {repr(form_data.password)}")  # 调试：打印 repr

    # 根据用户名查找用户
    statement = select(User).where(User.uname == form_data.username)
    user = session.exec(statement).first()

    if not user:
        print("User not found by uname")

    if user:
        print(f"User found: {user.uname}")
        print(f"Stored hash: '{user.hashed_pwd}'")

        is_valid = verify_password(form_data.password, user.hashed_pwd)
        print(f"Password valid: {is_valid}")

        if not is_valid:
            # 测试本地哈希
            test_hash = get_password_hash(form_data.password)
            print(f"Test hash: {test_hash}")
            print(f"Test verify: {verify_password(form_data.password, test_hash)}")

    if not user or not verify_password(form_data.password, user.hashed_pwd):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    user.last_login = datetime.now()
    session.add(user)
    session.commit()

    access_token_expires = timedelta(days=GlobalConfig.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        subject=user.uid, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")