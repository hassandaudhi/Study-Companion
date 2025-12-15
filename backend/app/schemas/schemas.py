from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============ Chat Schemas ============
class ChatBase(BaseModel):
    title: str = "New Chat"
    description: Optional[str] = None
    agent_type: Optional[str] = None


class ChatCreate(ChatBase):
    user_id: int


class ChatUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[str] = None
    status: Optional[str] = None


class ChatResponse(ChatBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============ Message Schemas ============
class MessageBase(BaseModel):
    content: str
    role: str = Field(..., pattern="^(user|assistant|system)$")
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="message_metadata")


class MessageCreate(MessageBase):
    chat_id: int


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(MessageBase):
    id: int
    chat_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============ File Schemas ============
class FileBase(BaseModel):
    filename: str
    original_filename: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None


class FileCreate(FileBase):
    user_id: int
    chat_id: Optional[int] = None
    file_path: str


class FileResponse(FileBase):
    id: int
    user_id: int
    chat_id: Optional[int] = None
    file_path: str
    status: str
    extracted_text: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ Memory Schemas ============
class MemoryBase(BaseModel):
    content: str
    content_type: str
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="memory_metadata")


class MemoryCreate(MemoryBase):
    user_id: int
    file_id: Optional[int] = None
    vector_id: str


class MemoryResponse(MemoryBase):
    id: int
    user_id: int
    file_id: Optional[int] = None
    vector_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============ Resource Schemas ============
class ResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    resource_type: str
    relevance_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = Field(default=None, alias="resource_metadata")


class ResourceCreate(ResourceBase):
    chat_id: Optional[int] = None


class ResourceResponse(ResourceBase):
    id: int
    chat_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============ Workflow Schemas ============
class WorkflowBase(BaseModel):
    workflow_type: str
    input_data: Optional[Dict[str, Any]] = None


class WorkflowCreate(WorkflowBase):
    user_id: int
    chat_id: Optional[int] = None


class WorkflowUpdate(BaseModel):
    status: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class WorkflowResponse(WorkflowBase):
    id: int
    user_id: int
    chat_id: Optional[int] = None
    status: str
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ Agent Request/Response Schemas ============
class AgentRequest(BaseModel):
    user_id: int
    chat_id: Optional[int] = None
    input_text: Optional[str] = None
    file_id: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    output_text: str
    metadata: Optional[Dict[str, Any]] = None
    resources: Optional[List[ResourceResponse]] = None


# ============ Chat with Messages Schema ============
class ChatWithMessages(ChatResponse):
    messages: List[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)
