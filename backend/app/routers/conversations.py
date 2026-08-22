import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.conversation_repository import MessageRepository
from app.schemas.messaging import (
    ConversationWithLastMessage,
    MessagePublic,
    SendMessageRequest,
    StartConversationRequest,
)
from app.services.messaging_service import MessagingService

router = APIRouter(prefix="/conversations", tags=["messaging"])


def _to_conversation_with_last(conversation, messages_repo: MessageRepository, user_id: uuid.UUID):
    last = messages_repo.last_message(conversation.id)
    unread = messages_repo.unread_count(conversation.id, user_id)
    return ConversationWithLastMessage(
        id=conversation.id,
        buyer_id=conversation.buyer_id,
        seller_id=conversation.seller_id,
        listing_id=conversation.listing_id,
        last_message_at=conversation.last_message_at,
        created_at=conversation.created_at,
        last_message=last,
        unread_count=unread,
    )


@router.post("", response_model=ConversationWithLastMessage, status_code=status.HTTP_201_CREATED)
def start_conversation(
    payload: StartConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MessagingService(db)
    conversation = service.start_or_get_conversation(current_user.id, payload.listing_id)
    return _to_conversation_with_last(conversation, service.messages, current_user.id)


@router.get("", response_model=list[ConversationWithLastMessage])
def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = MessagingService(db)
    conversations = service.list_conversations(current_user.id)
    return [_to_conversation_with_last(c, service.messages, current_user.id) for c in conversations]


@router.get("/{conversation_id}/messages", response_model=list[MessagePublic])
def list_messages(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Récupérer les messages marque automatiquement ceux reçus comme lus."""
    service = MessagingService(db)
    return service.list_messages(conversation_id, current_user.id)


@router.post("/{conversation_id}/messages", response_model=MessagePublic, status_code=status.HTTP_201_CREATED)
def send_message(
    conversation_id: uuid.UUID,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = MessagingService(db)
    return service.send_message(conversation_id, current_user.id, payload.content)
