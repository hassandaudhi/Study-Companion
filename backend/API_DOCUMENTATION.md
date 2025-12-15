# API Documentation

## Authentication (Optional)

If JWT authentication is enabled, include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Base URL

```
http://localhost:8000/api
```

## User Endpoints

### Create User
**POST** `/users/`

Request body:
```json
{
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "password": "optional_password"
}
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

### Get User
**GET** `/users/{user_id}`

### Update User
**PUT** `/users/{user_id}`

### Delete User
**DELETE** `/users/{user_id}`

## Chat Endpoints

### Create Chat
**POST** `/chats/`

Request body:
```json
{
  "user_id": 1,
  "title": "Study Session",
  "description": "Learning about AI",
  "agent_type": "summarizer"
}
```

### Get Chat with Messages
**GET** `/chats/{chat_id}`

### Get User Chats
**GET** `/chats/user/{user_id}?skip=0&limit=100`

### Update Chat
**PUT** `/chats/{chat_id}`

### Delete Chat
**DELETE** `/chats/{chat_id}`

## Message Endpoints

### Create Message
**POST** `/messages/`

Request body:
```json
{
  "chat_id": 1,
  "role": "user",
  "content": "Hello, can you help me?",
  "metadata": {"key": "value"}
}
```

### Get Chat Messages
**GET** `/messages/chat/{chat_id}?skip=0&limit=100`

### Update Message
**PATCH** `/messages/{message_id}`

### Delete Message
**DELETE** `/messages/{message_id}`

## File Endpoints

### Upload File
**POST** `/files/`

Form data:
- `file`: File upload (PDF, DOCX, TXT)
- `user_id`: User ID
- `chat_id`: Optional chat ID

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "chat_id": 1,
  "filename": "unique_filename.pdf",
  "original_filename": "document.pdf",
  "file_path": "/storage/uploads/1/unique_filename.pdf",
  "file_type": "pdf",
  "file_size": 102400,
  "status": "processed",
  "extracted_text": "Document content...",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get File
**GET** `/files/{file_id}`

### Get User Files
**GET** `/files/user/{user_id}?skip=0&limit=100`

### Delete File
**DELETE** `/files/{file_id}`

## Agent Endpoints

### Summarizer
**POST** `/agent/summarizer`

Request body:
```json
{
  "user_id": 1,
  "chat_id": 1,
  "input_text": "Long text to summarize...",
  "parameters": {
    "focus_areas": "key concepts"
  }
}
```

Or with file:
```json
{
  "user_id": 1,
  "chat_id": 1,
  "file_id": 1,
  "parameters": {}
}
```

Response:
```json
{
  "output_text": "This is a summary...",
  "metadata": {
    "summary": "This is a summary...",
    "original_length": 5000,
    "summary_length": 500,
    "compression_ratio": 0.1,
    "model": "gpt-3.5-turbo"
  }
}
```

### Question Generator
**POST** `/agent/question_generator`

Request body:
```json
{
  "user_id": 1,
  "chat_id": 1,
  "input_text": "Content to generate questions from...",
  "parameters": {
    "num_questions": 5,
    "difficulty": "medium"
  }
}
```

Response:
```json
{
  "output_text": "[{\"question\": \"...\", \"options\": [...], \"correct_answer\": \"A\", \"explanation\": \"...\"}]",
  "metadata": {
    "questions": [...],
    "num_questions": 5,
    "difficulty": "medium",
    "model": "gpt-3.5-turbo"
  }
}
```

### Explainer
**POST** `/agent/explainer`

Request body:
```json
{
  "user_id": 1,
  "chat_id": 1,
  "input_text": "What is machine learning?",
  "parameters": {
    "detail_level": "detailed"
  }
}
```

Response:
```json
{
  "output_text": "Machine learning is...",
  "metadata": {
    "explanation": "Machine learning is...",
    "question": "What is machine learning?",
    "used_context": true,
    "detail_level": "detailed",
    "model": "gpt-3.5-turbo"
  }
}
```

### Resource Recommender
**POST** `/agent/resource_recommender`

Request body:
```json
{
  "user_id": 1,
  "chat_id": 1,
  "input_text": "machine learning",
  "parameters": {
    "num_resources": 5
  }
}
```

Response:
```json
{
  "output_text": "[{\"title\": \"...\", \"description\": \"...\", \"url\": \"...\", \"type\": \"article\", \"relevance_score\": 0.95}]",
  "metadata": {
    "resources": [...],
    "num_resources": 5,
    "topic": "machine learning",
    "model": "gpt-3.5-turbo"
  },
  "resources": [...]
}
```

## Workflow Endpoints

### Run Workflow
**POST** `/workflow/run`

PDF Processing Workflow:
```json
{
  "user_id": 1,
  "chat_id": 1,
  "workflow_type": "pdf_processing",
  "input_data": {
    "file_id": 1
  }
}
```

Multi-Agent Chat Workflow:
```json
{
  "user_id": 1,
  "chat_id": 1,
  "workflow_type": "multi_agent_chat",
  "input_data": {
    "input_text": "Explain quantum computing"
  }
}
```

Response (202 Accepted):
```json
{
  "id": 1,
  "user_id": 1,
  "chat_id": 1,
  "workflow_type": "pdf_processing",
  "status": "pending",
  "input_data": {...},
  "output_data": null,
  "error_message": null,
  "started_at": "2024-01-01T00:00:00Z",
  "completed_at": null,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get Workflow Status
**GET** `/workflow/{workflow_id}`

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "chat_id": 1,
  "workflow_type": "pdf_processing",
  "status": "completed",
  "input_data": {...},
  "output_data": {
    "summary": "...",
    "questions": [...],
    "resources": [...]
  },
  "error_message": null,
  "started_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:00:10Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Get User Workflows
**GET** `/workflow/user/{user_id}?skip=0&limit=100`

## Memory/Embeddings Endpoints

### Create Embeddings
**POST** `/memory/`

Query parameters:
- `user_id`: User ID
- `file_id`: Optional file ID
- `content_type`: Content type (summary, question, explanation, resource)
- `metadata`: Optional metadata dict

Request body:
```json
{
  "texts": [
    "First chunk of text...",
    "Second chunk of text..."
  ]
}
```

Response:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "file_id": 1,
    "vector_id": "uuid-1",
    "content": "First chunk of text...",
    "content_type": "summary",
    "metadata": {...},
    "created_at": "2024-01-01T00:00:00Z"
  },
  ...
]
```

### Search Embeddings
**GET** `/memory/search?query=machine learning&user_id=1&top_k=5&content_type=summary`

Response:
```json
[
  {
    "vector_id": "uuid-1",
    "score": 0.95,
    "text": "Machine learning is...",
    "metadata": {...},
    "memory_id": 1,
    "file_id": 1,
    "content_type": "summary"
  },
  ...
]
```

### Get User Memories
**GET** `/memory/user/{user_id}?skip=0&limit=100`

### Delete Memory
**DELETE** `/memory/{memory_id}`

### Get Memory Stats
**GET** `/memory/stats`

Response:
```json
{
  "total_vector_count": 1000,
  "dimension": 1536,
  "index_fullness": 0.1
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `204 No Content`: Successful deletion
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

(To be implemented)

## Pagination

Most list endpoints support pagination with `skip` and `limit` query parameters:

```
GET /api/chats/user/1?skip=0&limit=20
```

## Filtering

(To be implemented)

## Sorting

(To be implemented)
