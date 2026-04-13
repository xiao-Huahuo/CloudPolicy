from typing import Literal, Optional

from sqlmodel import SQLModel


AuthPurpose = Literal["login", "register", "reset_password", "bind_phone", "bind_email"]
AuthChannel = Literal["phone", "email"]


class CaptchaResponse(SQLModel):
    captcha_id: str
    svg: str
    expires_in: int


class PhoneCodeSendRequest(SQLModel):
    phone: str
    purpose: AuthPurpose
    captcha_id: Optional[str] = None
    captcha_answer: Optional[str] = None


class EmailCodeSendRequest(SQLModel):
    email: str
    purpose: Literal["bind_email"]
    captcha_id: str
    captcha_answer: str


class CodeDispatchResponse(SQLModel):
    message: str
    expires_in: int
    retry_after: int
    delivery_channel: str = "sandbox"
    preview_code: Optional[str] = None


class PhoneRegisterRequest(SQLModel):
    uname: Optional[str] = None
    phone: str
    code: str
    pwd: Optional[str] = None


class PhoneLoginRequest(SQLModel):
    phone: str
    code: str


class PasswordLoginRequest(SQLModel):
    identity: str
    password: str


class RecoveryOptionsRequest(SQLModel):
    identifier: str


class RecoveryMethod(SQLModel):
    channel: AuthChannel
    masked_target: str
    label: str


class RecoveryOptionsResponse(SQLModel):
    identifier: str
    methods: list[RecoveryMethod]


class RecoverySendRequest(SQLModel):
    identifier: str
    channel: AuthChannel
    captcha_id: str
    captcha_answer: str


class PasswordResetRequest(SQLModel):
    identifier: str
    channel: AuthChannel
    code: str
    new_password: str
    confirm_password: str


class BindPhoneRequest(SQLModel):
    phone: str
    code: str


class BindEmailRequest(SQLModel):
    email: str
    code: str


class PasswordSetRequest(SQLModel):
    new_password: str
    confirm_password: str


class PasswordChangeRequest(SQLModel):
    current_password: str
    new_password: str
    confirm_password: str
