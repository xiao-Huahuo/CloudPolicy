import logging
import secrets
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, Optional

from app.core.config import GlobalConfig
from app.core.security import create_email_verification_token
from app.models.user import User
from app.services.auth_identity_service import get_public_email


logger = logging.getLogger(__name__)


def is_email_enabled() -> bool:
    return all(
        [
            GlobalConfig.SMTP_HOST,
            GlobalConfig.SMTP_USERNAME,
            GlobalConfig.SMTP_PASSWORD,
            GlobalConfig.SMTP_SENDER,
        ]
    )


def generate_verification_code() -> str:
    return "".join(
        str(secrets.randbelow(10))
        for _ in range(GlobalConfig.EMAIL_VERIFICATION_CODE_LENGTH)
    )


def _deliver_email(message: EmailMessage) -> bool:
    if not is_email_enabled():
        return False

    try:
        if GlobalConfig.SMTP_USE_SSL:
            with smtplib.SMTP_SSL(
                GlobalConfig.SMTP_HOST, GlobalConfig.SMTP_PORT, timeout=10
            ) as server:
                server.login(GlobalConfig.SMTP_USERNAME, GlobalConfig.SMTP_PASSWORD)
                server.send_message(message)
        else:
            with smtplib.SMTP(
                GlobalConfig.SMTP_HOST, GlobalConfig.SMTP_PORT, timeout=10
            ) as server:
                if GlobalConfig.SMTP_USE_TLS:
                    server.starttls()
                server.login(GlobalConfig.SMTP_USERNAME, GlobalConfig.SMTP_PASSWORD)
                server.send_message(message)
        return True
    except Exception as exc:
        logger.exception("邮件发送失败: %s", exc)
        return False


def _write_preview(recipient: str, subject: str, content: str) -> Path:
    GlobalConfig.MAIL_OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    filename = (
        GlobalConfig.MAIL_OUTBOX_DIR
        / f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{recipient.replace('@', '_at_')}.txt"
    )
    filename.write_text(
        f"TO: {recipient}\nSUBJECT: {subject}\n\n{content}",
        encoding="utf-8",
    )
    logger.info("邮件预览已写入: %s", filename)
    return filename


def send_email(
    recipient: str,
    subject: str,
    content: str,
    html_content: Optional[str] = None,
) -> dict:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{GlobalConfig.SMTP_SENDER_NAME} <{GlobalConfig.SMTP_SENDER}>"
    message["To"] = recipient
    message.set_content(content)

    if html_content:
        message.add_alternative(html_content, subtype="html")

    if _deliver_email(message):
        logger.info("邮件已发送至 %s, subject=%s", recipient, subject)
        return {"delivery_channel": "email", "preview_code": None}

    preview_path = _write_preview(recipient, subject, content)
    return {"delivery_channel": "preview", "preview_path": str(preview_path)}


def send_verification_email(user: User) -> dict:
    code = user.email_verification_code or ""
    token = create_email_verification_token(
        user.email,
        code,
        GlobalConfig.EMAIL_VERIFICATION_EXPIRE_MINUTES,
    )
    verify_url = f"{GlobalConfig.PUBLIC_BASE_URL}/user/verify-email-link?token={token}"
    content = (
        f"{user.uname}，您好：\n\n"
        "请点击下面的链接完成邮箱验证：\n"
        f"{verify_url}\n\n"
        f"该链接 {GlobalConfig.EMAIL_VERIFICATION_EXPIRE_MINUTES} 分钟内有效。\n"
        "如非本人操作，请忽略此邮件。"
    )
    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
      <p>{user.uname}，您好：</p>
      <p>请点击下面按钮完成邮箱验证：</p>
      <p>
        <a href="{verify_url}" style="display:inline-block;padding:10px 16px;background:#c0392b;color:#fff;text-decoration:none;border-radius:4px;">验证邮箱</a>
      </p>
      <p style="font-size:12px;color:#666;">该链接 {GlobalConfig.EMAIL_VERIFICATION_EXPIRE_MINUTES} 分钟内有效。</p>
      <p style="font-size:12px;color:#999;">如非本人操作，请忽略此邮件。</p>
    </div>
    """
    result = send_email(user.email, "ClearNotify 邮箱验证", content, html_content=html_content)
    if result["delivery_channel"] == "preview":
        result["preview_code"] = code
    return result


def send_code_email(recipient: str, code: str, purpose: str) -> dict:
    subject_map = {
        "reset_password": "ClearNotify 密码重置验证码",
        "bind_email": "ClearNotify 邮箱绑定验证码",
        "register": "ClearNotify 邮箱注册验证码",
    }
    purpose_label_map = {
        "reset_password": "重置密码",
        "bind_email": "绑定邮箱",
        "register": "注册验证",
    }
    subject = subject_map.get(purpose, "ClearNotify 验证码")
    purpose_label = purpose_label_map.get(purpose, "身份验证")
    content = (
        f"您好：\n\n"
        f"您正在进行{purpose_label}。\n"
        f"本次验证码为：{code}\n\n"
        f"验证码将在 {GlobalConfig.AUTH_CODE_EXPIRE_MINUTES} 分钟后失效。"
    )
    html_content = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
      <p>您好：</p>
      <p>您正在进行{purpose_label}。</p>
      <p style="font-size: 18px; font-weight: bold; letter-spacing: 2px;">{code}</p>
      <p style="font-size: 12px; color: #666;">验证码将在 {GlobalConfig.AUTH_CODE_EXPIRE_MINUTES} 分钟后失效。</p>
    </div>
    """
    result = send_email(recipient, subject, content, html_content=html_content)
    if result["delivery_channel"] == "preview":
        result["preview_code"] = code
    return result


def send_upgrade_request_email(requester: User, admins: Iterable[User]) -> None:
    for admin in admins:
        recipient = get_public_email(admin.email)
        if not recipient:
            continue
        send_email(
            recipient,
            "ClearNotify 权限升级申请",
            (
                f"用户 {requester.uname}（UID: {requester.uid}，邮箱: {requester.email}）"
                " 提交了管理员权限申请，请尽快在后台处理。"
            ),
        )


def send_role_change_email(user: User, role_name: str) -> None:
    recipient = get_public_email(user.email)
    if not recipient:
        return
    send_email(
        recipient,
        "ClearNotify 权限变更通知",
        f"您好，您的账户权限已变更为：{role_name}。",
    )
