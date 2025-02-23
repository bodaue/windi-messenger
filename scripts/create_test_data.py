import asyncio


from src.core.di.database import async_session_maker
from src.models.user import User
from src.models.chat import Chat, ChatMember, ChatType
from src.models.group import Group
from src.models.message import Message

from src.repositories.user import UserRepository
from src.repositories.chat import ChatRepository
from src.repositories.chat_member import ChatMemberRepository
from src.repositories.group import GroupRepository
from src.repositories.message import MessageRepository
from src.repositories.message_read_state import MessageReadStateRepository

from src.services.password_hasher import PasswordService


async def create_test_data() -> None:
    async with async_session_maker() as session:
        # Инициализируем репозитории и сервисы
        user_repo = UserRepository(session)
        chat_repo = ChatRepository(session)
        chat_member_repo = ChatMemberRepository(session)
        group_repo = GroupRepository(session)
        message_repo = MessageRepository(session)
        message_read_state_repo = MessageReadStateRepository(session)
        password_service = PasswordService()

        # Создаем тестовых пользователей
        users_data = [
            {"name": "Alice", "email": "alice@example.com", "password": "password123"},
            {"name": "Bob", "email": "bob@example.com", "password": "password123"},
            {
                "name": "Charlie",
                "email": "charlie@example.com",
                "password": "password123",
            },
            {"name": "David", "email": "david@example.com", "password": "password123"},
        ]

        users = {}
        for data in users_data:
            hashed = password_service.get_password_hash(data["password"])
            user = User(name=data["name"], email=data["email"], hashed_password=hashed)
            await user_repo.create(user)
            users[data["name"]] = user

        await session.commit()
        print("Пользователи созданы.")

        # Создаем личный чат между Alice и Bob
        personal_chat = Chat(
            name="Чат Alice и Bob",
            type=ChatType.PERSONAL,
        )
        await chat_repo.create(personal_chat)
        await session.flush()  # Обеспечиваем генерацию personal_chat.id
        personal_members = [
            ChatMember(chat_id=personal_chat.id, user_id=users["Alice"].id),
            ChatMember(chat_id=personal_chat.id, user_id=users["Bob"].id),
        ]
        await chat_member_repo.create_many(personal_members)
        await session.commit()
        print("Личный чат создан.")

        # Создаем сообщения в личном чате
        msg1 = Message(
            chat_id=personal_chat.id,
            sender_id=users["Alice"].id,
            text="Привет, Bob! Как дела?",
        )
        await message_repo.create(msg1)
        await session.flush()  # Обеспечиваем генерацию msg1.id
        await message_read_state_repo.mark_as_read(
            message_id=msg1.id, user_id=users["Alice"].id
        )

        msg2 = Message(
            chat_id=personal_chat.id,
            sender_id=users["Bob"].id,
            text="Привет, Alice! Всё отлично, спасибо.",
        )
        await message_repo.create(msg2)
        await session.flush()  # Обеспечиваем генерацию msg2.id
        await message_read_state_repo.mark_as_read(
            message_id=msg2.id, user_id=users["Bob"].id
        )

        await session.commit()
        print("Сообщения в личном чате созданы.")

        # Создаем групповой чат
        group = Group(title="Группа 1", creator_id=users["Alice"].id)
        await group_repo.create(group)
        await session.commit()  # Обеспечиваем генерацию group.id
        print("Группа создана.")

        group_chat = Chat(name=group.title, type=ChatType.GROUP, group_id=group.id)
        await chat_repo.create(group_chat)
        await session.flush()  # Обеспечиваем генерацию group_chat.id
        group_members = [
            ChatMember(chat_id=group_chat.id, user_id=users["Alice"].id),
            ChatMember(chat_id=group_chat.id, user_id=users["Bob"].id),
            ChatMember(chat_id=group_chat.id, user_id=users["Charlie"].id),
            ChatMember(chat_id=group_chat.id, user_id=users["David"].id),
        ]
        await chat_member_repo.create_many(group_members)
        await session.commit()
        print("Участники группового чата добавлены.")

        # Создаем сообщения в групповом чате
        g_msg1 = Message(
            chat_id=group_chat.id,
            sender_id=users["Alice"].id,
            text="Добро пожаловать в группу!",
        )
        await message_repo.create(g_msg1)
        await session.flush()  # Обеспечиваем генерацию g_msg1.id
        await message_read_state_repo.mark_as_read(
            message_id=g_msg1.id, user_id=users["Alice"].id
        )

        g_msg2 = Message(
            chat_id=group_chat.id,
            sender_id=users["Bob"].id,
            text="Спасибо, рада быть здесь.",
        )
        await message_repo.create(g_msg2)
        await session.flush()  # Обеспечиваем генерацию g_msg2.id
        await message_read_state_repo.mark_as_read(
            message_id=g_msg2.id, user_id=users["Bob"].id
        )

        g_msg3 = Message(
            chat_id=group_chat.id, sender_id=users["Charlie"].id, text="Привет всем!"
        )
        await message_repo.create(g_msg3)
        await session.flush()  # Обеспечиваем генерацию g_msg3.id
        await message_read_state_repo.mark_as_read(
            message_id=g_msg3.id, user_id=users["Charlie"].id
        )

        await session.commit()
        print("Сообщения в групповом чате созданы.")

        print("Test data created successfully!")


if __name__ == "__main__":
    asyncio.run(create_test_data())
