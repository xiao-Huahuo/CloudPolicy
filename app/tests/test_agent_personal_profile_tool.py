from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.agent_plugin.agent import tools as agent_tools
from app.models.chat_message import ChatMessage
from app.models.favorite import Favorite
from app.models.settings import Settings
from app.models.stats_analysis import StatsAnalysis
from app.models.todo import TodoItem
from app.models.user import User, UserRole
from app.services.agent_tool_services.catalog import TOOL_CATALOG
from app.services.agent_tool_services.personal_tool_service import get_personal_profile_payload


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_personal_profile_payload_includes_user_and_settings():
    with make_session() as session:
        user = User(
            uname="profile-user",
            email="profile-user@example.com",
            hashed_pwd="not-used",
            role=UserRole.certified,
            profession="高校教师",
            avatar_url="/media/avatars/user_1_avatar.png",
            phone="13900002222",
            login_phone="13900002222",
            email_verified=True,
            phone_verified=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        session.add(
            Settings(
                user_id=user.uid,
                default_audience="teacher",
                theme_mode="dark",
                color_scheme="wine-coral",
            )
        )
        session.commit()

        payload = get_personal_profile_payload(session, user.uid)

        item = payload["item"]
        assert item["user"]["uname"] == "profile-user"
        assert item["user"]["role"] == "certified"
        assert item["user"]["profession"] == "高校教师"
        assert item["settings"]["theme_mode"] == "dark"
        assert item["personal_profile"]["verified_contacts"] == ["email", "phone"]


def test_personal_profile_tool_is_registered():
    tool_names = {tool.name for tool in agent_tools.tools}
    catalog_names = {item["name"] for item in TOOL_CATALOG}

    assert "get_personal_profile" in tool_names
    assert "get_personal_profile" in catalog_names
