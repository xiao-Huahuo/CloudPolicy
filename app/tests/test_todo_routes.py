from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.api.deps import get_current_user
from app.api.routes import todo
from app.models.chat_message import ChatMessage
from app.models.favorite import Favorite
from app.models.settings import Settings
from app.models.stats_analysis import StatsAnalysis
from app.models.todo import TodoItem
from app.models.user import User

_RELATED_MODELS = (ChatMessage, Favorite, Settings, StatsAnalysis, TodoItem)


def make_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(
            uname="todo-user",
            email="todo-user@example.com",
            hashed_pwd="not-used",
            email_verified=True,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.uid

    def get_test_session():
        with Session(engine) as session:
            yield session

    def get_test_user():
        with Session(engine) as session:
            current_user = session.get(User, user_id)
            assert current_user is not None
            return current_user

    app = FastAPI()
    app.dependency_overrides[todo.get_session] = get_test_session
    app.dependency_overrides[get_current_user] = get_test_user
    app.include_router(todo.router, prefix="/todo")
    return TestClient(app)


def test_create_todo_returns_created_fields(monkeypatch):
    monkeypatch.setattr(todo.history_service, "record_todo_event", lambda *args, **kwargs: None)
    client = make_client()

    response = client.post("/todo/", params={"title": "测试待办", "detail": "点击调试", "deadline": "2026-05-10"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "测试待办"
    assert data["detail"] == "点击调试"
    assert data["deadline"] == "2026-05-10"
    assert data["is_done"] is False
    assert data["is_confirmed"] is True
    assert data["id"]


def test_toggle_todo_returns_updated_fields(monkeypatch):
    monkeypatch.setattr(todo.history_service, "record_todo_event", lambda *args, **kwargs: None)
    client = make_client()
    created = client.post("/todo/", params={"title": "切换状态"}).json()

    response = client.patch(f"/todo/{created['id']}/toggle")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["title"] == "切换状态"
    assert data["is_done"] is True
