# API Reference Guide

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required. For production, implement API key authentication.

---

## 📄 Document Management

### Upload Document
Upload a document for processing and indexing.

**Endpoint:** `POST /api/v1/upload`

**Content-Type:** `multipart/form-data`

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@document.pdf"
```

**Response:** `200 OK`
```json
{
  "doc_id": "a1b2c3d4e5f6g7h8",
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1048576,
  "status": "completed",
  "message": "Document uploaded and processed successfully"
}
```

**Supported File Types:**
- PDF (.pdf)
- Microsoft Word (.docx, .doc)
- Text files (.txt, .md)

**Max File Size:** 50 MB (configurable in `.env`)

---

### List Documents
Get a list of all uploaded documents.

**Endpoint:** `GET /api/v1/documents`

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records (default: 100)

**Request:**
```bash
curl "http://localhost:8000/api/v1/documents?skip=0&limit=10"
```

**Response:** `200 OK`
```json
{
  "documents": [
    {
      "id": "a1b2c3d4e5f6g7h8",
      "filename": "document.pdf",
      "file_type": "pdf",
      "file_size": 1048576,
      "upload_date": "2024-01-15T10:30:00",
      "status": "completed",
      "total_chunks": 42,
      "error_message": null,
      "metadata": {
        "total_pages": 10,
        "author": "John Doe"
      }
    }
  ],
  "total": 1
}
```

---

### Get Document Details
Retrieve details for a specific document.

**Endpoint:** `GET /api/v1/documents/{doc_id}`

**Request:**
```bash
curl "http://localhost:8000/api/v1/documents/a1b2c3d4e5f6g7h8"
```

**Response:** `200 OK`
```json
{
  "id": "a1b2c3d4e5f6g7h8",
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1048576,
  "upload_date": "2024-01-15T10:30:00",
  "status": "completed",
  "total_chunks": 42,
  "error_message": null,
  "metadata": {
    "total_pages": 10,
    "author": "John Doe"
  }
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Document not found"
}
```

---

### Delete Document
Delete a document and all associated data.

**Endpoint:** `DELETE /api/v1/documents/{doc_id}`

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/a1b2c3d4e5f6g7h8"
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Document a1b2c3d4e5f6g7h8 deleted successfully",
  "deleted_count": 1
}
```

---

## 💬 Question Answering

### Ask Question
Submit a question and receive an AI-generated answer with sources.

**Endpoint:** `POST /api/v1/query`

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "query": "What are the main findings?",
  "top_k": 5,
  "min_score": 0.7,
  "include_sources": true
}
```

**Parameters:**
- `query` (required): The question to ask (1-1000 characters)
- `top_k` (optional): Number of chunks to retrieve (1-20, default: 5)
- `min_score` (optional): Minimum similarity score (0-1, default: 0.7)
- `include_sources` (optional): Include source citations (default: true)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main findings?",
    "top_k": 5,
    "include_sources": true
  }'
```

**Response:** `200 OK`
```json
{
  "query": "What are the main findings?",
  "answer": "The main findings indicate that...",
  "sources": [
    {
      "document": "research_paper.pdf",
      "chunk_index": 5,
      "chunk_text": "Our research shows that...",
      "score": 0.89,
      "start_char": 1250,
      "end_char": 1750,
      "page": 3,
      "metadata": {
        "page_number": 3
      }
    }
  ],
  "processing_time": 0.45,
  "retrieved_count": 5,
  "llm_provider": "remote"
}
```

---

### Get Query History
Retrieve past queries and their responses.

**Endpoint:** `GET /api/v1/queries`

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records (default: 50)

**Request:**
```bash
curl "http://localhost:8000/api/v1/queries?limit=10"
```

**Response:** `200 OK`
```json
{
  "queries": [
    {
      "id": 1,
      "query_text": "What are the main findings?",
      "response": "The main findings indicate that...",
      "timestamp": "2024-01-15T10:35:00",
      "processing_time": 0.45,
      "top_k": 5
    }
  ],
  "total": 1
}
```

---

### Get Specific Query
Retrieve details for a specific query.

**Endpoint:** `GET /api/v1/queries/{query_id}`

**Request:**
```bash
curl "http://localhost:8000/api/v1/queries/1"
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "query_text": "What are the main findings?",
  "response": "The main findings indicate that...",
  "timestamp": "2024-01-15T10:35:00",
  "processing_time": 0.45,
  "retrieved_chunks": [
    {
      "chunk_id": 15,
      "score": 0.89
    }
  ],
  "top_k": 5,
  "llm_provider": "remote"
}
```

---

## 🔧 Admin Operations

### Get System Statistics
Retrieve comprehensive system statistics.

**Endpoint:** `GET /api/v1/admin/stats`

**Request:**
```bash
curl "http://localhost:8000/api/v1/admin/stats"
```

**Response:** `200 OK`
```json
{
  "total_documents": 10,
  "total_chunks": 420,
  "total_queries": 35,
  "index_size": 420,
  "database_size": 2048000,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "index_type": "IndexFlatIP"
}
```

---

### Reindex Documents
Rebuild the FAISS index from documents.

**Endpoint:** `POST /api/v1/admin/reindex`

**Content-Type:** `application/json`

**Request Body (Reindex All):**
```json
{}
```

**Request Body (Reindex Specific):**
```json
{
  "doc_ids": ["doc-id-1", "doc-id-2"]
}
```

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/admin/reindex" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Successfully reindexed 10 documents",
  "reindexed_count": 10,
  "total_chunks": 420
}
```

---

### Clear All Data
Delete all documents, chunks, and queries. **Use with caution!**

**Endpoint:** `DELETE /api/v1/admin/clear-all`

**Query Parameters:**
- `confirm` (required): Must be set to `true` to proceed

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/clear-all?confirm=true"
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Cleared all data successfully",
  "deleted_count": 465
}
```

---

## 🏥 Health & Status

### Health Check
Basic health check endpoint.

**Endpoint:** `GET /health`

**Request:**
```bash
curl "http://localhost:8000/health"
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:40:00",
  "database_connected": true,
  "index_loaded": true
}
```

---

### Detailed Status
Get detailed system status and statistics.

**Endpoint:** `GET /api/v1/status`

**Request:**
```bash
curl "http://localhost:8000/api/v1/status"
```

**Response:** `200 OK`
```json
{
  "status": "operational",
  "version": "1.0.0",
  "uptime": 3600.5,
  "stats": {
    "total_documents": 10,
    "total_chunks": 420,
    "total_queries": 35,
    "index_size": 420,
    "database_size": 2048000,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "index_type": "IndexFlatIP"
  },
  "health": {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2024-01-15T10:40:00",
    "database_connected": true,
    "index_loaded": true
  }
}
```

---

## 🔍 Error Responses

### Common Error Codes

**400 Bad Request**
```json
{
  "detail": "Unsupported file type: .exe. Allowed: .pdf, .docx, .txt"
}
```

**404 Not Found**
```json
{
  "detail": "Document not found"
}
```

**422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**
```json
{
  "detail": "Failed to process query: Connection timeout"
}
```

---

## 📊 Rate Limits

Currently no rate limiting implemented. For production:
- Recommended: 60 requests/minute per IP
- Heavy endpoints (upload, query): 10 requests/minute

---

## 🔐 Security Best Practices

### Production Deployment

1. **Add Authentication**
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
```

2. **Enable HTTPS**
```bash
uvicorn app.main:app --ssl-keyfile key.pem --ssl-certfile cert.pem
```

3. **Set Up CORS Properly**
```python
# In .env
CORS_ORIGINS=["https://yourdomain.com"]
```

4. **Implement Rate Limiting**
```bash
pip install slowapi
```

---

## 📖 Interactive Documentation

Visit these URLs when server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🐍 Python Client Example

```python
import requests

class RAGClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def upload_document(self, file_path):
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{self.base_url}/api/v1/upload", files=files)
            return response.json()
    
    def ask_question(self, query, top_k=5):
        data = {"query": query, "top_k": top_k}
        response = requests.post(f"{self.base_url}/api/v1/query", json=data)
        return response.json()
    
    def list_documents(self):
        response = requests.get(f"{self.base_url}/api/v1/documents")
        return response.json()

# Usage
client = RAGClient()
result = client.upload_document("document.pdf")
answer = client.ask_question("What are the main points?")
print(answer["answer"])
```

---

For more examples, see `examples.py` in the project root.
