# Quick Start: RAG Pipeline with Google Gemini

This guide will get your RAG (Retrieval-Augmented Generation) pipeline running in 5 minutes.

---

## 🚀 Prerequisites

1. Python 3.9+
2. PostgreSQL 13+
3. Google Gemini API key
4. Pinecone account

---

## ⚡ Quick Setup (5 Steps)

### **Step 1: Install Dependencies** (1 min)
```powershell
cd "e:\AI Study Companion Pro\backend"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### **Step 2: Get API Keys** (3 min)

#### Google Gemini API Key
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

#### Pinecone API Key
1. Go to: https://www.pinecone.io/
2. Sign up / Log in
3. Create a new project
4. Copy API key and environment from dashboard

### **Step 3: Configure Environment** (30 sec)
```powershell
copy .env.example .env
notepad .env
```

Update these values in `.env`:
```env
# Required - Add your keys
GOOGLE_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment

# Database (update if needed)
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_study_companion

# Optional - Keep defaults or customize
GEMINI_MODEL=gemini-pro
GEMINI_EMBEDDING_MODEL=models/embedding-001
```

### **Step 4: Setup Database** (30 sec)
```powershell
# Create database
createdb ai_study_companion

# Or using psql
psql -U postgres -c "CREATE DATABASE ai_study_companion;"

# Run migrations
alembic upgrade head
```

### **Step 5: Validate & Run** (30 sec)
```powershell
# Validate configuration
python check_config.py

# Start server
python -m uvicorn app.main:app --reload
```

---

## ✅ Verify Installation

### **1. Check API Docs**
Open browser: http://localhost:8000/docs

You should see the interactive API documentation.

### **2. Test Health Endpoint**
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "version": "1.0.0"}
```

### **3. Test RAG Pipeline**

#### Create Embeddings
```powershell
curl -X POST "http://localhost:8000/api/memory/" `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": 1,
    "chat_id": 1,
    "content": "Machine learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models.",
    "content_type": "text"
  }'
```

#### Search with Context
```powershell
curl -X POST "http://localhost:8000/api/memory/search" `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": 1,
    "query": "What is machine learning?",
    "top_k": 3
  }'
```

#### Generate with RAG
```powershell
curl -X POST "http://localhost:8000/api/agents/explain" `
  -H "Content-Type: application/json" `
  -d '{
    "input_text": "Explain machine learning",
    "user_id": 1,
    "chat_id": 1,
    "parameters": {}
  }'
```

---

## 📚 Key Endpoints

### **Memory/RAG Endpoints**
- `POST /api/memory/` - Create embeddings
- `POST /api/memory/search` - Semantic search
- `GET /api/memory/user/{user_id}` - Get user's memories

### **Agent Endpoints**
- `POST /api/agents/summarize` - Summarize text
- `POST /api/agents/generate-questions` - Generate quiz
- `POST /api/agents/explain` - Explain with RAG context
- `POST /api/agents/recommend-resources` - Get resources

### **File Processing**
- `POST /api/files/upload` - Upload PDF/DOCX
- `GET /api/files/{file_id}` - Get file details
- `POST /api/workflow/pdf-processing` - Process PDF with RAG

---

## 🎯 Common Use Cases

### **Use Case 1: Upload and Process PDF**

```powershell
# 1. Upload PDF file
curl -X POST "http://localhost:8000/api/files/upload" `
  -F "file=@document.pdf" `
  -F "user_id=1" `
  -F "chat_id=1"

# Response: {"file_id": 1, "filename": "document.pdf", ...}

# 2. Start PDF processing workflow
curl -X POST "http://localhost:8000/api/workflow/pdf-processing" `
  -H "Content-Type: application/json" `
  -d '{
    "file_id": 1,
    "user_id": 1,
    "chat_id": 1
  }'

# This will:
# - Extract text from PDF
# - Create summary
# - Generate quiz questions
# - Recommend resources
# - Store embeddings for RAG
```

### **Use Case 2: Chat with Context**

```powershell
# 1. Ask a question (uses RAG to find relevant context)
curl -X POST "http://localhost:8000/api/agents/explain" `
  -H "Content-Type: application/json" `
  -d '{
    "input_text": "What are neural networks?",
    "user_id": 1,
    "chat_id": 1,
    "parameters": {}
  }'

# The system will:
# - Generate embedding for the query
# - Search Pinecone for relevant context
# - Use context + Gemini to generate answer
```

### **Use Case 3: Generate Study Materials**

```powershell
# 1. Summarize your notes
curl -X POST "http://localhost:8000/api/agents/summarize" `
  -H "Content-Type: application/json" `
  -d '{
    "input_text": "Your lengthy notes here...",
    "user_id": 1,
    "parameters": {}
  }'

# 2. Generate quiz questions
curl -X POST "http://localhost:8000/api/agents/generate-questions" `
  -H "Content-Type: application/json" `
  -d '{
    "input_text": "Your notes or summary here...",
    "user_id": 1,
    "parameters": {"num_questions": 10}
  }'

# 3. Get learning resources
curl -X POST "http://localhost:8000/api/agents/recommend-resources" `
  -H "Content-Type: application/json" `
  -d '{
    "input_text": "Machine learning and neural networks",
    "user_id": 1,
    "parameters": {"num_resources": 5}
  }'
```

---

## 🔧 Configuration Tips

### **Adjust Model Temperature**
```env
# Lower = more focused, deterministic
# Higher = more creative, varied
GEMINI_TEMPERATURE=0.7  # Default (balanced)
GEMINI_TEMPERATURE=0.3  # More focused
GEMINI_TEMPERATURE=0.9  # More creative
```

### **Change Model**
```env
# Standard model (default)
GEMINI_MODEL=gemini-pro

# Faster, lighter model
GEMINI_MODEL=gemini-1.5-flash

# Most capable model
GEMINI_MODEL=gemini-1.5-pro
```

### **Adjust RAG Parameters**
Edit `app/config/rag_config.py`:
```python
# Chunk size for text splitting
CHUNK_SIZE = 1000  # Larger = more context, fewer chunks
CHUNK_OVERLAP = 200  # Overlap between chunks

# Search parameters
TOP_K_RESULTS = 5  # Number of context chunks to retrieve
SIMILARITY_THRESHOLD = 0.7  # Minimum similarity score
```

---

## 🐛 Troubleshooting

### **Problem: Server won't start**
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: 
```powershell
pip install -r requirements.txt
```

### **Problem: Database connection error**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Solution**: 
1. Check PostgreSQL is running
2. Verify DATABASE_URL in `.env`
3. Create database: `createdb ai_study_companion`

### **Problem: Gemini API error**
```
google.api_core.exceptions.PermissionDenied: 403
```
**Solution**: 
1. Check GOOGLE_API_KEY in `.env`
2. Verify key at https://makersuite.google.com/app/apikey
3. Ensure API is enabled

### **Problem: Pinecone error**
```
pinecone.exceptions.PineconeException: Index not found
```
**Solution**: 
```python
# Create Pinecone index
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="your-key")
pc.create_index(
    name="ai-study-companion",
    dimension=768,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-east-1")
)
```

---

## 📊 Monitor Your System

### **Check Logs**
Server logs show in the terminal:
- API requests
- Database queries
- AI agent calls
- Errors and warnings

### **API Documentation**
Interactive docs with try-it-out feature:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### **Database**
View data using pgAdmin or psql:
```sql
-- Connect
psql -d ai_study_companion

-- Check tables
\dt

-- View memories
SELECT * FROM memories LIMIT 10;
```

---

## 🎓 Next Steps

1. **Read Full Documentation**
   - `README.md` - Overview
   - `SETUP_GUIDE.md` - Detailed setup
   - `RAG_SETUP_COMPLETE.md` - RAG pipeline details
   - `API_DOCUMENTATION.md` - API reference

2. **Explore the Code**
   - `app/config/rag_config.py` - RAG configuration
   - `app/services/rag_service.py` - RAG implementation
   - `app/agents/langchain_agents.py` - AI agents

3. **Customize**
   - Modify prompt templates in `rag_config.py`
   - Add new agents in `langchain_agents.py`
   - Create custom workflows in `langgraph_workflows.py`

4. **Deploy**
   - Docker: `docker-compose up --build`
   - Cloud: Follow deployment guide in `README.md`

---

## 💡 Tips for Best Results

### **1. Quality Input**
- Provide clear, well-structured text
- Break large documents into chunks
- Use meaningful filenames and metadata

### **2. RAG Context**
- Upload relevant documents first
- Build up your knowledge base
- Let embeddings accumulate

### **3. Effective Prompts**
- Be specific in your questions
- Provide context when needed
- Use the explain endpoint for complex topics

### **4. Resource Management**
- Monitor API usage (Gemini has free tier limits)
- Clean up old embeddings if needed
- Use appropriate chunk sizes

---

## 📞 Support

- **Documentation**: Check markdown files in `backend/`
- **Configuration**: Run `python check_config.py`
- **API Issues**: Check `http://localhost:8000/docs`
- **Logs**: Review terminal output

---

## ✅ Success Checklist

- [ ] Dependencies installed
- [ ] API keys configured
- [ ] Database created and migrated
- [ ] Server running on port 8000
- [ ] API docs accessible
- [ ] Test endpoints working
- [ ] RAG pipeline functional

**You're all set! Start building your AI-powered study companion! 🚀**

---

**Last Updated**: December 2, 2025
**Version**: 1.0.0
**Stack**: FastAPI + LangChain + Google Gemini + Pinecone
