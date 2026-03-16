
from pathlib import Path
class GlobalConfig:
    DEFAULT_ADMIN_PASSWORD = "111111"
    DEFAULT_ADMIN_USERNAME="admin"
    DEFAULT_ADMIN_EMAIL="unknown@email.com"
    DEFAULT_ADMIN_PHONE=None

    # 数据库配置
    SQLITE_DATABASE_FILENAME = "database.db"  # 数据库文件名
    BASE_DIR = Path(__file__).resolve().parent.parent# 获取当前文件的父目录的父目录，即项目根目录

    # JWT配置
    # 常量,应该从环境变量获取,此处开发使用
    SECRET_KEY = "09d25e094faa6ca2556c81"  # 密钥
    ALGORITHM = "HS256"  # 加密算法,采用Hash256
    ACCESS_TOKEN_EXPIRE_DAYS = 30  # token有效期为30天