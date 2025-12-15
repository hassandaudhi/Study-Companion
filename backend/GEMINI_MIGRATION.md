# OpenAI to Google Gemini Migration Guide

## 📋 Migration Summary

This document explains the migration from OpenAI to Google Gemini API in the AI Study Companion Pro backend.

---

## 🔄 Key Changes

### **1. Dependencies**

#### Before (OpenAI)
```txt
openai==1.10.0
langchain-openai==0.0.5
```

#### After (Gemini)
```txt
langchain-google-genai==0.0.6
google-generativeai==0.3.2
```

---

### **2. Environment Variables**

#### Before (OpenAI)
```env
OPENAI_API_KEY=sk-your-openai-api-key
```

#### After (Gemini)
```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-pro
GEMINI_EMBEDDING_MODEL=models/embedding-001
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_OUTPUT_TOKENS=2048
```

---

### **3. Configuration Files**

#### Before (settings.py)
```python
OPENAI_API_KEY: str
```

#### After (settings.py)
```python
GOOGLE_API_KEY: str
GEMINI_MODEL: str = "gemini-pro"
GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
GEMINI_TEMPERATURE: float = 0.7
GEMINI_MAX_OUTPUT_TOKENS: int = 2048
```

---

### **4. Agent Implementation**

#### Before (OpenAI)
```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=settings.OPENAI_API_KEY
)

embeddings = OpenAIEmbeddings(
    openai_api_key=settings.OPENAI_API_KEY
)
```

#### After (Gemini)
```python
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from app.config.rag_config import RAGConfig

# Use centralized configuration
llm = RAGConfig.get_llm()

embeddings = RAGConfig.get_embeddings()
```

---

### **5. Embedding Dimensions**

#### Before (OpenAI)
- Embedding dimensions: **1536**
- Model: `text-embedding-ada-002`

#### After (Gemini)
- Embedding dimensions: **768**
- Model: `models/embedding-001`

⚠️ **Important**: Pinecone index dimension updated to 768

---

### **6. Prompt Structure**

#### Before (Direct in code)
```python
def summarize(self, text: str):
    prompt = f"Summarize this text: {text}"
    response = self.llm.invoke(prompt)
    return response
```

#### After (Centralized in rag_config.py)
```python
def summarize(self, text: str):
    messages = [
        {"role": "system", "content": RAGConfig.SUMMARIZER_SYSTEM_PROMPT},
        {"role": "user", "content": text}
    ]
    response = self.llm.invoke(messages)
    return response
```

---

## 🆕 New Features Added

### **1. RAG Service** (`app/services/rag_service.py`)
Complete RAG pipeline implementation:
- Text chunking
- Embedding generation
- Vector storage
- Context retrieval
- RAG-powered generation

### **2. Centralized Configuration** (`app/config/rag_config.py`)
Single source of truth for:
- Model settings
- Prompt templates
- RAG parameters
- Helper methods

### **3. Enhanced Memory API** (`app/api/memory.py`)
Improved endpoints using RAG service:
- Create embeddings
- Search with context
- Retrieve relevant chunks

---

## 📝 File Changes Summary

### **Modified Files**
1. ✅ `requirements.txt` - Updated dependencies
2. ✅ `.env.example` - New environment variables
3. ✅ `app/config/settings.py` - Gemini configuration
4. ✅ `app/agents/langchain_agents.py` - All agents updated
5. ✅ `app/services/pinecone_service.py` - Gemini embeddings
6. ✅ `app/api/memory.py` - RAG service integration
7. ✅ `check_config.py` - Gemini validation
8. ✅ `docker-compose.yml` - Environment variables
9. ✅ All documentation files

### **New Files**
1. 🆕 `app/config/rag_config.py` - Centralized RAG configuration
2. 🆕 `app/services/rag_service.py` - RAG pipeline service
3. 🆕 `RAG_SETUP_COMPLETE.md` - Setup documentation
4. 🆕 `GEMINI_MIGRATION.md` - This file

### **Deleted/Removed**
1. ❌ All OpenAI imports
2. ❌ OPENAI_API_KEY references
3. ❌ langchain-openai dependencies

---

## 🚀 Migration Steps for Developers

If you're working with this codebase:

### **Step 1: Update Dependencies**
```powershell
pip install -r requirements.txt
```

### **Step 2: Update Environment**
```powershell
# Remove old variables from .env
# OPENAI_API_KEY=...

# Add new variables
GOOGLE_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-pro
GEMINI_EMBEDDING_MODEL=models/embedding-001
```

### **Step 3: Recreate Pinecone Index**
```python
# The embedding dimension changed from 1536 to 768
# You need to recreate your Pinecone index

from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="your-key")

# Delete old index (if exists)
if "ai-study-companion" in pc.list_indexes().names():
    pc.delete_index("ai-study-companion")

# Create new index with correct dimensions
pc.create_index(
    name="ai-study-companion",
    dimension=768,  # Changed from 1536
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)
```

### **Step 4: Validate Setup**
```powershell
python check_config.py
```

### **Step 5: Test the System**
```powershell
python -m uvicorn app.main:app --reload
```

---

## 🔍 Code Comparison

### **Creating an Agent - Before**
```python
from langchain_openai import ChatOpenAI
from app.config.settings import settings

class MyAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def process(self, text: str):
        prompt = f"Process this: {text}"
        return self.llm.invoke(prompt)
```

### **Creating an Agent - After**
```python
from app.config.rag_config import RAGConfig

class MyAgent:
    def __init__(self):
        # Use centralized config
        self.llm = RAGConfig.get_llm()
    
    def process(self, text: str):
        messages = [
            {"role": "system", "content": "Your system prompt here"},
            {"role": "user", "content": text}
        ]
        return self.llm.invoke(messages)
```

---

## 💡 Best Practices

### **1. Use Centralized Config**
❌ Don't create LLM instances directly
```python
# Don't do this
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-pro")
```

✅ Use RAG config
```python
# Do this
from app.config.rag_config import RAGConfig
llm = RAGConfig.get_llm()
```

### **2. Use System Prompts from Config**
❌ Don't hardcode prompts
```python
# Don't do this
prompt = "You are a helpful assistant. Summarize this text."
```

✅ Use configured prompts
```python
# Do this
from app.config.rag_config import RAGConfig
system_prompt = RAGConfig.SUMMARIZER_SYSTEM_PROMPT
```

### **3. Leverage RAG Service**
❌ Don't implement RAG manually
```python
# Don't do this
embeddings = get_embeddings(text)
results = pinecone.query(embeddings)
context = extract_context(results)
response = llm.invoke(f"Context: {context}\nQuestion: {query}")
```

✅ Use RAG service
```python
# Do this
from app.services.rag_service import RAGService
response = await RAGService.generate_with_context(
    query="Your question",
    user_id=1,
    chat_id=1
)
```

---

## 📊 Performance Comparison

| Metric | OpenAI | Gemini |
|--------|--------|--------|
| Embedding Dimensions | 1536 | 768 |
| API Response Time | ~1-2s | ~1-2s |
| Cost (per 1M tokens) | $0.50 | $0.50 |
| Context Window | 4K-128K | 32K |
| Free Tier | Limited | 60 req/min |

---

## ⚠️ Breaking Changes

1. **Pinecone Index Dimensions**: Changed from 1536 to 768
   - Requires recreating Pinecone index
   - Existing embeddings are incompatible

2. **Environment Variables**: Different variable names
   - `OPENAI_API_KEY` → `GOOGLE_API_KEY`
   - Added model-specific configs

3. **Import Paths**: Updated import statements
   - `langchain_openai` → `langchain_google_genai`

---

## 🐛 Common Issues & Solutions

### **Issue 1: Import Error**
```
ModuleNotFoundError: No module named 'openai'
```
**Solution**: Run `pip install -r requirements.txt`

### **Issue 2: API Key Invalid**
```
google.api_core.exceptions.PermissionDenied: 403
```
**Solution**: Verify `GOOGLE_API_KEY` in `.env` file

### **Issue 3: Dimension Mismatch**
```
Pinecone index dimension mismatch: expected 1536, got 768
```
**Solution**: Recreate Pinecone index with dimension=768

### **Issue 4: Missing Config**
```
AttributeError: 'Settings' object has no attribute 'OPENAI_API_KEY'
```
**Solution**: Update `.env` with Gemini variables

---

## 📚 Additional Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **LangChain Gemini Integration**: https://python.langchain.com/docs/integrations/chat/google_generative_ai
- **Pinecone Documentation**: https://docs.pinecone.io/

---

## ✅ Verification Checklist

After migration, verify:

- [ ] All dependencies installed
- [ ] `.env` file updated with Gemini credentials
- [ ] Pinecone index recreated with dimension=768
- [ ] `check_config.py` passes all checks
- [ ] Server starts without errors
- [ ] API docs accessible at `/docs`
- [ ] Agent endpoints working
- [ ] RAG pipeline functioning
- [ ] File upload and processing working
- [ ] Memory/embedding creation successful

---

**Migration Date**: December 2, 2025
**Migrated By**: AI Study Companion Pro Team
**Status**: ✅ Complete
