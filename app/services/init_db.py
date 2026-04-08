import os
import json
import logging
from sqlmodel import Session, select
from app.core.database import create_db_and_tables, engine
from app.models.user import User, UserRole
from app.models.chat_message import ChatMessage
from app.models.favorite import Favorite
from app.models.todo import TodoItem
from app.models.rag_usage import RagUsage
from app.models.agent_conversation import AgentConversation
from app.models.agent_message import AgentMessage
from app.models.agent_memory import AgentMemory
from app.models.policy_document import PolicyDocument, DocStatus
from app.models.opinion import Opinion, OpinionType
from app.core.security import get_password_hash
from app.core.config import GlobalConfig

logger = logging.getLogger(__name__)

def init_db_and_admin():
    # 1. 创建数据库表
    create_db_and_tables()

    for path in (
        GlobalConfig.AVATAR_UPLOAD_DIR,
        GlobalConfig.DOCS_UPLOAD_DIR,
        GlobalConfig.IMAGES_UPLOAD_DIR,
        GlobalConfig.CHAT_EXPORT_DIR,
        GlobalConfig.LOG_DIR,
        GlobalConfig.MAIL_OUTBOX_DIR,
        GlobalConfig.KNOWLEDGE_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)

    # 2. 迁移旧库：补充新列
    from sqlalchemy import text
    with engine.connect() as conn:
        for sql in [
            "ALTER TABLE user ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0",
            "ALTER TABLE user ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT 0",
            "ALTER TABLE user ADD COLUMN email_verification_code VARCHAR",
            "ALTER TABLE user ADD COLUMN email_verification_sent_at DATETIME",
            "ALTER TABLE user ADD COLUMN role VARCHAR NOT NULL DEFAULT 'normal'",
            "ALTER TABLE chatmessage ADD COLUMN source_chat_id INTEGER REFERENCES chatmessage(id)",
            "ALTER TABLE chatmessage ADD COLUMN session_json_path VARCHAR",
            "ALTER TABLE agentmemory ADD COLUMN updated_time DATETIME",
            "ALTER TABLE policydocument ADD COLUMN view_count INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE policydocument ADD COLUMN like_count INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE user ADD COLUMN last_ip VARCHAR",
            "ALTER TABLE user ADD COLUMN profession VARCHAR",
        ]:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception:
                pass

    # 3. 自动创建/修复管理员
    admin_email = os.getenv("ADMIN_EMAIL", GlobalConfig.DEFAULT_ADMIN_EMAIL)
    admin_username = os.getenv("ADMIN_USERNAME", GlobalConfig.DEFAULT_ADMIN_USERNAME)
    admin_password = os.getenv("ADMIN_PASSWORD", GlobalConfig.DEFAULT_ADMIN_PASSWORD)

    if not admin_email:
        return

    with Session(engine) as session:
        existing_user = session.exec(select(User).where(User.email == admin_email)).first()

        if existing_user:
            if existing_user.role != UserRole.admin:
                existing_user.role = UserRole.admin
                existing_user.email_verified = True
                session.add(existing_user)
                session.commit()
                print(f"Migrated role to admin for {existing_user.email}")
            else:
                print(f"Admin user check: {existing_user.email} already exists.")
            if not existing_user.email_verified:
                existing_user.email_verified = True
                session.add(existing_user)
                session.commit()
        else:
            print(f"Initializing admin user: {admin_username} ({admin_email})")
            new_admin = User(
                uname=admin_username,
                email=admin_email,
                hashed_pwd=get_password_hash(admin_password),
                role=UserRole.admin,
                email_verified=True,
            )
            session.add(new_admin)
            session.commit()
            session.refresh(new_admin)
            print(f"Admin user created successfully. Password: {admin_password}")
            import_admin_original_data(session, new_admin.uid)
            seed_demo_data(session, new_admin.uid)


def import_admin_original_data(session: Session, admin_uid: int):
    """从项目根目录的 admin_original_data.json 导入初始测试数据"""
    data_file_path = GlobalConfig.PROJECT_ROOT / "admin_original_data.json"
    if not data_file_path.exists():
        print(f"No original data file found at {data_file_path}. Skipping initial data import.")
        return
    try:
        with open(data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Importing {len(data)} initial records for admin...")
        for item in data:
            chat_analysis = item.get("chat_analysis", "{}")
            if isinstance(chat_analysis, dict):
                chat_analysis = json.dumps(chat_analysis, ensure_ascii=False)
            msg = ChatMessage(
                user_id=admin_uid,
                original_text=item.get("original_text", ""),
                target_audience=item.get("target_audience"),
                handling_matter=item.get("handling_matter"),
                time_deadline=item.get("time_deadline"),
                location_entrance=item.get("location_entrance"),
                required_materials=item.get("required_materials"),
                handling_process=item.get("handling_process"),
                precautions=item.get("precautions"),
                risk_warnings=item.get("risk_warnings"),
                original_text_mapping=item.get("original_text_mapping"),
                chat_analysis=chat_analysis
            )
            session.add(msg)
        session.commit()
        print("Initial data imported successfully.")
    except Exception as e:
        print(f"Failed to import initial data: {e}")


def seed_demo_data(session: Session, admin_uid: int):
    """插入演示用政务文件和民意评议数据（仅首次初始化时调用）"""
    from datetime import datetime

    # 创建一个演示认证主体用户
    certified_user = User(
        uname="示范政务局",
        email="demo_certified@gov.example.com",
        hashed_pwd=get_password_hash("demo123456"),
        role=UserRole.certified,
        email_verified=True,
    )
    session.add(certified_user)
    session.commit()
    session.refresh(certified_user)

    docs_data = [
        ("关于推进数字政府建设的实施意见", "数字化", "数字政府,政务服务,数据共享",
         "为深入贯彻落实党中央、国务院关于数字中国建设的决策部署，加快推进数字政府建设，提升政府治理体系和治理能力现代化水平，现提出以下实施意见：一、总体要求；二、主要任务；三、保障措施。"),
        ("2026年惠企政策汇编", "惠企政策", "企业,补贴,减税,营商环境",
         "为进一步优化营商环境，支持企业高质量发展，现将2026年度主要惠企政策汇编如下，涵盖税收优惠、资金补贴、用地保障、人才引进等多个方面。"),
        ("关于加强基层医疗卫生服务能力建设的通知", "医疗卫生", "医疗,基层,卫生,健康",
         "为切实加强基层医疗卫生服务能力，保障人民群众就近享有公平可及、系统连续的基本医疗卫生服务，现就有关事项通知如下。"),
        ("乡村振兴重点帮扶县产业发展支持政策", "乡村振兴", "农村,产业,扶贫,振兴",
         "为巩固拓展脱贫攻坚成果，全面推进乡村振兴，加大对重点帮扶县产业发展支持力度，制定本政策。主要包括：产业项目支持、技术帮扶、市场对接等措施。"),
        ("关于规范网络直播营销活动的管理办法", "市场监管", "直播,电商,网络,监管",
         "为规范网络直播营销活动，维护消费者合法权益和社会公共利益，促进网络直播营销健康有序发展，依据相关法律法规，制定本办法。"),
    ]

    doc_ids = []
    for title, category, tags, content in docs_data:
        doc = PolicyDocument(
            title=title,
            content=content,
            category=category,
            tags=tags,
            uploader_id=certified_user.uid,
            status=DocStatus.approved,
            view_count=0,
            like_count=0,
            reviewed_time=datetime.now(),
        )
        session.add(doc)
        session.commit()
        session.refresh(doc)
        doc_ids.append(doc.id)

    opinions_data = [
        (doc_ids[0], admin_uid, OpinionType.review, "政策方向很好，数字政府建设确实能提升办事效率，希望尽快落地。", 5),
        (doc_ids[0], admin_uid, OpinionType.message, "请问数字政务平台什么时候上线？我们企业很期待。", None),
        (doc_ids[1], admin_uid, OpinionType.review, "惠企政策力度很大，减税降费措施对中小企业帮助明显。", 4),
        (doc_ids[1], admin_uid, OpinionType.correction, "第三条补贴申请材料清单中，营业执照应为最新版本，原文表述不够清晰。", None),
        (doc_ids[2], admin_uid, OpinionType.review, "基层医疗建设很重要，农村地区看病难问题确实需要重视。", 5),
        (doc_ids[2], admin_uid, OpinionType.message, "我们村卫生室设备老化，希望能纳入本次支持范围。", None),
        (doc_ids[3], admin_uid, OpinionType.review, "乡村振兴政策落地情况参差不齐，建议加强监督考核机制。", 3),
        (doc_ids[4], admin_uid, OpinionType.review, "直播监管办法出台及时，有效规范了市场秩序。", 4),
        (doc_ids[4], admin_uid, OpinionType.correction, "第八条处罚标准建议与电商法保持一致，避免执法口径不统一。", None),
    ]

    for doc_id, user_id, op_type, content, rating in opinions_data:
        op = Opinion(
            doc_id=doc_id,
            user_id=user_id,
            opinion_type=op_type,
            content=content,
            rating=rating,
            like_count=0,
        )
        session.add(op)

    session.commit()
    print("Demo data seeded successfully.")

    """
    从项目根目录的 admin_original_data.json 导入初始测试数据
    """
    data_file_path = GlobalConfig.PROJECT_ROOT / "admin_original_data.json"
    
    if not data_file_path.exists():
        print(f"No original data file found at {data_file_path}. Skipping initial data import.")
        return
        
    try:
        with open(data_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Importing {len(data)} initial records for admin...")
        for item in data:
            # 确保 chat_analysis 是字符串
            chat_analysis = item.get("chat_analysis", "{}")
            if isinstance(chat_analysis, dict):
                chat_analysis = json.dumps(chat_analysis, ensure_ascii=False)
                
            msg = ChatMessage(
                user_id=admin_uid,
                original_text=item.get("original_text", ""),
                target_audience=item.get("target_audience"),
                handling_matter=item.get("handling_matter"),
                time_deadline=item.get("time_deadline"),
                location_entrance=item.get("location_entrance"),
                required_materials=item.get("required_materials"),
                handling_process=item.get("handling_process"),
                precautions=item.get("precautions"),
                risk_warnings=item.get("risk_warnings"),
                original_text_mapping=item.get("original_text_mapping"),
                chat_analysis=chat_analysis
            )
            session.add(msg)
            
        session.commit()
        print("Initial data imported successfully.")
    except Exception as e:
        print(f"Failed to import initial data: {e}")
