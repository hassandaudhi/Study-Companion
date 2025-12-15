# AI Study Companion Pro - Backend

A comprehensive backend API for an AI-powered study companion built with FastAPI, LangChain, LangGraph, PostgreSQL, and Pinecone.

## 🚀 Features

- **Multi-Agent AI System**: Summarization, Question Generation, Explanations, Resource Recommendations
- **Workflow Orchestration**: Complex multi-step workflows with LangGraph
- **Vector Memory**: Context-aware responses using Pinecone embeddings
- **File Processing**: Upload and extract text from PDFs, DOCX, and TXT files
- **RESTful API**: Comprehensive FastAPI endpoints with automatic documentation
- **Database Management**: PostgreSQL with Alembic migrations
- **Modular Architecture**: Scalable, maintainable, and extensible design

## 📋 Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + Alembic
- **AI Orchestration**: LangChain + LangGraph
- **Vector Database**: Pinecone
- **File Processing**: PyPDF2, python-docx
- **Authentication**: JWT (optional)

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route definitions
│   │   ├── users.py
│   │   ├── chats.py
│   │   ├── messages.py
│   │   ├── files.py
│   │   ├── agents.py
│   │   ├── workflow.py
│   │   └── memory.py
│   ├── agents/                 # LangChain agent implementations
│   │   └── langchain_agents.py
│   ├── workflows/              # LangGraph workflow orchestrators
│   │   └── langgraph_workflows.py
│   ├── models/                 # SQLAlchemy models
│   │   └── models.py
│   ├── schemas/                # Pydantic schemas
│   │   └── schemas.py
│   ├── services/               # Business logic layer
│   │   ├── database_services.py
│   │   ├── file_service.py
│   │   └── pinecone_service.py
│   ├── db/                     # Database configuration
│   │   └── database.py
│   ├── config/                 # Application configuration
│   │   └── settings.py
│   └── utils/                  # Utility functions
│       ├── logger.py
│       └── text_processing.py
├── alembic/                    # Database migrations
│   ├── env.py
│   └── versions/
├── storage/                    # File upload storage
│   └── uploads/
├── tests/                      # Unit and integration tests
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── alembic.ini                 # Alembic configuration
└── README.md                   # This file
```

## 🔧 Installation & Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Google Gemini API key
- Pinecone API key

### Step 1: Clone and Navigate

```bash
cd "AI Study Companion Pro/backend"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Copy `.env.example` to `.env` and update with your credentials:

```bash
copy .env.example .env
```

Update the following in `.env`:
- `DATABASE_URL`: Your PostgreSQL connection string
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `GEMINI_MODEL`: The Gemini model to use (default: gemini-1.5-flash)
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENVIRONMENT`: Your Pinecone environment
- `SECRET_KEY`: Generate a secure secret key

### Step 5: Initialize Database

```bash
# Create database migrations
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Step 6: Run the Server

```bash
# Development mode
python -m uvicorn app.main:app --reload

# Production mode
python app/main.py
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

## 📚 API Endpoints

### Users
- `POST /api/users/` - Create a new user
- `GET /api/users/{user_id}` - Get user by ID
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user

### Chats
- `POST /api/chats/` - Create a new chat session
- `GET /api/chats/{chat_id}` - Get chat with messages
- `GET /api/chats/user/{user_id}` - Get all chats for a user
- `PUT /api/chats/{chat_id}` - Update chat
- `DELETE /api/chats/{chat_id}` - Delete chat

### Messages
- `POST /api/messages/` - Create a message
- `GET /api/messages/chat/{chat_id}` - Get all messages for a chat
- `PATCH /api/messages/{message_id}` - Update message
- `DELETE /api/messages/{message_id}` - Delete message

### Files
- `POST /api/files/` - Upload a file (PDF, DOCX, TXT)
- `GET /api/files/{file_id}` - Get file metadata
- `GET /api/files/user/{user_id}` - Get all files for a user
- `DELETE /api/files/{file_id}` - Delete file

### AI Agents
- `POST /api/agent/summarizer` - Summarize content
- `POST /api/agent/question_generator` - Generate quiz questions
- `POST /api/agent/explainer` - Get context-aware explanations
- `POST /api/agent/resource_recommender` - Get learning resource recommendations

### Workflows
- `POST /api/workflow/run` - Trigger a multi-agent workflow
- `GET /api/workflow/{workflow_id}` - Get workflow status
- `GET /api/workflow/user/{user_id}` - Get all workflows for a user

### Memory/Embeddings
- `POST /api/memory/` - Create embeddings
- `GET /api/memory/search` - Search similar embeddings
- `GET /api/memory/user/{user_id}` - Get all memories for a user
- `DELETE /api/memory/{memory_id}` - Delete memory
- `GET /api/memory/stats` - Get memory statistics

## 🧪 Usage Examples

### 1. Create a User

```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "username": "student1",
    "full_name": "John Doe"
  }'
```

### 2. Upload and Process a PDF

```bash
curl -X POST "http://localhost:8000/api/files/" \
  -F "file=@document.pdf" \
  -F "user_id=1"
```

### 3. Summarize Content

```bash
curl -X POST "http://localhost:8000/api/agent/summarizer" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "file_id": 1,
    "chat_id": 1
  }'
```

### 4. Run PDF Processing Workflow

```bash
curl -X POST "http://localhost:8000/api/workflow/run" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "chat_id": 1,
    "workflow_type": "pdf_processing",
    "input_data": {
      "file_id": 1
    }
  }'
```

## 🔄 Workflow Types

### PDF Processing Workflow
1. Extract text from PDF
2. Generate summary
3. Create quiz questions
4. Recommend learning resources
5. Store embeddings in Pinecone

### Multi-Agent Chat Workflow
1. Identify user intent
2. Retrieve relevant context from embeddings
3. Route to appropriate agent
4. Generate response
5. Store conversation embeddings

## 🗃️ Database Schema

### Core Tables
- **users**: User accounts
- **chats**: Chat sessions
- **messages**: Chat messages (user/assistant)
- **files**: Uploaded file metadata
- **memories**: Vector embedding metadata
- **resources**: Learning resource recommendations
- **workflows**: Workflow execution tracking

## 🔐 Security Considerations

- Use environment variables for sensitive credentials
- Implement JWT authentication for production
- Validate file uploads (size, type)
- Sanitize user inputs
- Use HTTPS in production
- Implement rate limiting

## 🚀 Deployment

### Docker Deployment (Recommended)

```dockerfile
# Create Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t ai-study-companion-backend .
docker run -p 8000:8000 --env-file .env ai-study-companion-backend
```

### Cloud Deployment Options
- **AWS**: EC2, ECS, or Lambda
- **Google Cloud**: Cloud Run or App Engine
- **Azure**: App Service or Container Instances
- **Heroku**: Using Procfile

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 📝 Environment Variables

See `.env.example` for all required environment variables.

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## 📄 License

MIT License

## 🆘 Support

For issues and questions, please open a GitHub issue.

## 🎯 Next Steps

- [ ] Implement JWT authentication
- [ ] Add WebSocket support for real-time responses
- [ ] Implement caching with Redis
- [ ] Add comprehensive test suite
- [ ] Set up CI/CD pipeline
- [ ] Add monitoring and logging
- [ ] Implement rate limiting
- [ ] Add API versioning

---

**Built with ❤️ for AI-powered learning**
