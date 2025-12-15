# AI Study Companion Pro - Backend Setup Guide

## Quick Start

### 1. Environment Setup

```powershell
# Navigate to backend directory
cd "e:\AI Study Companion Pro\backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

#### Install PostgreSQL

Download and install PostgreSQL from: https://www.postgresql.org/download/windows/

#### Create Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE ai_study_companion;

-- Create user (optional)
CREATE USER ai_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_study_companion TO ai_user;
```

### 3. Environment Configuration

```powershell
# Copy environment template
copy .env.example .env
```

Edit `.env` file and update:

```env
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_study_companion

# Google Gemini (Get from: https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your-google-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/embedding-001

# Pinecone (Get from: https://www.pinecone.io/)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=your-pinecone-environment
PINECONE_INDEX_NAME=ai-study-companion

# Security
SECRET_KEY=your-super-secret-key-change-this
```

### 4. Initialize Database Migrations

```powershell
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Run the Server

```powershell
# Development mode with auto-reload
python -m uvicorn app.main:app --reload

# Or run directly
python app/main.py
```

The server will start at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Testing the API

### Using Interactive Docs

1. Navigate to http://localhost:8000/docs
2. Try out the endpoints directly in the browser
3. See request/response examples

### Using cURL

```powershell
# Create a user
curl -X POST "http://localhost:8000/api/users/" `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"test@example.com\",\"username\":\"testuser\",\"full_name\":\"Test User\"}'

# Create a chat
curl -X POST "http://localhost:8000/api/chats/" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":1,\"title\":\"My Study Session\"}'

# Upload a file
curl -X POST "http://localhost:8000/api/files/" `
  -F "file=@document.pdf" `
  -F "user_id=1"
```

### Using Python Requests

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Create user
response = requests.post(
    f"{BASE_URL}/users/",
    json={
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User"
    }
)
user = response.json()
print(f"User created: {user}")

# Create chat
response = requests.post(
    f"{BASE_URL}/chats/",
    json={
        "user_id": user["id"],
        "title": "Study Session"
    }
)
chat = response.json()
print(f"Chat created: {chat}")

# Summarize text
response = requests.post(
    f"{BASE_URL}/agent/summarizer",
    json={
        "user_id": user["id"],
        "chat_id": chat["id"],
        "input_text": "Your long text here..."
    }
)
summary = response.json()
print(f"Summary: {summary}")
```

## Troubleshooting

### Database Connection Issues

```powershell
# Test PostgreSQL connection
psql -U postgres -d ai_study_companion -c "SELECT version();"
```

### Module Import Errors

```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Pinecone Connection Issues

```powershell
# Test Pinecone connection
python -c "from pinecone import Pinecone; pc = Pinecone(api_key='YOUR_KEY'); print(pc.list_indexes())"
```

### Port Already in Use

```powershell
# Run on different port
python -m uvicorn app.main:app --port 8001 --reload
```

## Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

## Development Workflow

### 1. Making Database Changes

```powershell
# 1. Modify models in app/models/models.py
# 2. Create migration
alembic revision --autogenerate -m "Description of changes"

# 3. Review migration in alembic/versions/
# 4. Apply migration
alembic upgrade head

# 5. Rollback if needed
alembic downgrade -1
```

### 2. Adding New Endpoints

1. Create route in `app/api/`
2. Add business logic in `app/services/`
3. Create Pydantic schemas in `app/schemas/`
4. Update `app/main.py` to include router
5. Test in interactive docs

### 3. Adding New Agents

1. Create agent class in `app/agents/langchain_agents.py`
2. Add to `get_agent()` factory function
3. Create endpoint in `app/api/agents.py`
4. Test the agent

## Production Deployment

### Using Docker

```powershell
# Build image
docker build -t ai-study-companion-backend .

# Run container
docker run -p 8000:8000 --env-file .env ai-study-companion-backend
```

### Using Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ai_study_companion
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Environment Variables for Production

```env
DEBUG=False
CORS_ORIGINS=["https://yourdomain.com"]
DATABASE_URL=postgresql://user:password@db_host:5432/ai_study_companion
SECRET_KEY=very-secure-secret-key
```

## Monitoring & Logging

### View Logs

```powershell
# Application logs are written to stdout
# In production, redirect to file or logging service
```

### Health Checks

```powershell
# Check API health
curl http://localhost:8000/health

# Check database
curl http://localhost:8000/api/users/1
```

## Performance Optimization

### Database Connection Pooling

Already configured in `app/db/database.py`:
- `pool_size=10`
- `max_overflow=20`

### Caching (To be implemented)

Use Redis for caching frequently accessed data.

### Rate Limiting (To be implemented)

Use slowapi or similar for rate limiting.

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Enable JWT authentication
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Validate all user inputs
- [ ] Set appropriate CORS origins
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Database backups
- [ ] Monitor API usage

## Next Steps

1. **Frontend Integration**: Connect with React frontend
2. **Authentication**: Implement JWT/OAuth2
3. **Real-time**: Add WebSocket support
4. **Caching**: Implement Redis caching
5. **Monitoring**: Add application monitoring
6. **CI/CD**: Set up automated deployment
7. **Documentation**: Generate API docs
8. **Testing**: Increase test coverage

## Support

For issues and questions:
- Check API docs: http://localhost:8000/docs
- Review README.md
- Check error logs
- Open GitHub issue

---

**Happy Coding! 🚀**
