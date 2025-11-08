# 🎯 START HERE - Complete Guide

Welcome to the Knowledge RAG Bot! This guide will get you up and running quickly.

## 🚀 Fastest Way to Deploy (10 minutes)

### Step 1: Get Your API Key

Choose one:
- **OpenAI**: Get key at https://platform.openai.com/api-keys
- **Anthropic**: Get key at https://console.anthropic.com/

### Step 2: Deploy to Streamlit Cloud

```bash
# Run the automated deployment script
./deploy_streamlit.sh
```

This script will:
1. ✅ Initialize Git repository
2. ✅ Commit your files
3. ✅ Guide you to create GitHub repo
4. ✅ Push code to GitHub
5. ✅ Give you instructions for Streamlit Cloud

### Step 3: Configure on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `streamlit_app.py`
6. Click "Deploy"

### Step 4: Add Your API Key

In Streamlit Cloud dashboard → Settings → Secrets:

**For OpenAI:**
```toml
OPENAI_API_KEY = "sk-your-actual-key-here"
LLM_PROVIDER = "openai"
DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

**For Anthropic:**
```toml
ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
LLM_PROVIDER = "anthropic"
DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

### Step 5: Wait for Deployment

- First deployment: ~5-10 minutes
- You'll get a URL like: `https://your-app.streamlit.app`
- Share this URL with anyone!

---

## 🧪 Test Locally First (Optional but Recommended)

### Quick Local Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API key
export OPENAI_API_KEY="your-key-here"
export LLM_PROVIDER="openai"

# 3. Run the app
streamlit run streamlit_app.py

# 4. Open browser to http://localhost:8501
```

---

## 📚 Documentation Quick Links

### For Beginners
- 👉 **[STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)** - Detailed deployment guide
- 👉 **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Step-by-step checklist

### For Developers
- 👉 **[README.md](README.md)** - Project overview
- 👉 **[API_REFERENCE.md](API_REFERENCE.md)** - API documentation
- 👉 **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture

### For Advanced Users
- 👉 **[DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)** - All deployment methods
- 👉 **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Development setup

---

## 🎯 What This App Does

### 📤 Upload Documents
- Upload PDF, DOCX, or TXT files
- Automatically chunks and indexes content
- Creates searchable knowledge base

### 💬 Ask Questions
- Type natural language questions
- Get AI-powered answers
- See source citations from your documents

### 📊 Track History
- View all previous questions
- Review past answers
- Monitor usage

---

## 🛠️ Quick Troubleshooting

### App Won't Start
**Problem:** Deployment failed or errors in logs

**Solutions:**
1. Check secrets are configured correctly
2. Verify API key has credits
3. Look at logs in Streamlit Cloud dashboard

### No Documents Uploading
**Problem:** Upload fails or hangs

**Solutions:**
1. Check file size (<50MB)
2. Verify file format (PDF, DOCX, TXT)
3. Check logs for specific errors

### Slow Responses
**Problem:** Questions take too long

**Solutions:**
1. Reduce "Number of sources" in sidebar
2. Use smaller documents
3. Check API rate limits

### Out of Memory
**Problem:** App crashes with memory errors

**Solutions:**
1. Delete old documents
2. Upload smaller files
3. Upgrade to Streamlit Cloud Pro ($20/mo for 4GB RAM)

---

## 💰 Cost Breakdown

### Streamlit Cloud (Hosting)
- **Free Tier**: $0/month
  - 1 GB RAM
  - 1 GB storage
  - Public apps
  - Perfect for testing!

- **Pro Tier**: $20/month
  - 4 GB RAM
  - Private apps
  - Custom domains
  - Better for production

### LLM API Costs (Estimate)

**OpenAI GPT-3.5-Turbo:**
- ~$0.002 per question
- 1,000 questions = ~$2
- Very affordable!

**OpenAI GPT-4:**
- ~$0.03 per question
- 1,000 questions = ~$30
- Better quality, higher cost

**Anthropic Claude:**
- Similar to GPT-3.5
- ~$0.002-0.01 per question

**Tip:** Start with GPT-3.5-Turbo for testing!

---

## ✅ Quick Verification Checklist

After deployment, verify:

- [ ] App loads at your Streamlit URL
- [ ] Can upload a test PDF
- [ ] Document appears in "Uploaded Documents"
- [ ] Can ask a question about the document
- [ ] Receives answer with source citations
- [ ] Query appears in History tab
- [ ] No errors in Streamlit Cloud logs

---

## 📞 Get Help

### Something Not Working?

1. **Check Logs**
   - Streamlit Cloud → Your App → Manage → Logs
   - Look for error messages

2. **Read Docs**
   - [STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md) - Deployment help
   - [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Troubleshooting

3. **Run Tests**
   ```bash
   ./test_deployment.sh  # Pre-deployment tests
   python verify_setup.py  # System verification
   ```

4. **Ask for Help**
   - Open GitHub issue
   - Check Streamlit forums
   - Stack Overflow

---

## 🎓 Next Steps After Deployment

### Week 1: Testing
- [ ] Upload various document types
- [ ] Test different question types
- [ ] Share with friends for feedback
- [ ] Monitor API costs

### Week 2: Optimization
- [ ] Adjust chunk size if needed
- [ ] Tune similarity threshold
- [ ] Optimize for your use case
- [ ] Add more documents

### Week 3: Scaling
- [ ] Evaluate user feedback
- [ ] Consider upgrading plan if needed
- [ ] Implement improvements
- [ ] Share with wider audience

---

## 🌟 Pro Tips

### 1. Better Answers
- Upload well-formatted documents
- Use clear, specific questions
- Adjust "Number of sources" (3-7 works best)
- Set "Minimum similarity" to 0.6-0.8

### 2. Cost Control
- Start with GPT-3.5-Turbo
- Monitor usage in OpenAI dashboard
- Set billing alerts
- Use smaller chunk sizes (256-512)

### 3. Performance
- Keep documents under 10MB
- Upload text-heavy PDFs (not scanned images)
- Limit to 50-100 documents total (free tier)
- Delete old documents you don't need

### 4. Best Practices
- Test locally before deploying
- Use descriptive document names
- Keep documents well-organized
- Regular backups of important data

---

## 📊 Success Stories

### Use Cases

**Research Assistant**
- Upload research papers
- Ask about methodologies
- Compare findings across papers

**Customer Support**
- Upload product manuals
- Answer customer questions
- Provide source citations

**Legal Document Review**
- Upload contracts
- Search for specific clauses
- Compare terms across documents

**Study Aid**
- Upload textbooks/notes
- Ask study questions
- Get explanations with references

---

## 🎉 You're Ready!

Choose your path:

### 🚀 Deploy Now (Recommended)
```bash
./deploy_streamlit.sh
```

### 🧪 Test Locally First
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
streamlit run streamlit_app.py
```

### 📖 Read More First
- [STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md) - Full guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Checklist

---

## 📝 Quick Reference Card

**Your App URL:** `https://your-app.streamlit.app`

**Streamlit Dashboard:** https://share.streamlit.io/

**Update App:** Just `git push` to GitHub (auto-deploys!)

**Add Secrets:** Dashboard → Settings → Secrets

**View Logs:** Dashboard → Manage App → Logs

**Get Help:** Open issue or check docs

---

**Happy deploying! 🚀**

Questions? Check the docs or open an issue!

Made with ❤️ for the community
