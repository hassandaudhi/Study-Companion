# 🏗️ RAG Pipeline Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Study Companion Pro                        │
│                   Backend Architecture                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Frontend/Client                           │
│                  (React/Next.js/Mobile App)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌────────────┐  ┌─────────────┐  ┌────────────┐               │
│  │   Users    │  │    Chats    │  │  Messages  │               │
│  │    API     │  │     API     │  │     API    │               │
│  └────────────┘  └─────────────┘  └────────────┘               │
│  ┌────────────┐  ┌─────────────┐  ┌────────────┐               │
│  │   Files    │  │   Agents    │  │  Workflow  │               │
│  │    API     │  │     API     │  │     API    │               │
│  └────────────┘  └─────────────┘  └────────────┘               │
│  ┌────────────┐                                                 │
│  │   Memory   │  ← RAG Endpoints                                │
│  │    API     │                                                 │
│  └────────────┘                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │ Google Gemini│ │   Pinecone   │
│   Database   │ │      API     │ │Vector Database│
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## RAG Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Pipeline Flow                             │
└─────────────────────────────────────────────────────────────────┘

1. INPUT
┌─────────────────┐
│  User uploads   │
│  PDF/DOCX/Text  │
└────────┬────────┘
         │
         ▼
2. TEXT EXTRACTION
┌─────────────────────────────┐
│   File Service              │
│   • PyPDF2 (PDF)            │
│   • python-docx (DOCX)      │
│   • Direct (TXT)            │
└────────┬────────────────────┘
         │ Raw text
         ▼
3. TEXT CHUNKING
┌──────────────────────────────────┐
│   RAG Service                    │
│   RecursiveCharacterTextSplitter │
│   • Chunk size: 1000 chars       │
│   • Overlap: 200 chars           │
└────────┬─────────────────────────┘
         │ Text chunks
         ▼
4. EMBEDDING GENERATION
┌──────────────────────────────────┐
│   Google Gemini Embeddings       │
│   • Model: embedding-001         │
│   • Dimension: 768               │
└────────┬─────────────────────────┘
         │ Vector embeddings
         ▼
5. VECTOR STORAGE
┌──────────────────────────────────┐
│   Pinecone Service               │
│   • Store vectors                │
│   • Add metadata                 │
│   • Namespace: user_{id}         │
└────────┬─────────────────────────┘
         │
         ▼
6. METADATA STORAGE
┌──────────────────────────────────┐
│   PostgreSQL Database            │
│   • Memory records               │
│   • Vector IDs                   │
│   • User/chat associations       │
└──────────────────────────────────┘
```

---

## Query & Response Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                Query Processing with RAG                         │
└─────────────────────────────────────────────────────────────────┘

1. USER QUERY
┌─────────────────┐
│ "Explain        │
│  neural         │
│  networks"      │
└────────┬────────┘
         │
         ▼
2. QUERY EMBEDDING
┌──────────────────────────────────┐
│   RAG Service                    │
│   • Generate query embedding     │
│   • Use Gemini embeddings        │
└────────┬─────────────────────────┘
         │ Query vector
         ▼
3. SEMANTIC SEARCH
┌──────────────────────────────────┐
│   Pinecone Service               │
│   • Cosine similarity search     │
│   • Filter by user namespace     │
│   • Return top-K results (5)     │
└────────┬─────────────────────────┘
         │ Relevant chunks
         ▼
4. CONTEXT RETRIEVAL
┌──────────────────────────────────┐
│   RAG Service                    │
│   • Extract text from results    │
│   • Combine into context         │
│   • Add relevance scores         │
└────────┬─────────────────────────┘
         │ Context string
         ▼
5. PROMPT CONSTRUCTION
┌──────────────────────────────────┐
│   Agent (Explainer)              │
│   • System prompt                │
│   • Retrieved context            │
│   • User query                   │
└────────┬─────────────────────────┘
         │ Complete prompt
         ▼
6. LLM GENERATION
┌──────────────────────────────────┐
│   Google Gemini API              │
│   • Model: gemini-pro            │
│   • Temperature: 0.7             │
│   • Max tokens: 2048             │
└────────┬─────────────────────────┘
         │ Generated response
         ▼
7. RESPONSE
┌──────────────────────────────────┐
│   "Neural networks are           │
│    computational models...       │
│    [uses context from docs]"     │
└──────────────────────────────────┘
```

---

## Agent System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI Agent System                              │
└─────────────────────────────────────────────────────────────────┘

                    ┌────────────────┐
                    │   RAG Config   │
                    │  rag_config.py │
                    └────────┬───────┘
                             │ Provides
                             ▼
          ┌──────────────────────────────────┐
          │  • LLM instances                 │
          │  • Embedding models              │
          │  • Prompt templates              │
          │  • Configuration parameters      │
          └──────────────────┬───────────────┘
                             │ Used by
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Summarizer      │ │ Question         │ │  Explainer       │
│  Agent           │ │ Generator        │ │  Agent           │
│                  │ │ Agent            │ │  (with RAG)      │
│  • Get LLM       │ │                  │ │                  │
│  • Use prompt    │ │  • Get LLM       │ │  • Retrieve ctx  │
│  • Generate      │ │  • Use prompt    │ │  • Get LLM       │
│    summary       │ │  • Generate Qs   │ │  • Explain       │
└──────────────────┘ └──────────────────┘ └──────────────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Google Gemini │
                    │      API       │
                    └────────────────┘
```

---

## Workflow Orchestration (LangGraph)

```
┌─────────────────────────────────────────────────────────────────┐
│              PDF Processing Workflow (LangGraph)                 │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│  Start PDF   │
│  Processing  │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│  1. Summarize       │
│     • Extract key   │
│       points        │
│     • Create summary│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  2. Generate        │
│     Questions       │
│     • Based on      │
│       summary       │
│     • 5 questions   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  3. Recommend       │
│     Resources       │
│     • Based on      │
│       topic         │
│     • 5 resources   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  4. Create          │
│     Embeddings      │
│     • Chunk text    │
│     • Store vectors │
└──────┬──────────────┘
       │
       ▼
┌──────────────┐
│   Complete   │
│   Return all │
│   results    │
└──────────────┘
```

---

## Configuration Management

```
┌─────────────────────────────────────────────────────────────────┐
│                  Configuration Hierarchy                         │
└─────────────────────────────────────────────────────────────────┘

1. ENVIRONMENT VARIABLES
┌──────────────────────────────┐
│         .env file            │
│  • GOOGLE_API_KEY            │
│  • GEMINI_MODEL              │
│  • GEMINI_EMBEDDING_MODEL    │
│  • GEMINI_TEMPERATURE        │
│  • GEMINI_MAX_OUTPUT_TOKENS  │
└────────┬─────────────────────┘
         │ Loaded by
         ▼
2. SETTINGS
┌──────────────────────────────┐
│   app/config/settings.py     │
│   • BaseSettings (Pydantic)  │
│   • Environment validation   │
│   • Type checking            │
└────────┬─────────────────────┘
         │ Used by
         ▼
3. RAG CONFIG
┌──────────────────────────────┐
│  app/config/rag_config.py    │
│  • LLM factory methods       │
│  • Embedding factory         │
│  • Prompt templates          │
│  • RAG parameters            │
└────────┬─────────────────────┘
         │ Used by
         ▼
4. APPLICATION COMPONENTS
┌──────────────────────────────┐
│  • Agents                    │
│  • Services                  │
│  • Workflows                 │
│  • API endpoints             │
└──────────────────────────────┘

** Change model = Update .env only! **
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Complete Data Flow                          │
└─────────────────────────────────────────────────────────────────┘

USER ACTION: Upload PDF
    │
    ▼
┌─────────────────────────────┐
│  1. File Upload             │
│     POST /api/files/upload  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  2. Store in PostgreSQL     │
│     • File metadata         │
│     • User association      │
│     • File path             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  3. Extract Text            │
│     • PyPDF2 service        │
│     • Parse document        │
└────────┬────────────────────┘
         │ Raw text
         ▼
┌─────────────────────────────┐
│  4. Start Workflow          │
│     POST /api/workflow/     │
│     pdf-processing          │
└────────┬────────────────────┘
         │
         ├─────────┐
         │         │
         ▼         ▼
    ┌─────────┐ ┌──────────────┐
    │Summarize│ │Create        │
    │         │ │Embeddings    │
    └────┬────┘ └──────┬───────┘
         │             │
         ▼             ▼
    ┌─────────┐   ┌──────────────┐
    │Generate │   │Store in      │
    │Questions│   │Pinecone      │
    └────┬────┘   └──────┬───────┘
         │               │
         ▼               ▼
    ┌─────────┐   ┌──────────────┐
    │Recommend│   │Store metadata│
    │Resources│   │in PostgreSQL │
    └────┬────┘   └──────────────┘
         │
         ▼
┌─────────────────────────────┐
│  5. Return Results          │
│     • Summary               │
│     • Questions             │
│     • Resources             │
│     • Status: complete      │
└─────────────────────────────┘
```

---

## Service Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      API Endpoints                               │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┬──────────────────┐
         │                  │                  │                  │
         ▼                  ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐
│ Database        │ │ RAG Service     │ │ Pinecone        │ │ File Service │
│ Services        │ │                 │ │ Service         │ │              │
│                 │ │                 │ │                 │ │              │
│ • Users         │ │ • chunk_text()  │ │ • upsert()      │ │ • upload()   │
│ • Chats         │ │ • create_       │ │ • query()       │ │ • extract()  │
│ • Messages      │ │   embeddings()  │ │ • delete()      │ │ • delete()   │
│ • Files         │ │ • store_        │ │ • create_index()│ │              │
│ • Memories      │ │   embeddings()  │ │                 │ │              │
│ • Workflows     │ │ • retrieve_     │ │                 │ │              │
│                 │ │   context()     │ │                 │ │              │
│                 │ │ • generate_     │ │                 │ │              │
│                 │ │   with_context()│ │                 │ │              │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └──────┬───────┘
         │                   │                   │                  │
         ▼                   ▼                   ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐
│   PostgreSQL    │ │ Google Gemini   │ │    Pinecone     │ │ File System  │
└─────────────────┘ └─────────────────┘ └─────────────────┘ └──────────────┘
```

---

## Security & Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  Authentication Flow (Optional)                  │
└─────────────────────────────────────────────────────────────────┘

1. User Login
┌──────────────┐
│   Client     │
│   Request    │
└──────┬───────┘
       │ POST /api/auth/login
       ▼
┌──────────────────┐
│  Verify          │
│  Credentials     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Generate JWT    │
│  Token           │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Return Token    │
└──────────────────┘

2. Protected Request
┌──────────────┐
│   Client     │
│   + Token    │
└──────┬───────┘
       │ Authorization: Bearer <token>
       ▼
┌──────────────────┐
│  Verify Token    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Process Request │
└──────────────────┘
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Production Deployment                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Load Balancer                               │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├────────────────┬────────────────┐
         │                │                │
         ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  FastAPI        │ │  FastAPI        │ │  FastAPI        │
│  Instance 1     │ │  Instance 2     │ │  Instance 3     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  PostgreSQL     │ │ Google Gemini   │ │   Pinecone      │
│  (Managed)      │ │     API         │ │  (Managed)      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Technology Stack Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    Technology Stack                              │
└─────────────────────────────────────────────────────────────────┘

Backend Framework
    ├─ FastAPI 0.109.0
    └─ Uvicorn 0.27.0

Database
    ├─ PostgreSQL 13+
    ├─ SQLAlchemy 2.0.25
    └─ Alembic 1.13.1

AI & LangChain
    ├─ LangChain 0.1.0
    ├─ LangGraph 0.0.20
    ├─ langchain-google-genai 0.0.6
    └─ google-generativeai 0.3.2

Vector Database
    └─ Pinecone Client 3.0.2

File Processing
    ├─ PyPDF2 3.0.1
    ├─ python-docx 1.1.0
    └─ aiofiles 23.2.1

Utilities
    ├─ Pydantic 2.5.3
    ├─ python-dotenv 1.0.0
    └─ httpx 0.26.0

Testing
    ├─ pytest 7.4.4
    └─ pytest-asyncio 0.23.3
```

---

**This architecture provides:**
- ✅ Scalable RAG pipeline
- ✅ Centralized configuration
- ✅ Modular design
- ✅ Production-ready
- ✅ Easy to maintain
