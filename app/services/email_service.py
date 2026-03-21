import logging
import secrets
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, Optional

from app.core.config import GlobalConfig
from app.models.user import User


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
    content = (
        f"{user.uname}，您好：\n\n"
        f"您的 ClearNotify 邮箱验证码为：{code}\n"
        f"验证码 {GlobalConfig.EMAIL_VERIFICATION_EXPIRE_MINUTES} 分钟内有效。\n"
        "若非本人操作，请忽略此邮件。"
    )
    result = send_email(user.email, "ClearNotify 邮箱验证", content)
    if result["delivery_channel"] == "preview":
        result["preview_code"] = code
    return result


def send_upgrade_request_email(requester: User, admins: Iterable[User]) -> None:
    for admin in admins:
        send_email(
            admin.email,
            "ClearNotify 权限升级申请",
            (
                f"用户 {requester.uname}（UID: {requester.uid}，邮箱: {requester.email}）"
                " 提交了管理员权限申请，请尽快在后台处理。"
            ),
        )


def send_role_change_email(user: User, role_name: str) -> None:
    send_email(
        user.email,
        "ClearNotify 权限变更通知",
        f"您好，您的账户权限已变更为：{role_name}。",
    )
