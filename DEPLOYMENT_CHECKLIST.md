# 🚀 Streamlit Deployment Checklist

## Pre-Deployment (Local)

### ✅ Code Preparation
- [ ] All code tested locally
- [ ] `streamlit run streamlit_app.py` works without errors
- [ ] Run `./test_deployment.sh` successfully
- [ ] No hardcoded API keys in code
- [ ] `.gitignore` includes `.streamlit/secrets.toml`

### ✅ Files Ready
- [ ] `streamlit_app.py` - Main application file
- [ ] `requirements.txt` - All dependencies listed
- [ ] `packages.txt` - System packages (for PyMuPDF, etc.)
- [ ] `.streamlit/config.toml` - Streamlit configuration
- [ ] `.streamlit/secrets.toml.example` - Example secrets file
- [ ] `STREAMLIT_DEPLOY.md` - Deployment guide
- [ ] `README.md` - Project documentation

### ✅ API Keys Ready
- [ ] OpenAI API key (if using OpenAI)
- [ ] Anthropic API key (if using Anthropic)
- [ ] Keys have sufficient credits
- [ ] Keys tested locally

## GitHub Setup

### ✅ Repository
- [ ] Git repository initialized
- [ ] All changes committed
- [ ] Repository pushed to GitHub
- [ ] Repository is public (or you have Streamlit paid plan)
- [ ] No secrets in git history

```bash
# Commands to run:
git init
git add .
git commit -m "Initial commit: RAG Bot"
git remote add origin https://github.com/YOUR_USERNAME/Knowledge-RAGbot.git
git branch -M main
git push -u origin main
```

## Streamlit Cloud Setup

### ✅ Account & App Creation
- [ ] Created Streamlit Cloud account at https://share.streamlit.io/
- [ ] Connected GitHub account
- [ ] Created new app
- [ ] Selected correct repository
- [ ] Set main file path to: `streamlit_app.py`
- [ ] Clicked "Deploy"

### ✅ Secrets Configuration
- [ ] Opened app settings in Streamlit Cloud
- [ ] Navigated to "Secrets" section
- [ ] Added secrets in TOML format:

```toml
# Copy and paste into Streamlit Cloud secrets editor:

# Option 1: OpenAI
OPENAI_API_KEY = "sk-your-actual-key-here"
LLM_PROVIDER = "openai"

# Option 2: Anthropic (comment out if using OpenAI)
# ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
# LLM_PROVIDER = "anthropic"

# Configuration
DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K_DEFAULT = 5
```

- [ ] Saved secrets
- [ ] Restarted app (if needed)

## Post-Deployment Testing

### ✅ Basic Functionality
- [ ] App loads without errors
- [ ] Can access app URL: `https://YOUR_APP.streamlit.app`
- [ ] No import errors in logs
- [ ] System stats show in sidebar
- [ ] All three tabs visible (Questions, Upload, History)

### ✅ Upload Testing
- [ ] Can upload PDF file
- [ ] Can upload DOCX file
- [ ] Can upload TXT file
- [ ] Document appears in "Uploaded Documents"
- [ ] Chunk count is reasonable
- [ ] No errors in processing

### ✅ Query Testing
- [ ] Can ask questions
- [ ] Receives AI-generated answers
- [ ] Source citations appear
- [ ] Sources show correct document names
- [ ] Processing time is reasonable (<30s)
- [ ] Query appears in History tab

### ✅ Performance
- [ ] App loads in <10 seconds
- [ ] Queries complete in <30 seconds
- [ ] No memory errors
- [ ] No timeout errors

## Monitoring & Maintenance

### ✅ Daily Checks (First Week)
- [ ] Check app is still running
- [ ] Review logs for errors
- [ ] Monitor API usage/costs
- [ ] Check memory usage

### ✅ Weekly Checks
- [ ] Review analytics
- [ ] Check for failed queries
- [ ] Update documentation if needed
- [ ] Respond to user feedback

## Troubleshooting

### ❌ App Won't Start
**Check:**
- Logs in Streamlit Cloud dashboard
- All secrets are configured
- requirements.txt has correct versions
- packages.txt includes system dependencies

**Solution:**
```bash
# Check logs
# Fix dependencies
# Restart app in dashboard
```

### ❌ Out of Memory
**Check:**
- Number of documents uploaded
- Size of documents
- Memory usage in dashboard

**Solution:**
- Reduce `CHUNK_SIZE` to 256
- Delete old documents
- Upgrade to paid plan (4GB RAM)

### ❌ Slow Performance
**Check:**
- Processing time for queries
- Number of chunks being retrieved
- Model size

**Solution:**
- Reduce `TOP_K_DEFAULT` to 3
- Use smaller embedding model
- Enable more caching

### ❌ API Errors
**Check:**
- API key is correct in secrets
- Key has available credits
- LLM_PROVIDER matches key type

**Solution:**
- Verify key in provider dashboard
- Add credits if needed
- Check for rate limits

## Optimization Tips

### 🚀 Performance
- [ ] Use `@st.cache_resource` for model loading
- [ ] Use `@st.cache_data` for data processing
- [ ] Reduce chunk size if memory is tight
- [ ] Use smaller embedding model if needed

### 💰 Cost Reduction
- [ ] Monitor API usage daily
- [ ] Set usage limits in provider dashboard
- [ ] Use cheaper models (gpt-3.5-turbo vs gpt-4)
- [ ] Cache common queries

### 🎨 User Experience
- [ ] Add helpful error messages
- [ ] Include usage instructions
- [ ] Add example questions
- [ ] Show loading indicators

## Success Criteria

### ✅ Deployment Complete When:
- [ ] App is live and accessible via public URL
- [ ] Users can upload documents successfully
- [ ] Users can ask questions and get answers
- [ ] Source citations work correctly
- [ ] No critical errors in logs
- [ ] Response time is acceptable
- [ ] API costs are within budget

## Next Steps After Deployment

### 📈 Enhancements
- [ ] Add user authentication (paid plan)
- [ ] Implement rate limiting
- [ ] Add analytics tracking
- [ ] Create feedback mechanism
- [ ] Add more LLM providers
- [ ] Improve UI/UX based on feedback

### 📢 Promotion
- [ ] Share URL with team
- [ ] Add to portfolio
- [ ] Write blog post
- [ ] Share on social media
- [ ] Gather user feedback

### 📊 Monitoring
- [ ] Set up monitoring alerts
- [ ] Track usage patterns
- [ ] Monitor costs weekly
- [ ] Review error logs
- [ ] Collect user feedback

---

## Quick Reference

**App URL Format:** `https://YOUR-APP-NAME.streamlit.app`

**Streamlit Cloud Dashboard:** https://share.streamlit.io/

**Update Deployment:**
```bash
git add .
git commit -m "Update: description"
git push
# Auto-deploys in 2-3 minutes
```

**View Logs:**
Streamlit Cloud → Your App → Manage App → Logs

**Update Secrets:**
Streamlit Cloud → Your App → Settings → Secrets

---

## 🎉 Congratulations!

Your RAG Bot is now live on Streamlit Cloud!

**Share your app:** `https://YOUR-APP-NAME.streamlit.app`

**Need help?** Check `STREAMLIT_DEPLOY.md` for detailed instructions.
