from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from app.api.routes import auth
from app.models.chat_message import ChatMessage
from app.models.favorite import Favorite
from app.models.settings import Settings
from app.models.stats_analysis import StatsAnalysis
from app.models.todo import TodoItem
from app.models.user import User
from app.services import auth_challenge_service

_RELATED_MODELS = (ChatMessage, Favorite, Settings, StatsAnalysis, TodoItem)


def make_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_test_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    app.dependency_overrides[auth.get_session] = get_test_session
    app.include_router(auth.router, prefix="/auth")
    return TestClient(app), engine


def test_unregistered_phone_can_use_one_click_login(monkeypatch):
    client, engine = make_client()
    phone = "13900001111"

    async def no_sleep(_seconds):
        return None

    auth_challenge_service._memory_store.clear()
    monkeypatch.setattr(auth.email_service, "generate_verification_code", lambda: "246810")
    monkeypatch.setattr(auth.asyncio, "sleep", no_sleep)

    send_response = client.post("/auth/phone/send-code", json={"phone": phone, "purpose": "login"})

    assert send_response.status_code == 200
    assert send_response.json()["preview_code"] == "246810"

    login_response = client.post("/auth/phone/login", json={"phone": phone, "code": "246810"})

    assert login_response.status_code == 200
    assert login_response.json()["access_token"]
    with Session(engine) as session:
        user = session.exec(select(User).where(User.login_phone == phone)).one()
        assert user.phone_verified is True
        assert user.password_login_enabled is False
        assert user.last_login_method == "phone_code"
