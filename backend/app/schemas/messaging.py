import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StartConversationRequest(BaseModel):
    listing_id: uuid.UUID


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class MessagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    is_read: bool
    created_at: datetime


class ConversationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    buyer_id: uuid.UUID
    seller_id: uuid.UUID
    listing_id: uuid.UUID | None
    last_message_at: datetime | None
    created_at: datetime


class ConversationWithLastMessage(ConversationPublic):
    last_message: MessagePublic | None
    unread_count: int
