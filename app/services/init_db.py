import os
from sqlmodel import Session, select
from app.core.database import create_db_and_tables, engine
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import GlobalConfig

def init_db_and_admin():
    """
    初始化数据库表并检查/创建默认管理员用户
    """
    # 1. 创建数据库表
    create_db_and_tables()
    
    # 2. 自动创建管理员
    # 优先从环境变量获取，否则使用默认配置
    admin_email = os.getenv("ADMIN_EMAIL", GlobalConfig.DEFAULT_ADMIN_EMAIL)
    admin_username = os.getenv("ADMIN_USERNAME", GlobalConfig.DEFAULT_ADMIN_USERNAME)
    admin_password = os.getenv("ADMIN_PASSWORD", GlobalConfig.DEFAULT_ADMIN_PASSWORD)
    
    if admin_email:
        with Session(engine) as session:
            statement = select(User).where(User.email == admin_email)
            existing_user = session.exec(statement).first()
            
            if not existing_user:
                print(f"Initializing admin user: {admin_username} ({admin_email})")
                
                hashed_pwd = get_password_hash(admin_password)
                new_admin = User(
                    uname=admin_username,
                    email=admin_email,
                    hashed_pwd=hashed_pwd
                )
                session.add(new_admin)
                session.commit()
                print(f"Admin user created successfully. Password: {admin_password}")
            else:
                print(f"Admin user check: {existing_user.email} already exists.")
