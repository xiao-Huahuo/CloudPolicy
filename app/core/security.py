from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext

from app.core.config import GlobalConfig

# 尝试更换哈希算法，解决 bcrypt 可能的兼容性问题
# 使用 pbkdf2_sha256，它是纯 Python 支持良好的算法
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# 加密密码
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 生成token
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    生成 JWT Access Token
    :param subject: 用户uid
    :param expires_delta: 过期时间段 (可选)
    :return: 加密后的 Token 字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=GlobalConfig.ACCESS_TOKEN_EXPIRE_DAYS)

    # 准备载荷 (Payload)
    # sub (Subject) 是 JWT 标准字段，存放用户 ID
    # exp (Expiration Time) 是 JWT 标准字段，存放过期时间
    to_encode = {"exp": expire, "sub": str(subject)}

    # 编码,生成 Token 并返回
    encoded_jwt = jwt.encode(to_encode, GlobalConfig.SECRET_KEY, algorithm=GlobalConfig.ALGORITHM)
    return encoded_jwt
