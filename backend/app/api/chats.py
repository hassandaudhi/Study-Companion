from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.schemas import ChatCreate, ChatUpdate, ChatResponse, ChatWithMessages
from app.services.database_services import ChatService, MessageService
from typing import List

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(chat: ChatCreate, db: Session = Depends(get_db)):
    """Create a new chat session"""
    return ChatService.create_chat(db, chat)


@router.get("/{chat_id}", response_model=ChatWithMessages)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    """Get chat by ID with all messages"""
    chat = ChatService.get_chat(db, chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    # Get messages for this chat
    messages = MessageService.get_chat_messages(db, chat_id)

    # Convert to dict and add messages
    chat_dict = {
        "id": chat.id,
        "user_id": chat.user_id,
        "title": chat.title,
        "description": chat.description,
        "agent_type": chat.agent_type,
        "status": chat.status,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
        "messages": messages
    }

    return chat_dict


@router.get("/user/{user_id}", response_model=List[ChatResponse])
def get_user_chats(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all chats for a user"""
    return ChatService.get_user_chats(db, user_id, skip, limit)


@router.put("/{chat_id}", response_model=ChatResponse)
def update_chat(chat_id: int, chat_update: ChatUpdate, db: Session = Depends(get_db)):
    """Update chat"""
    chat = ChatService.update_chat(db, chat_id, chat_update)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return chat


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    """Delete chat"""
    success = ChatService.delete_chat(db, chat_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    return None
