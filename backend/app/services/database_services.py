from sqlalchemy.orm import Session
from app.models.models import User, Chat, Message, File, Memory, Resource, Workflow
from app.schemas.schemas import (
    UserCreate, UserUpdate,
    ChatCreate, ChatUpdate,
    MessageCreate, MessageUpdate,
    FileCreate,
    MemoryCreate,
    ResourceCreate,
    WorkflowCreate, WorkflowUpdate
)
from typing import List, Optional
from datetime import datetime, timezone
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============ User Service ============
class UserService:
    """Service for user operations"""

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Create a new user with hashed password"""
        hashed_password = hash_password(user.password) if user.password else None
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True


# ============ Chat Service ============
class ChatService:
    """Service for chat operations"""

    @staticmethod
    def create_chat(db: Session, chat: ChatCreate) -> Chat:
        """Create a new chat session"""
        db_chat = Chat(**chat.model_dump())
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat

    @staticmethod
    def get_chat(db: Session, chat_id: int) -> Optional[Chat]:
        """Get chat by ID"""
        return db.query(Chat).filter(Chat.id == chat_id).first()

    @staticmethod
    def get_user_chats(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Chat]:
        """Get all chats for a user"""
        return db.query(Chat).filter(Chat.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def update_chat(db: Session, chat_id: int, chat_update: ChatUpdate) -> Optional[Chat]:
        """Update chat"""
        db_chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not db_chat:
            return None

        update_data = chat_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chat, field, value)

        db.commit()
        db.refresh(db_chat)
        return db_chat

    @staticmethod
    def delete_chat(db: Session, chat_id: int) -> bool:
        """Delete chat"""
        db_chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if not db_chat:
            return False

        db.delete(db_chat)
        db.commit()
        return True


# ============ Message Service ============
class MessageService:
    """Service for message operations"""

    @staticmethod
    def create_message(db: Session, message: MessageCreate) -> Message:
        """Create a new message"""
        message_data = message.model_dump()
        # Map schema field 'metadata' to model attribute 'message_metadata'
        if 'metadata' in message_data:
            message_data['message_metadata'] = message_data.pop('metadata')
        db_message = Message(**message_data)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    @staticmethod
    def get_message(db: Session, message_id: int) -> Optional[Message]:
        """Get message by ID"""
        return db.query(Message).filter(Message.id == message_id).first()

    @staticmethod
    def get_chat_messages(db: Session, chat_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        """Get all messages for a chat"""
        return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).offset(skip).limit(limit).all()

    @staticmethod
    def update_message(db: Session, message_id: int, message_update: MessageUpdate) -> Optional[Message]:
        """Update message"""
        db_message = db.query(Message).filter(Message.id == message_id).first()
        if not db_message:
            return None

        update_data = message_update.model_dump(exclude_unset=True)
        # Map schema field 'metadata' to model attribute 'message_metadata'
        if 'metadata' in update_data:
            update_data['message_metadata'] = update_data.pop('metadata')
        for field, value in update_data.items():
            setattr(db_message, field, value)

        db.commit()
        db.refresh(db_message)
        return db_message

    @staticmethod
    def delete_message(db: Session, message_id: int) -> bool:
        """Delete message"""
        db_message = db.query(Message).filter(Message.id == message_id).first()
        if not db_message:
            return False

        db.delete(db_message)
        db.commit()
        return True


# ============ File Service (Database Operations) ============
class FileDBService:
    """Service for file database operations"""

    @staticmethod
    def create_file(db: Session, file: FileCreate) -> File:
        """Create file record"""
        db_file = File(**file.model_dump())
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

    @staticmethod
    def get_file(db: Session, file_id: int) -> Optional[File]:
        """Get file by ID"""
        return db.query(File).filter(File.id == file_id).first()

    @staticmethod
    def get_user_files(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[File]:
        """Get all files for a user"""
        return db.query(File).filter(File.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def update_file_status(db: Session, file_id: int, status: str, extracted_text: Optional[str] = None) -> Optional[File]:
        """Update file status and extracted text"""
        db_file = db.query(File).filter(File.id == file_id).first()
        if not db_file:
            return None

        db_file.status = status
        if extracted_text:
            db_file.extracted_text = extracted_text

        db.commit()
        db.refresh(db_file)
        return db_file

    @staticmethod
    def delete_file(db: Session, file_id: int) -> bool:
        """Delete file record"""
        db_file = db.query(File).filter(File.id == file_id).first()
        if not db_file:
            return False

        db.delete(db_file)
        db.commit()
        return True


# ============ Memory Service (Database Operations) ============
class MemoryDBService:
    """Service for memory database operations"""

    @staticmethod
    def create_memory(db: Session, memory: MemoryCreate) -> Memory:
        """Create memory record"""
        memory_data = memory.model_dump()
        # Map schema field 'metadata' to model attribute 'memory_metadata'
        if 'metadata' in memory_data:
            memory_data['memory_metadata'] = memory_data.pop('metadata')
        db_memory = Memory(**memory_data)
        db.add(db_memory)
        db.commit()
        db.refresh(db_memory)
        return db_memory

    @staticmethod
    def get_memory(db: Session, memory_id: int) -> Optional[Memory]:
        """Get memory by ID"""
        return db.query(Memory).filter(Memory.id == memory_id).first()

    @staticmethod
    def get_memory_by_vector_id(db: Session, vector_id: str) -> Optional[Memory]:
        """Get memory by vector ID"""
        return db.query(Memory).filter(Memory.vector_id == vector_id).first()

    @staticmethod
    def get_user_memories(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Memory]:
        """Get all memories for a user"""
        return db.query(Memory).filter(Memory.user_id == user_id).offset(skip).limit(limit).all()

    @staticmethod
    def delete_memory(db: Session, memory_id: int) -> bool:
        """Delete memory record"""
        db_memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if not db_memory:
            return False

        db.delete(db_memory)
        db.commit()
        return True


# ============ Resource Service ============
class ResourceDBService:
    """Service for resource database operations"""

    @staticmethod
    def create_resource(db: Session, resource: ResourceCreate) -> Resource:
        """Create resource"""
        resource_data = resource.model_dump()
        # Map schema field 'metadata' to model attribute 'resource_metadata'
        if 'metadata' in resource_data:
            resource_data['resource_metadata'] = resource_data.pop('metadata')
        db_resource = Resource(**resource_data)
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        return db_resource

    @staticmethod
    def get_resource(db: Session, resource_id: int) -> Optional[Resource]:
        """Get resource by ID"""
        return db.query(Resource).filter(Resource.id == resource_id).first()

    @staticmethod
    def get_chat_resources(db: Session, chat_id: int) -> List[Resource]:
        """Get all resources for a chat"""
        return db.query(Resource).filter(Resource.chat_id == chat_id).all()

    @staticmethod
    def delete_resource(db: Session, resource_id: int) -> bool:
        """Delete resource"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            return False

        db.delete(db_resource)
        db.commit()
        return True


# ============ Workflow Service ============
class WorkflowDBService:
    """Service for workflow database operations"""

    @staticmethod
    def create_workflow(db: Session, workflow: WorkflowCreate) -> Workflow:
        """Create workflow"""
        db_workflow = Workflow(**workflow.model_dump(), started_at=datetime.now(timezone.utc))
        db.add(db_workflow)
        db.commit()
        db.refresh(db_workflow)
        return db_workflow

    @staticmethod
    def get_workflow(db: Session, workflow_id: int) -> Optional[Workflow]:
        """Get workflow by ID"""
        return db.query(Workflow).filter(Workflow.id == workflow_id).first()

    @staticmethod
    def update_workflow(db: Session, workflow_id: int, workflow_update: WorkflowUpdate) -> Optional[Workflow]:
        """Update workflow"""
        db_workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not db_workflow:
            return None

        update_data = workflow_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_workflow, field, value)

        if update_data.get("status") in ["completed", "failed"]:
            db_workflow.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(db_workflow)
        return db_workflow

    @staticmethod
    def get_user_workflows(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Workflow]:
        """Get all workflows for a user"""
        return db.query(Workflow).filter(Workflow.user_id == user_id).offset(skip).limit(limit).all()
