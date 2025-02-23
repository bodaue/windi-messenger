from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class WebSocketAction(str, Enum):
    JOIN_CHAT = "join_chat"
    LEAVE_CHAT = "leave_chat"
    SEND_MESSAGE = "send_message"
    MESSAGE_READ = "message_read"
    TYPING = "typing"


class WSMessageBase(BaseModel):
    action: WebSocketAction


class WSTyping(WSMessageBase):
    action: WebSocketAction = WebSocketAction.TYPING
    chat_id: UUID


class WSJoinChat(WSMessageBase):
    action: WebSocketAction = WebSocketAction.JOIN_CHAT
    chat_id: UUID


class WSLeaveChat(WSMessageBase):
    action: WebSocketAction = WebSocketAction.LEAVE_CHAT
    chat_id: UUID


class WSSendMessage(WSMessageBase):
    action: WebSocketAction = WebSocketAction.SEND_MESSAGE
    chat_id: UUID
    text: str = Field(min_length=1, max_length=4096)


class WSMessageRead(WSMessageBase):
    action: WebSocketAction = WebSocketAction.MESSAGE_READ
    chat_id: UUID
    message_id: UUID
