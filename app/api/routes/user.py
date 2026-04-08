from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.user import User, UserRole
from app.schemas.user import *
from app.core.security import get_password_hash
from app.api.deps import get_current_user
from app.core.config import GlobalConfig
from app.core.security import decode_email_verification_token
from app.services import email_service

# 创建路由器
router = APIRouter()  #在main中被登记为"/user"

#用户注册
@router.post("/", response_model=UserRegisterResponse) #最后返回字段是基于响应DTO(UserRead)过滤后的
def create_user(user: UserCreate, session: Session = Depends(get_session)): #接收注册DTO(UserCreate)
    """
    创建新用户
    :param user:
    :param session:
    :return:
    """
    existing_email = session.exec(select(User).where(User.email == user.email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    existing_name = session.exec(select(User).where(User.uname == user.uname)).first()
    if existing_name:
        raise HTTPException(status_code=400, detail="该用户名已存在")

    hashed_pwd = get_password_hash(user.pwd)
    verification_code = email_service.generate_verification_code()

    db_user = User.model_validate(
        user,
        update={
            "hashed_pwd": hashed_pwd,
            "email_verified": False,
            "email_verification_code": verification_code,
            "email_verification_sent_at": datetime.now(),
        },
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    delivery = email_service.send_verification_email(db_user)
    return UserRegisterResponse(
        user=UserRead(
            uid=db_user.uid,
            uname=db_user.uname,
            email=db_user.email,
            phone=db_user.phone,
            avatar_url=db_user.avatar_url,
            is_admin=db_user.is_admin,
            created_time=db_user.created_time,
            last_login=db_user.last_login,
            email_verified=db_user.email_verified,
        ),
        verification_required=True,
        delivery_channel=delivery["delivery_channel"],
        preview_code=delivery.get("preview_code"),
    )


@router.post("/verify-email")
def verify_email(
    payload: EmailVerificationRequest,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.email_verified:
        return {"message": "邮箱已验证"}
    if not user.email_verification_code or not user.email_verification_sent_at:
        raise HTTPException(status_code=400, detail="验证码不存在，请重新发送")
    if datetime.now() - user.email_verification_sent_at > timedelta(
        minutes=GlobalConfig.EMAIL_VERIFICATION_EXPIRE_MINUTES
    ):
        raise HTTPException(status_code=400, detail="验证码已过期，请重新发送")
    if payload.code != user.email_verification_code:
        raise HTTPException(status_code=400, detail="验证码错误")

    user.email_verified = True
    user.email_verification_code = None
    user.email_verification_sent_at = None
    session.add(user)
    session.commit()
    return {"message": "邮箱验证成功"}


@router.get("/verify-email-link", response_class=HTMLResponse)
def verify_email_link(
    token: str,
    session: Session = Depends(get_session),
):
    payload = decode_email_verification_token(token)
    email = payload.get("sub")
    code = payload.get("code")
    if not email or not code:
        return HTMLResponse(
            "<h2>验证失败：链接无效</h2>",
            status_code=400,
        )

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return HTMLResponse("<h2>验证失败：用户不存在</h2>", status_code=404)

    if user.email_verified:
        return HTMLResponse(
            f"<h2>邮箱已验证</h2><p><a href=\"{GlobalConfig.FRONTEND_BASE_URL}\">返回应用</a></p>",
            status_code=200,
        )

    if not user.email_verification_code or not user.email_verification_sent_at:
        return HTMLResponse("<h2>验证失败：验证码不存在</h2>", status_code=400)

    if datetime.now() - user.email_verification_sent_at > timedelta(
        minutes=GlobalConfig.EMAIL_VERIFICATION_EXPIRE_MINUTES
    ):
        return HTMLResponse("<h2>验证失败：链接已过期</h2>", status_code=400)

    if code != user.email_verification_code:
        return HTMLResponse("<h2>验证失败：链接无效</h2>", status_code=400)

    user.email_verified = True
    user.email_verification_code = None
    user.email_verification_sent_at = None
    session.add(user)
    session.commit()
    return HTMLResponse(
        f"""
        <div style="font-family: Arial, sans-serif; line-height:1.6;">
          <h2>邮箱验证成功</h2>
          <p>您可以返回应用继续登录。</p>
          <p><a href="{GlobalConfig.FRONTEND_BASE_URL}">返回应用</a></p>
        </div>
        """,
        status_code=200,
    )


@router.post("/resend-verification")
def resend_verification_email(
    payload: EmailVerificationResendRequest,
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.email_verified:
        return {"message": "邮箱已验证", "delivery_channel": "none"}

    user.email_verification_code = email_service.generate_verification_code()
    user.email_verification_sent_at = datetime.now()
    session.add(user)
    session.commit()
    session.refresh(user)

    delivery = email_service.send_verification_email(user)
    return {
        "message": "验证码已重新发送",
        "delivery_channel": delivery["delivery_channel"],
        "preview_code": delivery.get("preview_code"),
    }

#查询个人信息
#Header格式:  Authorization: bearer <你的Access Token>
@router.get("/me",response_model=UserRead)
def get_user(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的个人信息
    :param current_user:
    :return:
    """
    return current_user

#修改个人信息(部分更新)
@router.patch("/me",response_model=UserRead)
def update_user(user_in:UserUpdate,session:Session=Depends(get_session),current_user: User = Depends(get_current_user)):
    """
    更新当前登录用户的个人信息
    :param user_in: 更新的用户信息
    :param session:
    :param current_user:
    :return:
    """
    # 1. 提取需要更新的数据的字典 (排除None字段)
    update_data = user_in.model_dump(exclude_unset=True)

    # 2. 如果包含密码，需要特殊处理
    if "pwd" in update_data:
        # 加密新密码
        hashed_password = get_password_hash(update_data["pwd"])
        # 从更新数据中移除明文密码
        del update_data["pwd"]
        # 添加加密后的密码字段
        update_data["hashed_pwd"] = hashed_password

    # 3. 根据字典更新当前用户对象
    current_user.sqlmodel_update(update_data)

    # 4. 保存到数据库
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    # 5. 返回更新后的用户
    return current_user


@router.post("/request-upgrade")
def request_permission_upgrade(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """普通用户申请升级为认证主体，认证主体申请升级为管理员（向所有管理员发送通知）"""
    if current_user.role == UserRole.admin:
        raise HTTPException(status_code=400, detail="您已经是管理员")
    admins = session.exec(select(User).where(User.role == UserRole.admin)).all()
    if not admins:
        raise HTTPException(status_code=404, detail="暂无管理员可处理申请")
    email_service.send_upgrade_request_email(current_user, admins)
    return {"message": f"申请已提交，已通知 {len(admins)} 位管理员"}


@router.post("/request-downgrade")
def request_permission_downgrade(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """认证主体或管理员申请降级为普通用户"""
    if current_user.role == UserRole.normal:
        raise HTTPException(status_code=400, detail="您已经是普通用户")
    current_user.role = UserRole.normal
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    email_service.send_role_change_email(current_user, "普通用户")
    return {"message": "已成功降级为普通用户"}
