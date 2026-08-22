import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, conversation_id: uuid.UUID) -> Conversation | None:
        return self.db.get(Conversation, conversation_id)

    def get_between(
        self, buyer_id: uuid.UUID, seller_id: uuid.UUID, listing_id: uuid.UUID | None
    ) -> Conversation | None:
        return self.db.scalar(
            select(Conversation).where(
                Conversation.buyer_id == buyer_id,
                Conversation.seller_id == seller_id,
                Conversation.listing_id == listing_id,
            )
        )

    def create(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.flush()
        return conversation

    def list_for_user(self, user_id: uuid.UUID) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(or_(Conversation.buyer_id == user_id, Conversation.seller_id == user_id))
            .order_by(Conversation.last_message_at.desc().nullslast(), Conversation.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def save(self, conversation: Conversation) -> Conversation:
        self.db.add(conversation)
        self.db.flush()
        return conversation


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, message: Message) -> Message:
        self.db.add(message)
        self.db.flush()
        return message

    def list_for_conversation(self, conversation_id: uuid.UUID) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(self.db.scalars(stmt))

    def last_message(self, conversation_id: uuid.UUID) -> Message | None:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def unread_count(self, conversation_id: uuid.UUID, for_user_id: uuid.UUID) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Message).where(
                Message.conversation_id == conversation_id,
                Message.sender_id != for_user_id,
                Message.is_read.is_(False),
            )
        ) or 0

    def mark_all_read(self, conversation_id: uuid.UUID, for_user_id: uuid.UUID) -> None:
        messages = self.db.scalars(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.sender_id != for_user_id,
                Message.is_read.is_(False),
            )
        )
        for m in messages:
            m.is_read = True
            self.db.add(m)
        self.db.flush()
