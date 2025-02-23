from typing import Any
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from src.main import create_application
from starlette import status


# Фикстуры для приложения и асинхронного клиента
@pytest.fixture
def app() -> Any:
    """Возвращает экземпляр FastAPI-приложения."""
    return create_application()


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    app = create_application()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_auth_registration_and_login(async_client: AsyncClient) -> None:
    """
    Тест регистрации и авторизации.
    Проверяется успешная регистрация, отказ при повторной регистрации и
    получение JWT-токена.
    """
    reg_data: dict[str, str] = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "password123",
    }
    reg_response = await async_client.post("/auth/register", json=reg_data)
    assert reg_response.status_code == status.HTTP_201_CREATED
    user_data: dict[str, Any] = reg_response.json()
    assert "id" in user_data

    # Повторная регистрация с тем же email должна вернуть ошибку
    dup_response = await async_client.post("/auth/register", json=reg_data)
    assert dup_response.status_code == status.HTTP_409_CONFLICT

    login_data: dict[str, str] = {
        "email": "testuser@example.com",
        "password": "password123",
    }
    login_response = await async_client.post("/auth/login", json=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    token: str = login_response.json().get("access_token")
    assert token is not None


@pytest.mark.asyncio
async def test_personal_chat(async_client: AsyncClient) -> None:
    """
    Тест создания личного чата между двумя пользователями.
    Проверяется регистрация, логин и создание чата, а также присутствие созданного
    чата в списке.
    """
    alice_data: dict[str, str] = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "password123",
    }
    bob_data: dict[str, str] = {
        "name": "Bob",
        "email": "bob@example.com",
        "password": "password123",
    }

    resp_alice = await async_client.post("/auth/register", json=alice_data)
    resp_bob = await async_client.post("/auth/register", json=bob_data)
    assert resp_alice.status_code == status.HTTP_201_CREATED
    assert resp_bob.status_code == status.HTTP_201_CREATED

    alice = resp_alice.json()
    bob = resp_bob.json()

    login_resp = await async_client.post(
        "/auth/login",
        json={"email": alice_data["email"], "password": alice_data["password"]},
    )
    token: str = login_resp.json()["access_token"]
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}

    chat_resp = await async_client.post(
        "/chats", json={"user_id": bob["id"]}, headers=headers
    )
    assert chat_resp.status_code == status.HTTP_201_CREATED
    chat: dict[str, Any] = chat_resp.json()
    assert chat["type"] == "personal"

    # Проверка списка чатов для пользователя
    chats_resp = await async_client.get("/chats", headers=headers)
    assert chats_resp.status_code == status.HTTP_200_OK
    chats = chats_resp.json()
    assert any(c["id"] == chat["id"] for c in chats)


@pytest.mark.asyncio
async def test_group_chat(async_client: AsyncClient) -> None:
    """
    Тест создания группового чата.
    Проверяется регистрация создателя, логин и успешное создание группы.
    """
    creator_data: dict[str, str] = {
        "name": "GroupCreator",
        "email": "groupcreator@example.com",
        "password": "password123",
    }
    reg_resp = await async_client.post("/auth/register", json=creator_data)
    assert reg_resp.status_code == status.HTTP_201_CREATED

    login_resp = await async_client.post(
        "/auth/login",
        json={"email": creator_data["email"], "password": creator_data["password"]},
    )
    token: str = login_resp.json()["access_token"]
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}

    group_payload: dict[str, Any] = {"title": "Test Group", "member_ids": []}
    group_resp = await async_client.post("/groups", json=group_payload, headers=headers)
    assert group_resp.status_code == status.HTTP_201_CREATED
    group = group_resp.json()
    assert group["title"] == "Test Group"


@pytest.mark.asyncio
async def test_message_history(async_client: AsyncClient) -> None:
    """
    Тест получения истории сообщений.
    Создаются два пользователя, личный чат между ними, а затем проверяется эндпоинт
     истории сообщений.
    """
    user1_data: dict[str, str] = {
        "name": "MsgUser1",
        "email": "msguser1@example.com",
        "password": "password123",
    }
    user2_data: dict[str, str] = {
        "name": "MsgUser2",
        "email": "msguser2@example.com",
        "password": "password123",
    }

    r1 = await async_client.post("/auth/register", json=user1_data)
    r2 = await async_client.post("/auth/register", json=user2_data)
    assert r1.status_code == status.HTTP_201_CREATED
    assert r2.status_code == status.HTTP_201_CREATED
    user1 = r1.json()
    user2 = r2.json()

    login_resp = await async_client.post(
        "/auth/login",
        json={"email": user1_data["email"], "password": user1_data["password"]},
    )
    token: str = login_resp.json()["access_token"]
    headers: dict[str, str] = {"Authorization": f"Bearer {token}"}

    chat_resp = await async_client.post(
        "/chats", json={"user_id": user2["id"]}, headers=headers
    )
    assert chat_resp.status_code == status.HTTP_201_CREATED
    chat = chat_resp.json()

    history_resp = await async_client.get(
        f"/messages/history/{chat['id']}", headers=headers
    )
    assert history_resp.status_code == status.HTTP_200_OK
    history = history_resp.json()
    assert isinstance(history, list)


def test_websocket_connection() -> None:
    """
    Тест WebSocket-соединения с использованием TestClient.
    Регистрируется пользователь, выполняется логин и устанавливается соединение с /ws.
    Затем отправляется сообщение (например, join_chat) и проверяется, что получен
     корректный ответ.
    """
    app = create_application()
    client = TestClient(app)

    reg_data: dict[str, str] = {
        "name": "WsUser",
        "email": "wsuser@example.com",
        "password": "password123",
    }
    reg_resp = client.post("/auth/register", json=reg_data)
    assert reg_resp.status_code == status.HTTP_201_CREATED

    login_resp = client.post(
        "/auth/login",
        json={"email": reg_data["email"], "password": reg_data["password"]},
    )
    token: str = login_resp.json()["access_token"]

    # Подключаемся к WebSocket с передачей токена через query-параметр
    with client.websocket_connect(f"/ws?token={token}") as websocket:
        test_payload: dict[str, str] = {
            "action": "join_chat",
            "chat_id": "00000000-0000-0000-0000-000000000000",
        }
        websocket.send_json(test_payload)
        received = websocket.receive_json()
        assert isinstance(received, dict)
