# 🤖 Knowledge RAG Bot - Streamlit Edition

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready **Retrieval-Augmented Generation (RAG)** system that allows users to upload documents and ask questions with AI-powered answers and source citations.

**🚀 Live Demo:** [https://your-app-url.streamlit.app](https://your-app-url.streamlit.app)

![RAG Bot Demo](https://via.placeholder.com/800x400?text=RAG+Bot+Screenshot)

## ✨ Features

- 📤 **Multi-Format Upload**: PDF, DOCX, TXT, Markdown
- 🔍 **Semantic Search**: FAISS vector similarity search
- 🤖 **AI Answers**: Powered by OpenAI GPT or Anthropic Claude
- 📑 **Source Citations**: Traceable answers with document references
- 💾 **Persistent Storage**: SQLite database for documents and queries
- 🎨 **Beautiful UI**: Clean, responsive Streamlit interface
- ⚡ **Fast**: Efficient embedding and retrieval pipeline
- 🔒 **Secure**: API keys stored in Streamlit secrets

## 🎯 Quick Start

### Option 1: Use the Live App

Just visit: **[https://your-app-url.streamlit.app](https://your-app-url.streamlit.app)**

### Option 2: Run Locally

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Knowledge-RAGbot.git
cd Knowledge-RAGbot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key-here"
export LLM_PROVIDER="openai"

# Run app
streamlit run streamlit_app.py
```

Visit http://localhost:8501 in your browser.

## 📦 What's Inside

```
Knowledge-RAGbot/
├── streamlit_app.py          # Main Streamlit application
├── app/                       # Core RAG components
│   ├── config.py             # Configuration management
│   ├── core/                 # RAG pipeline
│   │   ├── ingestion/        # Document processing
│   │   ├── retrieval/        # Semantic search
│   │   └── llm/              # LLM integration
│   ├── models/               # Database models
│   └── utils/                # Helper functions
├── .streamlit/               # Streamlit configuration
│   ├── config.toml           # UI theme and settings
│   └── secrets.toml.example  # Secrets template
├── requirements.txt          # Python dependencies
├── packages.txt              # System dependencies
└── tests/                    # Unit tests
```

## 🚀 Deploy to Streamlit Cloud

### Step 1: Prepare Your Code

```bash
# Run pre-deployment tests
./test_deployment.sh

# Commit and push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click "New app"
3. Select your repo: `YOUR_USERNAME/Knowledge-RAGbot`
4. Set main file: `streamlit_app.py`
5. Click "Deploy"

### Step 3: Configure Secrets

In Streamlit Cloud dashboard → Settings → Secrets:

```toml
OPENAI_API_KEY = "sk-your-key-here"
LLM_PROVIDER = "openai"
DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

**📖 Detailed Guide:** See [STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)

**✅ Checklist:** See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

## 💡 How to Use

### 1. Upload Documents

- Go to "📤 Upload Documents" tab
- Click "Choose a file"
- Select PDF, DOCX, or TXT file
- Click "Upload"
- Wait for processing (shows chunks created)

### 2. Ask Questions

- Go to "💬 Ask Questions" tab
- Type your question
- Adjust settings in sidebar (optional):
  - Number of sources (1-10)
  - Minimum similarity (0-1)
- Click "🔍 Ask"
- View answer and source citations

### 3. View History

- Go to "📜 History" tab
- See all previous questions and answers
- Click to expand for details

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required if using OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required if using Anthropic |
| `LLM_PROVIDER` | LLM provider (`openai`, `anthropic`, `local`) | `openai` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | Text chunk size in characters | `512` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |
| `TOP_K_DEFAULT` | Default number of sources | `5` |

### Customization

Edit `.streamlit/config.toml` for UI customization:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## 📊 Tech Stack

| Component | Technology |
|-----------|-----------|
| **UI Framework** | Streamlit 1.29.0 |
| **Vector Search** | FAISS (faiss-cpu) |
| **Embeddings** | sentence-transformers |
| **LLM** | OpenAI GPT / Anthropic Claude |
| **Document Processing** | PyMuPDF, python-docx |
| **Database** | SQLite + SQLAlchemy |
| **Web Server** | Streamlit Cloud / Uvicorn |

## 🔧 Advanced Usage

### Using Different LLM Providers

**OpenAI:**
```toml
OPENAI_API_KEY = "sk-..."
LLM_PROVIDER = "openai"
```

**Anthropic:**
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
LLM_PROVIDER = "anthropic"
```

**Local Model:**
```toml
LLM_PROVIDER = "local"
LOCAL_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"
```

### Custom Embedding Models

```toml
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

See [sentence-transformers models](https://www.sbert.net/docs/pretrained_models.html)

## 📈 Performance

- **Upload Speed**: ~2-5 seconds per document
- **Query Speed**: ~2-5 seconds per question
- **Embedding Model**: 384-dimensional vectors
- **Memory Usage**: ~500MB base + ~1MB per document
- **Concurrent Users**: 10+ (Streamlit Cloud free tier)

## 🐛 Troubleshooting

### App Won't Start
- Check Streamlit Cloud logs
- Verify secrets are configured
- Ensure all dependencies in requirements.txt

### Out of Memory
- Reduce `CHUNK_SIZE` to 256
- Upgrade to Streamlit Cloud paid plan (4GB RAM)
- Delete old documents

### Slow Performance
- Reduce `TOP_K_DEFAULT` to 3
- Use smaller embedding model
- Check API rate limits

**More solutions:** See [Troubleshooting Guide](STREAMLIT_DEPLOY.md#troubleshooting)

## 📚 Documentation

- [Deployment Guide](STREAMLIT_DEPLOY.md) - Detailed deployment instructions
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) - Step-by-step checklist
- [API Reference](API_REFERENCE.md) - API documentation
- [Architecture](ARCHITECTURE.md) - System architecture
- [Setup Guide](SETUP_GUIDE.md) - Development setup

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest tests/`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Amazing framework
- [FAISS](https://github.com/facebookresearch/faiss) - Fast vector search
- [sentence-transformers](https://www.sbert.net/) - Embeddings
- [OpenAI](https://openai.com/) / [Anthropic](https://anthropic.com/) - LLMs

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/Knowledge-RAGbot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/Knowledge-RAGbot/discussions)
- 📧 **Email**: your.email@example.com

## 🌟 Star History

If you find this project helpful, please give it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_USERNAME/Knowledge-RAGbot&type=Date)](https://star-history.com/#YOUR_USERNAME/Knowledge-RAGbot&Date)

---

**Made with ❤️ by [Your Name](https://github.com/YOUR_USERNAME)**

**Deploy your own:** [![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
