# 🔐 Streamlit Secrets Configuration Guide

## Overview

This guide explains how to configure API keys and settings for the Knowledge-RAGbot using Streamlit secrets. This is the **recommended approach** for deploying on Streamlit Cloud or running locally.

---

## ✅ Required Environment Variables

### **1. LLM Provider Settings**

Choose one of the following LLM providers:

#### **Option A: Google Gemini (Recommended - FREE)**
```toml
LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "your-gemini-api-key-here"
GEMINI_MODEL = "gemini-2.0-flash-exp"
```

**How to get Gemini API Key:**
1. Go to https://makersuite.google.com/app/apikey
2. Click "Get API Key"
3. Copy your API key

#### **Option B: HuggingFace Gemma (FREE)**
```toml
LLM_PROVIDER = "gemma"
HUGGINGFACE_API_KEY = "your-huggingface-api-key-here"
```

**How to get HuggingFace API Key:**
1. Go to https://huggingface.co/settings/tokens
2. Create new token with "read" access
3. Copy your token (starts with `hf_`)

#### **Option C: Local Model (FREE - No API Key)**
```toml
LLM_PROVIDER = "free"
```
Uses `google/flan-t5-small` model locally (no internet required)

---

### **2. Core System Settings**

```toml
# Database
DATABASE_URL = "sqlite:///./data/rag.db"

# Embeddings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# RAG Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.15
```

---

## 📁 Setup Instructions

### **For Local Development**

#### **Method 1: Using .streamlit/secrets.toml (Recommended)**

1. **Create the secrets file:**
   ```bash
   cd /workspaces/Knowledge-RAGbot
   cp .streamlit/secrets.toml.template .streamlit/secrets.toml
   ```

2. **Edit .streamlit/secrets.toml:**
   ```bash
   nano .streamlit/secrets.toml
   ```

3. **Add your API keys:**
   ```toml
   LLM_PROVIDER = "gemini"
   GEMINI_API_KEY = "AIzaSy..."  # Your actual key
   HUGGINGFACE_API_KEY = "hf_..."  # Your actual key
   GEMINI_MODEL = "gemini-2.0-flash-exp"
   
   DATABASE_URL = "sqlite:///./data/rag.db"
   EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
   CHUNK_SIZE = 500
   CHUNK_OVERLAP = 50
   TOP_K_RESULTS = 5
   SIMILARITY_THRESHOLD = 0.15
   ```

4. **Verify .gitignore excludes secrets:**
   ```bash
   # Check that .streamlit/secrets.toml is in .gitignore
   grep "secrets.toml" .gitignore
   ```

   If not present, add it:
   ```bash
   echo ".streamlit/secrets.toml" >> .gitignore
   ```

5. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

#### **Method 2: Using Environment Variables**

If you prefer environment variables over secrets.toml:

```bash
export GEMINI_API_KEY="your-gemini-key"
export HUGGINGFACE_API_KEY="your-hf-key"
export LLM_PROVIDER="gemini"
streamlit run streamlit_app.py
```

**Permanent setup (add to ~/.bashrc or ~/.zshrc):**
```bash
echo 'export GEMINI_API_KEY="your-gemini-key"' >> ~/.bashrc
echo 'export HUGGINGFACE_API_KEY="your-hf-key"' >> ~/.bashrc
echo 'export LLM_PROVIDER="gemini"' >> ~/.bashrc
source ~/.bashrc
```

---

### **For Streamlit Cloud Deployment**

1. **Push your code to GitHub** (without secrets.toml)

2. **Go to Streamlit Cloud:**
   - Visit https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `Sh4rvsh-code/Knowledge-RAGbot`
   - Set main file: `streamlit_app.py`

3. **Add Secrets in Streamlit Cloud:**
   - Click "Advanced settings"
   - Go to "Secrets" tab
   - Paste your configuration:

   ```toml
   LLM_PROVIDER = "gemini"
   GEMINI_API_KEY = "AIzaSy..."
   HUGGINGFACE_API_KEY = "hf_..."
   GEMINI_MODEL = "gemini-2.0-flash-exp"
   
   DATABASE_URL = "sqlite:///./data/rag.db"
   EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
   CHUNK_SIZE = 500
   CHUNK_OVERLAP = 50
   TOP_K_RESULTS = 5
   SIMILARITY_THRESHOLD = 0.15
   ```

4. **Deploy:**
   - Click "Deploy!"
   - Wait for deployment to complete
   - Your app will be live at: `https://your-app.streamlit.app`

---

## 🔍 Verification

### Check if Secrets are Loaded

The app will automatically detect and use secrets. You can verify by:

1. **Start the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Check the sidebar:**
   - Look for "🤖 LLM Settings"
   - You should see your selected provider (Gemini/Gemma/Local)

3. **Test a query:**
   - Upload a document
   - Ask a question
   - Check if it generates an answer (confirms API key works)

### Debugging Secrets Issues

**Problem: "API key not found" error**

**Solution:**
```bash
# Check if secrets file exists
ls -la .streamlit/secrets.toml

# Check if app can read it
streamlit run streamlit_app.py --logger.level=debug
```

**Problem: "Invalid API key" error**

**Solution:**
1. Verify your API key is correct
2. Check for extra spaces or quotes
3. Regenerate the API key if needed

**Problem: App uses environment variables instead of secrets**

**Solution:**
- Ensure `.streamlit/secrets.toml` exists
- Restart Streamlit completely: `pkill -f streamlit && streamlit run streamlit_app.py`

---

## 📋 Complete secrets.toml Template

Here's a complete template with all options:

```toml
# =============================================================================
# LLM PROVIDER CONFIGURATION
# =============================================================================

# Choose ONE of the following:

# Option 1: Google Gemini (FREE - Recommended)
LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "your-gemini-api-key-here"
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Option 2: HuggingFace Gemma (FREE - Alternative)
# LLM_PROVIDER = "gemma"
HUGGINGFACE_API_KEY = "your-huggingface-api-key-here"

# Option 3: Local Model (FREE - No API needed, slower)
# LLM_PROVIDER = "free"

# =============================================================================
# DATABASE & STORAGE
# =============================================================================

DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# =============================================================================
# RAG CONFIGURATION
# =============================================================================

# Text chunking
CHUNK_SIZE = 500        # Characters per chunk (400-600 recommended)
CHUNK_OVERLAP = 50      # Overlap between chunks (50-100 recommended)

# Retrieval settings
TOP_K_RESULTS = 5       # Number of chunks to retrieve (3-7 recommended)
SIMILARITY_THRESHOLD = 0.15  # Minimum similarity score (0.10-0.20 recommended)

# =============================================================================
# OPTIONAL: ADVANCED SETTINGS
# =============================================================================

# Uncomment to customize further:

# OpenAI (Paid - Better quality)
# LLM_PROVIDER = "openai"
# OPENAI_API_KEY = "sk-your-key-here"
# OPENAI_MODEL = "gpt-3.5-turbo"

# Anthropic Claude (Paid)
# LLM_PROVIDER = "anthropic"
# ANTHROPIC_API_KEY = "sk-ant-your-key-here"
# ANTHROPIC_MODEL = "claude-3-sonnet-20240229"
```

---

## 🎯 Recommended Configurations

### **Development (Local Testing)**
```toml
LLM_PROVIDER = "free"  # No API key needed
CHUNK_SIZE = 500
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.15
```

### **Production (Streamlit Cloud - Free)**
```toml
LLM_PROVIDER = "gemini"
GEMINI_API_KEY = "your-actual-key"
GEMINI_MODEL = "gemini-2.0-flash-exp"
HUGGINGFACE_API_KEY = "your-actual-key"  # For Gemma fallback
CHUNK_SIZE = 500
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.15
```

### **High Quality (Paid)**
```toml
LLM_PROVIDER = "openai"
OPENAI_API_KEY = "your-actual-key"
OPENAI_MODEL = "gpt-4"
CHUNK_SIZE = 1000
TOP_K_RESULTS = 7
SIMILARITY_THRESHOLD = 0.10
```

---

## 🔒 Security Best Practices

### ✅ DO:
1. **Use `.streamlit/secrets.toml` for local development**
2. **Use Streamlit Cloud Secrets for deployment**
3. **Add `secrets.toml` to `.gitignore`**
4. **Rotate API keys regularly**
5. **Use read-only HuggingFace tokens**

### ❌ DON'T:
1. **Commit `secrets.toml` to Git**
2. **Share API keys in public forums**
3. **Hardcode keys in source files**
4. **Use production keys for testing**
5. **Give API keys write permissions**

---

## 📊 Priority Order

The app loads settings in this order (first found wins):

1. **Streamlit Secrets** (`.streamlit/secrets.toml`) - **HIGHEST PRIORITY**
2. **Environment Variables** (`export KEY=value`)
3. **`.env` file** (local development)
4. **Default Values** (fallback)

**Recommendation:** Use Streamlit Secrets (#1) for consistency across local and cloud deployments.

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution:**
```bash
pip install streamlit
```

### Issue: "st.secrets is empty"
**Solution:**
```bash
# Ensure file exists
touch .streamlit/secrets.toml

# Add at least one setting
echo 'LLM_PROVIDER = "gemini"' >> .streamlit/secrets.toml

# Restart Streamlit
pkill -f streamlit && streamlit run streamlit_app.py
```

### Issue: "GEMINI_API_KEY not found"
**Solution:**
1. Check spelling in `secrets.toml`: `GEMINI_API_KEY` (case-sensitive)
2. Verify no extra spaces: `GEMINI_API_KEY = "key"` not `GEMINI_API_KEY ="key"`
3. Restart app completely

### Issue: "API quota exceeded"
**Solution:**
- Gemini free tier: 60 requests/minute
- Wait 1 minute and retry
- Consider upgrading to paid tier
- Use caching to reduce API calls (already enabled in app)

---

## 📚 Additional Resources

- **Streamlit Secrets Documentation:** https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- **Google Gemini API:** https://ai.google.dev/
- **HuggingFace Tokens:** https://huggingface.co/settings/tokens
- **Project Repository:** https://github.com/Sh4rvsh-code/Knowledge-RAGbot

---

## ✅ Quick Start Checklist

- [ ] Copy `secrets.toml.template` to `secrets.toml`
- [ ] Get Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Get HuggingFace API key from https://huggingface.co/settings/tokens
- [ ] Add keys to `.streamlit/secrets.toml`
- [ ] Verify `secrets.toml` is in `.gitignore`
- [ ] Run `streamlit run streamlit_app.py`
- [ ] Test with a sample document
- [ ] Deploy to Streamlit Cloud (add secrets there too)

---

**System Status:** ✅ Secrets system fully configured and tested  
**Security:** 🔒 API keys removed from source code  
**Deployment:** 🚀 Ready for Streamlit Cloud
