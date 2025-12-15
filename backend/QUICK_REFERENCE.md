# AI Study Companion Pro - Quick Reference

## 🚀 Start Commands

```powershell
# Activate environment
.\venv\Scripts\activate

# Run server
python -m uvicorn app.main:app --reload

# Run with Docker
docker-compose up
```

## 🔧 Database Commands

```powershell
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current version
alembic current
```

## 📡 Common API Calls

### Create User
```powershell
curl -X POST "http://localhost:8000/api/users/" `
  -H "Content-Type: application/json" `
  -d '{\"email\":\"user@example.com\",\"username\":\"user1\",\"full_name\":\"User Name\"}'
```

### Create Chat
```powershell
curl -X POST "http://localhost:8000/api/chats/" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":1,\"title\":\"My Study Session\"}'
```

### Upload File
```powershell
curl -X POST "http://localhost:8000/api/files/" `
  -F "file=@document.pdf" `
  -F "user_id=1"
```

### Summarize
```powershell
curl -X POST "http://localhost:8000/api/agent/summarizer" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":1,\"file_id\":1,\"chat_id\":1}'
```

### Run Workflow
```powershell
curl -X POST "http://localhost:8000/api/workflow/run" `
  -H "Content-Type: application/json" `
  -d '{\"user_id\":1,\"chat_id\":1,\"workflow_type\":\"pdf_processing\",\"input_data\":{\"file_id\":1}}'
```

## 🧪 Testing Commands

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_api.py::test_create_user

# Verbose output
pytest -v
```

## 🐛 Debugging

```powershell
# Check server logs
# (stdout when running)

# Test database connection
psql -U postgres -d ai_study_companion

# Test Pinecone
python -c "from app.services.pinecone_service import pinecone_service; print(pinecone_service.get_index_stats())"

# Check environment
python -c "from app.config.settings import settings; print(settings.dict())"
```

## 📊 Useful URLs

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

## 🔑 Environment Variables

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
GOOGLE_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/embedding-001
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=...
SECRET_KEY=...
```

## 📁 Project Structure

```
app/
├── main.py              # Entry point
├── api/                 # Routes
├── agents/              # AI agents
├── workflows/           # Workflows
├── models/              # DB models
├── schemas/             # Validation
├── services/            # Business logic
├── db/                  # Database
└── config/              # Settings
```

## 🎯 Common Tasks

### Add New Endpoint
1. Create route in `app/api/`
2. Add service in `app/services/`
3. Add schema in `app/schemas/`
4. Include router in `app/main.py`

### Add New Agent
1. Create agent class in `app/agents/langchain_agents.py`
2. Add to `get_agent()` factory
3. Create endpoint in `app/api/agents.py`

### Modify Database
1. Edit `app/models/models.py`
2. Run `alembic revision --autogenerate -m "message"`
3. Run `alembic upgrade head`

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | Change port: `--port 8001` |
| DB connection error | Check DATABASE_URL in .env |
| Module not found | Activate venv, reinstall |
| Pinecone error | Check API key and environment |
| File upload fails | Check UPLOAD_DIR permissions |

## 📞 Quick Links

- [README](README.md) - Full documentation
- [Setup Guide](SETUP_GUIDE.md) - Installation
- [API Docs](API_DOCUMENTATION.md) - API reference
- [Project Overview](PROJECT_OVERVIEW.md) - Complete overview

## 💡 Tips

1. Always activate virtual environment first
2. Check `/docs` for interactive API testing
3. Use environment variables for secrets
4. Test endpoints in interactive docs
5. Check logs for error details
6. Use alembic for all DB changes
7. Write tests for new features

---

**Need help? Check the full documentation in README.md**
