# System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│  HTTP Client  │  Streamlit UI  │  Python SDK  │  curl/Postman      │
└────────┬────────────────┬────────────┬────────────────┬──────────────┘
         │                │            │                │
         └────────────────┴────────────┴────────────────┘
                            │
                    ┌───────▼────────┐
                    │   FastAPI      │
                    │   Application  │
                    └───────┬────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼─────┐    ┌──────▼──────┐    ┌────▼─────┐
    │ Upload   │    │   Query     │    │  Admin   │
    │ Routes   │    │   Routes    │    │  Routes  │
    └────┬─────┘    └──────┬──────┘    └────┬─────┘
         │                  │                 │
         └──────────────────┼─────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼────────┐  ┌─────▼──────┐   ┌──────▼─────┐
    │  Document   │  │     QA     │   │   Admin    │
    │  Service    │  │  Service   │   │  Service   │
    └────┬────────┘  └─────┬──────┘   └──────┬─────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │                       │                       │
┌───▼────────┐    ┌─────────▼─────────┐    ┌──────▼──────┐
│ Ingestion  │    │    Retrieval      │    │     LLM     │
│  Pipeline  │    │     System        │    │ Integration │
└───┬────────┘    └─────────┬─────────┘    └──────┬──────┘
    │                       │                      │
    │                       │                      │
┌───▼─────────────────┐    │              ┌───────▼────────┐
│  Text Extraction    │    │              │  OpenAI API    │
│  Chunking          │    │              │  Anthropic API │
│  Embeddings        │    │              │  Local Models  │
│  FAISS Indexing    │    │              └────────────────┘
└───┬─────────────────┘    │
    │                      │
    └──────────┬───────────┘
               │
    ┌──────────▼──────────┐
    │   Data Layer        │
    ├─────────────────────┤
    │  SQLite Database    │
    │  FAISS Index        │
    │  File Storage       │
    └─────────────────────┘
```

## Data Flow - Document Upload

```
User uploads PDF
       │
       ▼
┌─────────────────┐
│  Upload Route   │ ──► Validate file type & size
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document Service│ ──► Save to disk
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PDF Extractor  │ ──► Extract text & metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text Chunker   │ ──► Split into chunks with overlap
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Embedder     │ ──► Generate embeddings
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FAISS Index    │ ──► Add vectors to index
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Database     │ ──► Store chunks & metadata
└─────────────────┘
         │
         ▼
    Return success
```

## Data Flow - Question Answering

```
User asks question
       │
       ▼
┌─────────────────┐
│  Query Route    │ ──► Validate request
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   QA Service    │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│    Embedder     │  │   Retriever     │
│ (Query→Vector)  │  │ (Search Index)  │
└────────┬────────┘  └────────┬────────┘
         │                    │
         └──────┬─────────────┘
                │
                ▼
       ┌─────────────────┐
       │  FAISS Search   │ ──► Find top-k similar chunks
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │    Database     │ ──► Enrich with metadata
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │  LLM Provider   │ ──► Generate answer
       │ (GPT/Claude)    │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Format Response │ ──► Add sources & citations
       └────────┬────────┘
                │
                ▼
       Return answer with sources
```

## Component Dependencies

```
┌─────────────────────────────────────────────────┐
│              FastAPI Application                │
│                                                 │
│  ┌────────────────────────────────────────┐    │
│  │         API Routes Layer              │    │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │    │
│  │  │Upload│ │Query │ │Admin │ │Health│ │    │
│  │  └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘ │    │
│  └──────┼────────┼────────┼────────┼─────┘    │
│         │        │        │        │          │
│  ┌──────┼────────┼────────┼────────┼─────┐    │
│  │      │        │        │        │     │    │
│  │  ┌───▼──┐ ┌──▼────┐ ┌─▼────┐ ┌▼────┐│    │
│  │  │Doc   │ │QA     │ │Admin │ │Stats││    │
│  │  │Svc   │ │Svc    │ │Svc   │ │Svc  ││    │
│  │  └───┬──┘ └──┬────┘ └──┬───┘ └─┬───┘│    │
│  └──────┼───────┼─────────┼────────┼─────┘    │
│         │       │         │        │          │
│  ┌──────▼───────▼─────────▼────────▼─────┐    │
│  │         Core Components               │    │
│  │  ┌──────────┐ ┌──────────┐ ┌────────┐│    │
│  │  │Ingestion │ │Retrieval │ │  LLM   ││    │
│  │  │          │ │          │ │        ││    │
│  │  │Extract   │ │Retriever │ │OpenAI  ││    │
│  │  │Chunker   │ │Ranker    │ │Claude  ││    │
│  │  │Embedder  │ │          │ │Local   ││    │
│  │  │Indexer   │ │          │ │        ││    │
│  │  └────┬─────┘ └────┬─────┘ └───┬────┘│    │
│  └───────┼────────────┼──────────┬─┼─────┘    │
│          │            │          │ │          │
└──────────┼────────────┼──────────┼─┼──────────┘
           │            │          │ │
    ┌──────▼────────────▼──────────▼─▼──────┐
    │         Data Layer                     │
    │  ┌──────────┐ ┌──────────┐ ┌────────┐│
    │  │ SQLite   │ │  FAISS   │ │  File  ││
    │  │ Database │ │  Index   │ │Storage ││
    │  └──────────┘ └──────────┘ └────────┘│
    └────────────────────────────────────────┘
```

## Database Schema

```
┌─────────────────────────┐
│      Documents          │
├─────────────────────────┤
│ id (PK)                 │
│ filename                │
│ file_type               │
│ file_size               │
│ upload_date             │
│ status                  │
│ total_chunks            │
│ error_message           │
│ metadata (JSON)         │
└────────┬────────────────┘
         │ 1
         │
         │ N
┌────────▼────────────────┐
│       Chunks            │
├─────────────────────────┤
│ id (PK)                 │
│ doc_id (FK)             │
│ chunk_index             │
│ chunk_text              │
│ start_char              │
│ end_char                │
│ faiss_id                │
│ embedding_id            │
│ metadata (JSON)         │
│ created_at              │
└─────────────────────────┘

┌─────────────────────────┐
│       Queries           │
├─────────────────────────┤
│ id (PK)                 │
│ query_text              │
│ response                │
│ timestamp               │
│ processing_time         │
│ retrieved_chunks (JSON) │
│ top_k                   │
│ llm_provider            │
│ error_message           │
└─────────────────────────┘
```

## Technology Stack Layers

```
┌──────────────────────────────────────────┐
│           Presentation Layer             │
│  Streamlit UI  │  HTTP API  │  CLI      │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│          Application Layer               │
│  FastAPI │ Pydantic │ Dependencies       │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│           Business Logic Layer           │
│  DocumentService  │  QAService           │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│            Core Domain Layer             │
│ Ingestion │ Retrieval │ LLM Integration  │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│          Infrastructure Layer            │
│  Database  │  FAISS  │  File System      │
└──────────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│          External Services               │
│  OpenAI  │  Anthropic  │  HuggingFace    │
└──────────────────────────────────────────┘
```

## Deployment Architecture

```
                    Internet
                       │
                       ▼
              ┌────────────────┐
              │  Load Balancer │
              └───────┬────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
   │ API     │  │ API     │  │ API     │
   │ Server 1│  │ Server 2│  │ Server 3│
   └────┬────┘  └────┬────┘  └────┬────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
   │Database │  │  FAISS  │  │  Redis  │
   │(Primary)│  │  Index  │  │  Cache  │
   └────┬────┘  └─────────┘  └─────────┘
        │
   ┌────▼────┐
   │Database │
   │(Replica)│
   └─────────┘
```

---

This architecture provides:
- ✅ Separation of concerns
- ✅ Scalability
- ✅ Maintainability  
- ✅ Testability
- ✅ Extensibility
