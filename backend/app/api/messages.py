from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import MessageCreate, MessageUpdate, MessageResponse
from app.services.database_services import MessageService, ChatService
from typing import List

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """Create a new message"""
    # Verify chat exists
    chat = ChatService.get_chat(db, message.chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    return MessageService.create_message(db, message)


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(message_id: int, db: Session = Depends(get_db)):
    """Get message by ID"""
    message = MessageService.get_message(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    return message


@router.get("/chat/{chat_id}", response_model=List[MessageResponse])
def get_chat_messages(chat_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all messages for a chat"""
    # Verify chat exists
    chat = ChatService.get_chat(db, chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    return MessageService.get_chat_messages(db, chat_id, skip, limit)


@router.patch("/{message_id}", response_model=MessageResponse)
def update_message(message_id: int, message_update: MessageUpdate, db: Session = Depends(get_db)):
    """Update message"""
    message = MessageService.update_message(db, message_id, message_update)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    return message


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    """Delete message"""
    success = MessageService.delete_message(db, message_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    return None
