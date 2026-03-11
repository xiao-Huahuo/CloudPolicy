from sqlmodel import SQLModel

#登录逻辑: 前端发送必要字段,后端验证密码,返回token
# 响应给前端的 Token 信息
class Token(SQLModel):
    access_token: str
    token_type: str

# 解密 Token 后得到的数据（通常只包含 sub/用户ID）
class TokenPayload(SQLModel):
    sub: int | None = None  #存放用户的uid