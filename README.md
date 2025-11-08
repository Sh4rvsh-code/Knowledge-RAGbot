# RAG Document Q&A System

A production-ready Retrieval-Augmented Generation (RAG) system that allows users to upload documents (PDF, DOCX, TXT), ask questions, and receive accurate answers with source citations and highlighted text spans.

## Features

- 📄 **Multi-format Document Support**: Upload PDF, DOCX, and TXT files
- 🔍 **Semantic Search**: Advanced vector similarity search using FAISS
- 🤖 **Flexible LLM Support**: Use local models or remote APIs (OpenAI/Anthropic)
- 📊 **Source Citations**: Get answers with exact source references and character offsets
- ⚡ **High Performance**: Optimized batch processing and caching
- 🔒 **Production Ready**: Comprehensive error handling, logging, and testing
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Tech Stack

- **Backend**: FastAPI with Uvicorn
- **Vector Search**: FAISS + sentence-transformers (all-MiniLM-L6-v2)
- **Document Processing**: PyMuPDF, python-docx
- **Database**: SQLite with SQLAlchemy ORM
- **LLM**: OpenAI/Anthropic APIs or local transformers models
- **Validation**: Pydantic v2

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Knowledge-RAGbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

### 3. Initialize Data Directories

```bash
mkdir -p data/uploads data/faiss_index
touch data/uploads/.gitkeep data/faiss_index/.gitkeep
```

### 4. Run the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the API

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## API Endpoints

### Document Management

- `POST /api/v1/upload` - Upload a document
- `GET /api/v1/documents` - List all documents
- `GET /api/v1/documents/{doc_id}` - Get document details
- `DELETE /api/v1/documents/{doc_id}` - Delete a document

### Question Answering

- `POST /api/v1/query` - Ask a question
- `GET /api/v1/queries` - Get query history

### Admin Operations

- `POST /api/v1/admin/reindex` - Rebuild FAISS index
- `DELETE /api/v1/admin/clear-all` - Clear all data
- `GET /api/v1/admin/stats` - Get system statistics

### Health & Status

- `GET /health` - Health check
- `GET /api/v1/status` - Detailed system status

## Usage Examples

### Upload a Document

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Ask a Question

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main findings?",
    "top_k": 5
  }'
```

### Response Format

```json
{
  "query": "What are the main findings?",
  "answer": "The main findings indicate...",
  "sources": [
    {
      "document": "document.pdf",
      "page": 3,
      "chunk_text": "...",
      "score": 0.89,
      "start_char": 1250,
      "end_char": 1750
    }
  ],
  "processing_time": 0.45
}
```

## Configuration

Key settings in `.env`:

- **LLM_PROVIDER**: Choose `local` or `remote`
- **OPENAI_API_KEY**: Your OpenAI API key (if using remote)
- **CHUNK_SIZE**: Size of text chunks (default: 1000)
- **CHUNK_OVERLAP**: Overlap between chunks (default: 200)
- **TOP_K_RESULTS**: Number of results to retrieve (default: 5)
- **SIMILARITY_THRESHOLD**: Minimum similarity score (default: 0.7)

## Project Structure

```
rag-document-qa/
├── app/
│   ├── api/              # API routes
│   ├── core/             # Core RAG components
│   │   ├── ingestion/    # Document processing
│   │   ├── retrieval/    # Search and retrieval
│   │   └── llm/          # LLM integration
│   ├── models/           # Database and schemas
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── data/                 # Data storage
├── tests/                # Test suite
└── frontend/             # Optional Streamlit UI
```

## Development

### Run Tests

```bash
pytest tests/ -v --cov=app
```

### Format Code

```bash
black app/ tests/
isort app/ tests/
```

### Type Checking

```bash
mypy app/
```

## Docker Deployment

```bash
docker-compose up -d
```

## Performance Optimization

- Embedding caching to avoid recomputation
- Batch processing for embeddings (configurable batch size)
- FAISS index optimization for fast similarity search
- Connection pooling for database operations
- Async I/O for non-blocking operations

## Monitoring

- Structured logging with Loguru
- Request/response timing
- Error tracking and reporting
- System statistics endpoint

## Security Considerations

- File upload validation and size limits
- API key management via environment variables
- Input sanitization and validation
- Rate limiting (recommended for production)

## Troubleshooting

### Common Issues

1. **FAISS Index Error**: Delete `data/faiss_index/` and reindex
2. **Model Download Issues**: Check internet connection and disk space
3. **Memory Issues**: Reduce batch size or chunk size in `.env`

### Logs

Check logs for detailed error messages:
```bash
tail -f logs/app.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.
