import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.models.conversation import Conversation, Message
from app.models.enums import NotificationType
from app.repositories.conversation_repository import ConversationRepository, MessageRepository
from app.repositories.listing_repository import ListingRepository
from app.services.notification_service import NotificationService


class MessagingService:
    def __init__(self, db: Session):
        self.db = db
        self.conversations = ConversationRepository(db)
        self.messages = MessageRepository(db)
        self.listings = ListingRepository(db)
        self.notifications = NotificationService(db)

    def start_or_get_conversation(self, buyer_id: uuid.UUID, listing_id: uuid.UUID) -> Conversation:
        listing = self.listings.get_by_id(listing_id)
        if not listing:
            raise NotFoundError("Annonce introuvable.")
        if listing.seller_id == buyer_id:
            raise ValidationError("Tu ne peux pas démarrer une conversation avec toi-même.")

        existing = self.conversations.get_between(buyer_id, listing.seller_id, listing_id)
        if existing:
            return existing

        conversation = Conversation(buyer_id=buyer_id, seller_id=listing.seller_id, listing_id=listing_id)
        conversation = self.conversations.create(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def _assert_participant(self, conversation: Conversation, user_id: uuid.UUID) -> None:
        if user_id not in (conversation.buyer_id, conversation.seller_id):
            raise ForbiddenError("Tu ne fais pas partie de cette conversation.")

    def list_conversations(self, user_id: uuid.UUID) -> list[Conversation]:
        return self.conversations.list_for_user(user_id)

    def get_conversation(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Conversation:
        conversation = self.conversations.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundError("Conversation introuvable.")
        self._assert_participant(conversation, user_id)
        return conversation

    def list_messages(self, conversation_id: uuid.UUID, user_id: uuid.UUID) -> list[Message]:
        conversation = self.get_conversation(conversation_id, user_id)
        self.messages.mark_all_read(conversation.id, user_id)
        self.db.commit()
        return self.messages.list_for_conversation(conversation.id)

    def send_message(self, conversation_id: uuid.UUID, sender_id: uuid.UUID, content: str) -> Message:
        conversation = self.get_conversation(conversation_id, sender_id)
        message = self.messages.create(
            Message(conversation_id=conversation.id, sender_id=sender_id, content=content)
        )
        conversation.last_message_at = message.created_at
        self.conversations.save(conversation)

        recipient_id = conversation.seller_id if sender_id == conversation.buyer_id else conversation.buyer_id
        self.notifications.notify(
            recipient_id, NotificationType.NEW_MESSAGE, "Nouveau message",
            content[:100], related_entity_id=conversation.id, auto_commit=False,
        )

        self.db.commit()
        self.db.refresh(message)
        return message
