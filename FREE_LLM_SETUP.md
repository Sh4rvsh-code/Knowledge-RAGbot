# 🆓 FREE LLM Setup Guide - No Payment Required!

## 🎉 Great News!

Your RAG bot can now work **completely FREE** without any paid API keys! Choose from these options:

---

## ✅ Option 1: FREE - Hugging Face API (Recommended)

**Pros:**
- ✅ Completely FREE
- ✅ Good quality responses
- ✅ Easy setup
- ✅ Works on Streamlit Cloud

**Setup:**

1. **Get a FREE Hugging Face Token** (Optional but recommended):
   - Go to: https://huggingface.co/
   - Sign up for free
   - Go to: https://huggingface.co/settings/tokens
   - Create a "Read" token
   - Copy the token (starts with `hf_`)

2. **Configure Streamlit Secrets**:
   ```toml
   LLM_PROVIDER = "huggingface"
   HUGGINGFACE_API_KEY = "hf_your_token_here"
   HUGGINGFACE_MODEL = "google/flan-t5-xxl"
   ```

3. **Without Token** (Rate limited but works):
   ```toml
   LLM_PROVIDER = "huggingface"
   HUGGINGFACE_MODEL = "google/flan-t5-xxl"
   ```

**Models you can use (all free):**
- `google/flan-t5-xxl` - Best for Q&A (Recommended)
- `google/flan-t5-large` - Faster, slightly lower quality
- `mistralai/Mistral-7B-Instruct-v0.1` - Very good but slower
- `HuggingFaceH4/zephyr-7b-beta` - Conversational

---

## ✅ Option 2: FREE - Auto-Select Best Available

**Pros:**
- ✅ Automatically uses best free option
- ✅ No configuration needed
- ✅ Falls back if one fails

**Setup:**

Just set this in Streamlit Secrets:
```toml
LLM_PROVIDER = "free"
```

That's it! The system will:
1. Try Hugging Face API (with or without token)
2. Fall back to local model if HF is unavailable

---

## ✅ Option 3: FREE - Local Model

**Pros:**
- ✅ 100% free
- ✅ No API calls
- ✅ Complete privacy

**Cons:**
- ⚠️ Slower on Streamlit Cloud (limited CPU)
- ⚠️ Lower quality responses
- ⚠️ May timeout on large requests

**Setup:**
```toml
LLM_PROVIDER = "local"
LOCAL_MODEL_NAME = "google/flan-t5-small"
```

**Note:** Works better when running locally than on Streamlit Cloud.

---

## 💰 Paid Options (Better Quality)

### OpenAI GPT-3.5 Turbo
**Cost:** ~$0.002 per question (very affordable)

```toml
LLM_PROVIDER = "openai"
OPENAI_API_KEY = "sk-your-key-here"
OPENAI_MODEL = "gpt-3.5-turbo"
```

Get key: https://platform.openai.com/api-keys

### Anthropic Claude
**Cost:** Similar to OpenAI

```toml
LLM_PROVIDER = "anthropic"
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

Get key: https://console.anthropic.com/

---

## 🚀 Quick Start - FREE Setup

### For Streamlit Cloud:

1. **Go to your app settings**:
   - Visit: https://share.streamlit.io/
   - Click your app → Settings → Secrets

2. **Paste this configuration**:
   ```toml
   LLM_PROVIDER = "free"
   DATABASE_URL = "sqlite:///./data/rag.db"
   EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
   CHUNK_SIZE = 512
   CHUNK_OVERLAP = 50
   TOP_K_RESULTS = 5
   SIMILARITY_THRESHOLD = 0.7
   ```

3. **Save and wait**:
   - Click "Save"
   - App will restart (~30 seconds)
   - Visit your app URL

4. **Test it**:
   - Upload a PDF
   - Ask a question
   - Get FREE AI answers!

---

## 📊 Comparison Table

| Option | Cost | Quality | Speed | Setup |
|--------|------|---------|-------|-------|
| **Hugging Face (with token)** | FREE | ⭐⭐⭐⭐ | Fast | Easy |
| **Hugging Face (no token)** | FREE | ⭐⭐⭐⭐ | Fast* | Easiest |
| **Local Model** | FREE | ⭐⭐⭐ | Slow | Easy |
| OpenAI GPT-3.5 | ~$0.002/q | ⭐⭐⭐⭐⭐ | Very Fast | Easy |
| OpenAI GPT-4 | ~$0.03/q | ⭐⭐⭐⭐⭐⭐ | Fast | Easy |

*Rate limited without token but still usable

---

## 🎯 Recommended Configuration

**Best FREE setup for Streamlit Cloud:**

```toml
# Use Hugging Face with optional token
LLM_PROVIDER = "huggingface"

# Optional: Add token for better rate limits (still FREE!)
# HUGGINGFACE_API_KEY = "hf_your_token_here"

# Good model for Q&A
HUGGINGFACE_MODEL = "google/flan-t5-xxl"

# Database
DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# RAG Settings
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7
```

---

## 🆓 Get Your FREE Hugging Face Token

1. Visit: **https://huggingface.co/**
2. Click "Sign Up" (it's FREE!)
3. Verify your email
4. Go to: **https://huggingface.co/settings/tokens**
5. Click "New token"
6. Name it: "RAG Bot"
7. Type: Select "Read"
8. Click "Generate"
9. Copy the token (starts with `hf_`)

**No credit card required!** 🎉

---

## 💡 Tips

### For Best FREE Performance:
- Use `google/flan-t5-xxl` with Hugging Face
- Get a free HF token (removes rate limits)
- Keep questions concise
- Upload smaller documents (<50 pages)

### If Model is "Loading":
- First time using a model takes ~20 seconds to load
- Just wait and try again
- The model will stay loaded afterward

### Rate Limits Without Token:
- Hugging Face free tier: ~100 requests/hour
- More than enough for personal use!
- Get token for unlimited requests

---

## 🎊 You're All Set!

With the FREE configuration, your RAG bot is ready to use **without spending a penny**! 

Test it at: https://knowledge-ragbot-6kwqvc6giy2crhkortxswc.streamlit.app

Enjoy your FREE AI-powered document Q&A system! 🚀
