# AI Study Companion Pro - System Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                     http://localhost:3000                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                             │
│                  http://localhost:8000/api                       │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              API Layer (FastAPI Routes)                  │   │
│  │  • Users    • Chats     • Messages    • Files           │   │
│  │  • Agents   • Workflow  • Memory                        │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐   │
│  │              Service Layer (Business Logic)              │   │
│  │  • Database Services  • File Service                     │   │
│  │  • Pinecone Service   • Agent Orchestration             │   │
│  └─────┬──────────────────┬──────────────────┬─────────────┘   │
│        │                  │                  │                  │
│  ┌─────▼────┐      ┌──────▼─────┐     ┌─────▼──────┐          │
│  │ Agents   │      │ Workflows  │     │  Utils     │          │
│  │ • Summary│      │ • PDF Proc │     │ • Logger   │          │
│  │ • Q&A    │      │ • MultiChat│     │ • Text Proc│          │
│  │ • Explain│      └────────────┘     └────────────┘          │
│  │ • Resource│                                                 │
│  └──────────┘                                                  │
└───────────────┬──────────────────┬──────────────────┬──────────┘
                │                  │                  │
    ┌───────────▼─────────┐  ┌────▼─────────┐  ┌────▼──────────┐
    │   PostgreSQL DB     │  │Google Gemini │  │   Pinecone    │
    │  • Users            │  │  Gemini 1.5  │  │  Vector Store │
    │  • Chats            │  │  Embeddings  │  │  Semantic     │
    │  • Messages         │  │   API        │  │  Search       │
    │  • Files            │  └──────────────┘  └───────────────┘
    │  • Memories         │
    │  • Resources        │
    │  • Workflows        │
    └─────────────────────┘
```

---

## 📊 Data Flow Diagrams

### 1. PDF Upload & Processing Flow

```
┌──────────┐
│  User    │
│ Uploads  │
│   PDF    │
└────┬─────┘
     │
     ▼
┌─────────────────┐
│ POST /api/files │
└────┬────────────┘
     │
     ▼
┌────────────────────┐
│  File Service      │
│  • Save to storage │
│  • Extract text    │
└────┬───────────────┘
     │
     ▼
┌──────────────────────┐
│  Store in PostgreSQL │
│  • File metadata     │
│  • Extracted text    │
└────┬─────────────────┘
     │
     │ Optional: Run Workflow
     ▼
┌────────────────────────────┐
│ POST /api/workflow/run     │
│ type: pdf_processing       │
└────┬───────────────────────┘
     │
     ▼
┌────────────────────────────┐
│  PDF Processing Workflow   │
│  ┌──────────────────────┐  │
│  │ 1. Summarize         │  │
│  └──────┬───────────────┘  │
│         ▼                  │
│  ┌──────────────────────┐  │
│  │ 2. Generate Questions│  │
│  └──────┬───────────────┘  │
│         ▼                  │
│  ┌──────────────────────┐  │
│  │ 3. Recommend Resources│ │
│  └──────┬───────────────┘  │
│         ▼                  │
│  ┌──────────────────────┐  │
│  │ 4. Create Embeddings │  │
│  └──────┬───────────────┘  │
└─────────┼──────────────────┘
          │
          ▼
    ┌──────────┐
    │ Pinecone │
    │  Store   │
    └──────────┘
```

### 2. Chat Interaction Flow

```
┌──────────────┐
│  User Sends  │
│   Message    │
└──────┬───────┘
       │
       ▼
┌───────────────────┐
│ POST /api/messages│
└──────┬────────────┘
       │
       ▼
┌──────────────────────────┐
│  Identify Agent Type     │
│  (from chat.agent_type)  │
└──────┬───────────────────┘
       │
       ├─────────┬──────────┬──────────┐
       │         │          │          │
       ▼         ▼          ▼          ▼
   ┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
   │Summary │ │ Q&A  │ │Explain │ │ Resource │
   │ Agent  │ │Agent │ │ Agent  │ │  Agent   │
   └────┬───┘ └──┬───┘ └───┬────┘ └────┬─────┘
        │        │         │           │
        └────────┴─────┬───┴───────────┘
                       │
                       ▼
            ┌────────────────────┐
            │  Context Retrieval │
            │  (Pinecone Search) │
            └─────────┬──────────┘
                      │
                      ▼
            ┌────────────────────┐
            │  LangChain Agent   │
            │  Process & Generate│
            └─────────┬──────────┘
                      │
                      ▼
            ┌────────────────────┐
            │  Store Response    │
            │  in Messages       │
            └─────────┬──────────┘
                      │
                      ▼
            ┌────────────────────┐
            │  Optional: Store   │
            │  New Embeddings    │
            └────────────────────┘
```

### 3. Vector Memory Flow

```
┌─────────────────┐
│  Input Text     │
│  (Summary/Q/A)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Gemini Embeddings   │
│  Generate Vector    │
│  (768 dimensions)   │
└────────┬────────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌──────────────┐
│   Pinecone      │  │ PostgreSQL   │
│   Store Vector  │  │ Store Meta   │
│   + Metadata    │  │ + Vector ID  │
└─────────────────┘  └──────────────┘
         │                  │
         └──────────┬───────┘
                    │
         Later: Search Query
                    │
                    ▼
         ┌────────────────────┐
         │  Semantic Search   │
         │  (Cosine Similarity│
         └─────────┬──────────┘
                   │
                   ▼
         ┌────────────────────┐
         │  Return Top-K      │
         │  Similar Chunks    │
         └────────────────────┘
```

---

## 🔄 Component Interaction Matrix

```
┌─────────────┬──────┬──────┬──────┬──────┬──────┬──────┐
│ Component   │ API  │ DB   │ AI   │Work  │Pinec │Files │
├─────────────┼──────┼──────┼──────┼──────┼──────┼──────┤
│ API Routes  │  -   │  ✓   │  ✓   │  ✓   │  ✓   │  ✓   │
│ Database    │  ✓   │  -   │  ✗   │  ✓   │  ✗   │  ✓   │
│ AI Agents   │  ✓   │  ✗   │  -   │  ✓   │  ✓   │  ✗   │
│ Workflows   │  ✓   │  ✓   │  ✓   │  -   │  ✓   │  ✓   │
│ Pinecone    │  ✓   │  ✗   │  ✓   │  ✓   │  -   │  ✗   │
│ File Service│  ✓   │  ✓   │  ✗   │  ✓   │  ✗   │  -   │
└─────────────┴──────┴──────┴──────┴──────┴──────┴──────┘

✓ = Direct interaction
✗ = No direct interaction
```

---

## 🗄️ Database Schema

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ PK: id          │
│    email        │
│    username     │
│    full_name    │
│    created_at   │
└────────┬────────┘
         │ 1
         │
         │ n
    ┌────┴──────────┬────────────┬──────────────┐
    │               │            │              │
┌───▼──────────┐ ┌──▼────────┐ ┌▼──────────┐ ┌─▼─────────┐
│   chats      │ │  files    │ │ memories  │ │ workflows │
├──────────────┤ ├───────────┤ ├───────────┤ ├───────────┤
│ PK: id       │ │ PK: id    │ │ PK: id    │ │ PK: id    │
│ FK: user_id  │ │FK: user_id│ │FK:user_id │ │FK:user_id │
│    title     │ │   filename│ │ vector_id │ │ workflow  │
│    agent_type│ │  file_path│ │   content │ │   status  │
└──────┬───────┘ └─────┬─────┘ └───────────┘ └───────────┘
       │ 1             │ 1
       │               │
       │ n             │ n
   ┌───▼──────┐    ┌───▼──────┐
   │ messages │    │ memories │
   ├──────────┤    ├──────────┤
   │ PK: id   │    │FK:file_id│
   │FK:chat_id│    │vector_id │
   │   role   │    └──────────┘
   │  content │
   │ metadata │
   └──────────┘

   ┌────────────┐
   │ resources  │
   ├────────────┤
   │ PK: id     │
   │FK: chat_id │
   │   title    │
   │   url      │
   │   type     │
   └────────────┘
```

---

## 🤖 AI Agent Architecture

```
                    ┌──────────────┐
                    │  API Request │
                    └──────┬───────┘
                           │
                    ┌──────▼──────────┐
                    │  Agent Factory  │
                    │  get_agent()    │
                    └──────┬──────────┘
                           │
         ┌─────────────────┼─────────────────┬────────────────┐
         │                 │                 │                │
    ┌────▼────┐      ┌─────▼─────┐    ┌────▼────┐    ┌──────▼──────┐
    │Summary  │      │ Question  │    │Explainer│    │  Resource   │
    │ Agent   │      │ Generator │    │  Agent  │    │Recommender  │
    └────┬────┘      └─────┬─────┘    └────┬────┘    └──────┬──────┘
         │                 │                │                │
         └─────────────────┴────────────────┴────────────────┘
                           │
                    ┌──────▼──────────┐
                    │  LangChain      │
                    │  • ChatGemini   │
                    │  • Prompts      │
                    │  • Chains       │
                    └──────┬──────────┘
                           │
                    ┌──────▼──────────┐
                    │  Gemini API     │
                    │  gemini-1.5-    │
                    │    flash        │
                    └─────────────────┘
```

---

## 🔀 Workflow Orchestration (LangGraph)

```
PDF Processing Workflow:

Start
  │
  ▼
┌────────────────┐
│  Summarize     │ ──┐
└────────────────┘   │
  │                  │
  ▼                  │
┌────────────────┐   │  State
│ Generate Q's   │ ──┤  Management
└────────────────┘   │  (TypedDict)
  │                  │
  ▼                  │
┌────────────────┐   │
│ Recommend Res. │ ──┤
└────────────────┘   │
  │                  │
  ▼                  │
┌────────────────┐   │
│Create Embedding│ ──┘
└────────────────┘
  │
  ▼
 End

Multi-Agent Chat Workflow:

Start
  │
  ▼
┌────────────────┐
│ Identify Intent│
└────────────────┘
  │
  ▼
┌────────────────┐
│Retrieve Context│ (Pinecone)
└────────────────┘
  │
  ▼
┌────────────────┐
│Generate Response│ (Agent)
└────────────────┘
  │
  ▼
┌────────────────┐
│Store Embeddings│
└────────────────┘
  │
  ▼
 End
```

---

## 🔐 Security Layers

```
┌─────────────────────────────────────────┐
│          Request from Frontend          │
└──────────────────┬──────────────────────┘
                   │
           ┌───────▼────────┐
           │  CORS Check    │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │ JWT Validation │ (Optional)
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │ Input Validate │ (Pydantic)
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │ Rate Limiting  │ (To implement)
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │  Process       │
           │  Request       │
           └────────────────┘
```

---

## 📦 Deployment Architecture

```
Development:
┌──────────────────────────────────┐
│  Local Machine                   │
│  ┌────────────────────────────┐  │
│  │  Backend (Port 8000)       │  │
│  │  • FastAPI                 │  │
│  │  • SQLite/PostgreSQL       │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘

Production (Docker):
┌──────────────────────────────────┐
│  Docker Host                     │
│  ┌────────────────────────────┐  │
│  │  Backend Container         │  │
│  │  • FastAPI                 │  │
│  │  • Uvicorn                 │  │
│  └────────┬───────────────────┘  │
│           │                      │
│  ┌────────▼───────────────────┐  │
│  │  PostgreSQL Container      │  │
│  │  • Database                │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
           │
    ┌──────┴─────┐
    │            │
┌───▼────┐  ┌────▼──────┐
│Gemini  │  │ Pinecone  │
│  API   │  │  Service  │
└────────┘  └───────────┘

Production (Cloud):
┌─────────────────────────────────────┐
│  Cloud Provider (AWS/GCP/Azure)     │
│  ┌──────────────────────────────┐   │
│  │  Load Balancer               │   │
│  └──────────┬───────────────────┘   │
│             │                       │
│    ┌────────┴────────┐              │
│    │                 │              │
│  ┌─▼────┐         ┌──▼───┐          │
│  │ App  │         │ App  │ (Scaled) │
│  │ Node │         │ Node │          │
│  └──┬───┘         └──┬───┘          │
│     │                │              │
│     └───────┬────────┘              │
│             │                       │
│  ┌──────────▼───────────────┐       │
│  │  Managed PostgreSQL       │       │
│  │  (RDS/Cloud SQL)         │       │
│  └──────────────────────────┘       │
└─────────────────────────────────────┘
```

---

## 🎯 Request/Response Cycle

```
1. User Request
   ↓
2. FastAPI receives request
   ↓
3. CORS validation
   ↓
4. Route matching
   ↓
5. Pydantic validation
   ↓
6. Service layer processing
   ├─→ Database queries (PostgreSQL)
   ├─→ File operations (Storage)
   ├─→ AI agent calls (Google Gemini)
   └─→ Vector searches (Pinecone)
   ↓
7. Response formatting
   ↓
8. Return to client
```

---

## 📊 Performance Considerations

```
┌──────────────────────────┐
│  Async Operations        │
│  • All I/O is async      │
│  • Non-blocking          │
└──────────────────────────┘
┌──────────────────────────┐
│  Connection Pooling      │
│  • Database: 10 + 20     │
│  • Reuse connections     │
└──────────────────────────┘
┌──────────────────────────┐
│  Caching (Future)        │
│  • Redis for hot data    │
│  • Reduce DB queries     │
└──────────────────────────┘
┌──────────────────────────┐
│  Load Balancing          │
│  • Horizontal scaling    │
│  • Multiple instances    │
└──────────────────────────┘
```

---

This architecture is designed to be:
- **Scalable**: Easy to add more instances
- **Maintainable**: Clear separation of concerns
- **Extensible**: Simple to add new features
- **Reliable**: Proper error handling
- **Performant**: Async operations throughout
- **Secure**: Multiple security layers

---

*Architecture subject to evolution based on requirements*
