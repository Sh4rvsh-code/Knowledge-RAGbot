# 📋 Environment Variables Checklist

## Required for Streamlit Deployment

Copy this to your Streamlit Cloud Secrets or `.streamlit/secrets.toml`:

```toml
# ============================================
# REQUIRED: LLM Provider (Choose ONE)
# ============================================

# Option 1: Google Gemini (FREE - Recommended)
LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "your-gemini-api-key-here"
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Option 2: HuggingFace Gemma (FREE)
# LLM_PROVIDER = "gemma"
HUGGINGFACE_API_KEY = "your-huggingface-api-key-here"

# Option 3: Local (FREE - No API key needed)
# LLM_PROVIDER = "free"

# ============================================
# REQUIRED: Database & Embeddings
# ============================================

DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ============================================
# REQUIRED: RAG Settings
# ============================================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.15
```

---

## ✅ Verification Checklist

### Before Deployment

- [ ] **GEMINI_API_KEY** - Get from https://makersuite.google.com/app/apikey
- [ ] **HUGGINGFACE_API_KEY** - Get from https://huggingface.co/settings/tokens
- [ ] **LLM_PROVIDER** - Set to "gemini", "gemma", or "free"
- [ ] **secrets.toml in .gitignore** - Verify with: `grep secrets.toml .gitignore`
- [ ] **No hardcoded keys** - Check with: `git grep -E "AIzaSy|hf_[A-Za-z0-9]{34}"`

### After Deployment

- [ ] App loads without errors
- [ ] Can select LLM provider in sidebar
- [ ] Can upload a document successfully
- [ ] Can ask questions and get answers
- [ ] Reranker toggle works (if enabled)
- [ ] Cache indicators show correctly

---

## 🚀 Quick Setup Commands

### Local Development
```bash
# 1. Copy template
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# 2. Edit with your keys
nano .streamlit/secrets.toml

# 3. Verify gitignore
echo ".streamlit/secrets.toml" >> .gitignore

# 4. Run app
streamlit run streamlit_app.py
```

### Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Deploy from GitHub: `Sh4rvsh-code/Knowledge-RAGbot`
3. Add secrets in Advanced Settings → Secrets
4. Paste the config above with your real API keys
5. Deploy!

---

## 🔍 How to Get API Keys

### Gemini API Key (FREE)
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Get API Key" → "Create API key"
3. Copy the key (starts with `AIzaSy...`)
4. Paste into `GEMINI_API_KEY`

### HuggingFace API Key (FREE)
1. Visit: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "Knowledge-RAGbot"
4. Type: "Read"
5. Copy the token (starts with `hf_...`)
6. Paste into `HUGGINGFACE_API_KEY`

---

## 🎯 Minimal Working Config

If you just want to get started quickly:

```toml
# Bare minimum - uses local LLM (no API key needed)
LLM_PROVIDER = "free"
DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.15
```

This works but is slower. For production, use Gemini.

---

## 🔒 Security Check

Run this to verify no secrets in git:

```bash
# Check for leaked keys
git grep -E "AIzaSy[A-Za-z0-9_-]{33}|hf_[A-Za-z0-9]{34}" || echo "✅ No API keys found in git"

# Check if secrets.toml is ignored
git check-ignore .streamlit/secrets.toml && echo "✅ secrets.toml is gitignored" || echo "⚠️  Add secrets.toml to .gitignore!"
```

---

## 📊 Variable Priority

The system loads in this order:

1. **Streamlit Secrets** (`.streamlit/secrets.toml` or Cloud Secrets)
2. **Environment Variables** (`export VAR=value`)
3. **`.env` file**
4. **Default values**

**Recommendation:** Always use Streamlit Secrets (option 1).

---

## 🛠️ Common Issues

### "GEMINI_API_KEY not set"
→ Add `GEMINI_API_KEY = "your-key"` to secrets.toml

### "HUGGINGFACE_API_KEY not set"
→ Add `HUGGINGFACE_API_KEY = "your-key"` to secrets.toml

### "st.secrets is empty"
→ Check file exists: `ls .streamlit/secrets.toml`
→ Check it has content: `cat .streamlit/secrets.toml`
→ Restart: `pkill -f streamlit && streamlit run streamlit_app.py`

### "API quota exceeded"
→ Wait 60 seconds (free tier: 60 req/min)
→ Enable cache to reduce API calls (already enabled)

---

## ✨ All Set!

Once you have:
- ✅ API keys in secrets.toml (or Streamlit Cloud Secrets)
- ✅ secrets.toml in .gitignore
- ✅ No hardcoded keys in code

You're ready to deploy! 🚀
