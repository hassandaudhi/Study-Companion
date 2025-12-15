from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255))  # Optional for auth
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")


class Chat(Base):
    """Chat session model"""
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="New Chat")
    description = Column(Text)
    agent_type = Column(String(50))  # summarizer, question_generator, explainer, resource_recommender
    status = Column(String(20), default="active")  # active, archived, deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    files = relationship("File", back_populates="chat")


class Message(Base):
    """Message model for chat messages"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column("metadata", JSON)  # Store additional info like agent outputs, resources
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    chat = relationship("Chat", back_populates="messages")


class File(Base):
    """File upload model"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, docx, txt
    file_size = Column(Integer)  # in bytes
    extracted_text = Column(Text)  # Extracted text content
    status = Column(String(20), default="uploaded")  # uploaded, processing, processed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="files")
    chat = relationship("Chat", back_populates="files")
    memories = relationship("Memory", back_populates="file")


class Memory(Base):
    """Memory embeddings metadata model"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="SET NULL"), nullable=True)
    vector_id = Column(String(255), unique=True, nullable=False)  # Pinecone vector ID
    content = Column(Text)  # Original text chunk
    content_type = Column(String(50))  # summary, question, explanation, resource
    memory_metadata = Column("metadata", JSON)  # Additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="memories")
    file = relationship("File", back_populates="memories")


class Resource(Base):
    """Resource recommendations model"""
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    url = Column(String(1000))
    resource_type = Column(String(50))  # article, video, book, course
    relevance_score = Column(Float)
    resource_metadata = Column("metadata", JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Workflow(Base):
    """Workflow execution tracking model"""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=True)
    workflow_type = Column(String(100), nullable=False)  # pdf_processing, multi_agent_chat
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
