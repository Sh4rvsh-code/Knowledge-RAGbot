# RAG Document Q&A System - Setup Guide

## 📋 Prerequisites

- Python 3.10 or higher
- 4GB RAM minimum (8GB recommended)
- OpenAI API key (or Anthropic API key for Claude)
- Git (optional)

## 🚀 Quick Start (Recommended)

### 1. Run the Setup Script

```bash
chmod +x quickstart.sh
./quickstart.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up the `.env` file
- Create necessary directories
- Initialize the database

### 2. Configure API Keys

Edit the `.env` file and add your API key:

```bash
# For OpenAI (GPT models)
OPENAI_API_KEY="sk-your-api-key-here"

# OR for Anthropic (Claude models)
ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

### 3. Start the Server

```bash
./run.sh
```

Or manually:

```bash
source venv/bin/activate
python3 -m uvicorn app.main:app --reload
```

### 4. Access the API

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📦 Manual Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

### 4. Create Data Directories

```bash
mkdir -p data/uploads data/faiss_index logs
```

### 5. Initialize Database

```bash
python3 -c "from app.models.database import get_db_manager; get_db_manager().create_tables()"
```

### 6. Run the Server

```bash
python3 app/main.py
```

## 🔧 Configuration Options

Edit `.env` to customize:

### LLM Provider

```bash
LLM_PROVIDER="remote"  # Options: "local", "remote"
OPENAI_API_KEY="your-key"
OPENAI_MODEL="gpt-3.5-turbo"  # or "gpt-4"
```

### Embedding Model

```bash
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

### Chunking Parameters

```bash
CHUNK_SIZE=1000        # Characters per chunk
CHUNK_OVERLAP=200      # Overlap between chunks
```

### Retrieval Settings

```bash
TOP_K_RESULTS=5              # Default number of results
SIMILARITY_THRESHOLD=0.7     # Minimum similarity score
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Set environment variables
export OPENAI_API_KEY="your-key-here"

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Build and Run Manually

```bash
# Build image
docker build -t rag-document-qa .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY="your-key" \
  --name rag-api \
  rag-document-qa

# View logs
docker logs -f rag-api
```

## 📚 Usage Examples

### Upload a Document

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
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

### Python Example

```python
import requests

# Upload document
with open("document.pdf", "rb") as f:
    files = {"file": ("document.pdf", f)}
    response = requests.post("http://localhost:8000/api/v1/upload", files=files)
    print(response.json())

# Ask question
query = {
    "query": "What are the main findings?",
    "top_k": 5,
    "include_sources": True
}
response = requests.post("http://localhost:8000/api/v1/query", json=query)
print(response.json()["answer"])
```

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test file
pytest tests/test_api.py -v
```

## 🔍 Troubleshooting

### Issue: "Module not found"

**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "FAISS index error"

**Solution**: Delete the index and let it rebuild:
```bash
rm -rf data/faiss_index/*
# Restart the server
```

### Issue: "Database locked"

**Solution**: Close any other connections to the database:
```bash
rm data/database.db
python3 -c "from app.models.database import get_db_manager; get_db_manager().create_tables()"
```

### Issue: "Model download failed"

**Solution**: Check internet connection and disk space. Models are cached in `~/.cache/huggingface/`

### Issue: "Out of memory"

**Solution**: Reduce batch size in `.env`:
```bash
EMBEDDING_BATCH_SIZE=16  # Default is 32
CHUNK_SIZE=500           # Default is 1000
```

## 📊 Performance Tuning

### For Better Speed

1. Use GPU for embeddings (requires `faiss-gpu` instead of `faiss-cpu`)
2. Increase batch size: `EMBEDDING_BATCH_SIZE=64`
3. Use smaller embedding model
4. Reduce `TOP_K_RESULTS`

### For Better Accuracy

1. Use larger embedding model
2. Decrease `CHUNK_SIZE` for more granular chunks
3. Increase `TOP_K_RESULTS`
4. Lower `SIMILARITY_THRESHOLD`
5. Use GPT-4 instead of GPT-3.5

## 🔐 Security Notes

### Production Deployment

1. **Never commit `.env` file** to version control
2. **Use environment variables** for sensitive data
3. **Add authentication** to API endpoints
4. **Enable HTTPS** in production
5. **Set up rate limiting**
6. **Regular security updates**

### Example: Adding API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Use in routes:
@router.post("/query")
async def query(request: QueryRequest, api_key: str = Depends(verify_api_key)):
    ...
```

## 📈 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### System Stats

```bash
curl http://localhost:8000/api/v1/admin/stats
```

### Logs

```bash
tail -f logs/app.log      # Application logs
tail -f logs/error.log    # Error logs
```

## 🔄 Maintenance

### Reindex All Documents

```bash
curl -X POST "http://localhost:8000/api/v1/admin/reindex" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Clear All Data

```bash
curl -X DELETE "http://localhost:8000/api/v1/admin/clear-all?confirm=true"
```

### Backup Data

```bash
# Backup database
cp data/database.db data/database.db.backup

# Backup FAISS index
cp -r data/faiss_index data/faiss_index.backup

# Backup uploaded files
tar -czf uploads_backup.tar.gz data/uploads/
```

## 🆘 Getting Help

1. Check logs: `tail -f logs/app.log`
2. Review examples: `examples.py`
3. Check API docs: http://localhost:8000/docs
4. Refer to `README.md` for detailed documentation

## 📝 Next Steps

1. ✅ Install and configure the system
2. ✅ Upload your first document
3. ✅ Ask a question
4. 🔧 Customize settings for your use case
5. 🚀 Deploy to production
6. 📊 Monitor and optimize performance

---

**Need help?** Check the troubleshooting section or review the examples in `examples.py`.
