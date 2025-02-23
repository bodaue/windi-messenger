from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.message import MessageReadState


class MessageReadStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def mark_as_read(
        self,
        message_id: UUID,
        user_id: UUID,
    ) -> None:
        read_state = MessageReadState(
            message_id=message_id, user_id=user_id, read_at=datetime.now(UTC)
        )
        self._session.add(read_state)
