# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### Prerequisites
1. GitHub account
2. Streamlit Cloud account (free at https://streamlit.io/cloud)
3. OpenAI or Anthropic API key

### Step-by-Step Deployment

#### 1. Push Code to GitHub

```bash
# Initialize git repository (if not already done)
cd /Users/sharveshraja/Knowledge-RAGbot
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: RAG Bot for Streamlit deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/Knowledge-RAGbot.git
git branch -M main
git push -u origin main
```

#### 2. Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io/
   - Sign in with GitHub

2. **Create New App**
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/Knowledge-RAGbot`
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, click on your app
   - Go to "Settings" → "Secrets"
   - Add your secrets in TOML format:

   ```toml
   # Choose one LLM provider
   
   # Option 1: OpenAI
   OPENAI_API_KEY = "sk-your-actual-openai-key"
   LLM_PROVIDER = "openai"
   
   # Option 2: Anthropic
   # ANTHROPIC_API_KEY = "sk-ant-your-actual-anthropic-key"
   # LLM_PROVIDER = "anthropic"
   
   # Database and model settings
   DATABASE_URL = "sqlite:///./data/rag.db"
   EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
   CHUNK_SIZE = 512
   CHUNK_OVERLAP = 50
   ```

4. **Wait for Deployment**
   - Streamlit Cloud will install dependencies
   - First deployment takes 5-10 minutes
   - Watch the logs for any errors

5. **Access Your App**
   - Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`
   - Share this URL with others!

### 🔧 Advanced Configuration

#### Custom Domain (Optional)
1. Go to app settings
2. Click "Custom domain"
3. Follow instructions to set up CNAME

#### Resource Limits
- **Memory**: 1 GB (free tier)
- **Storage**: 1 GB (free tier)
- **Files**: Uploaded files stored in memory (cleared on restart)

**⚠️ Note**: For production with large documents:
- Consider upgrading to Streamlit Cloud paid plan
- Or use external storage (AWS S3, Google Cloud Storage)

### 🐛 Troubleshooting

#### Issue: App Won't Start
**Solution**: Check logs in Streamlit Cloud dashboard
- Look for import errors
- Verify all dependencies in requirements.txt
- Check secrets are properly configured

#### Issue: Out of Memory
**Solution**: 
- Reduce `CHUNK_SIZE` in secrets
- Limit number of documents
- Upgrade to paid plan

#### Issue: Slow Performance
**Solution**:
- Use smaller embedding model
- Reduce `top_k` parameter
- Enable caching in code

#### Issue: API Key Not Working
**Solution**:
- Verify key is correct in secrets
- Check key has sufficient credits
- Ensure LLM_PROVIDER matches your key

### 📊 Monitoring

#### View Logs
```bash
# In Streamlit Cloud dashboard
Settings → Logs
```

#### View Analytics
```bash
# In Streamlit Cloud dashboard
Analytics → Usage
```

### 🔄 Update Deployment

To update your deployed app:

```bash
# Make changes to your code
git add .
git commit -m "Update: description of changes"
git push

# Streamlit Cloud will auto-redeploy
```

### 🌐 Sharing Your App

Your app URL: `https://YOUR_APP_NAME.streamlit.app`

Share options:
- Direct link
- Embed in website: `<iframe src="https://YOUR_APP_NAME.streamlit.app"></iframe>`
- QR code for mobile access

### 💰 Cost Considerations

**Free Tier Includes:**
- 1 GB RAM
- 1 GB storage
- Unlimited public apps
- Community support

**Paid Tier ($20/month per user):**
- 4 GB RAM
- More storage
- Private apps
- Priority support
- Custom domains

### 🔒 Security Best Practices

1. **Never commit secrets.toml**
   - Already in .gitignore
   - Use Streamlit Cloud secrets manager

2. **API Key Protection**
   - Rotate keys regularly
   - Use separate keys for dev/prod
   - Monitor usage in provider dashboard

3. **Access Control**
   - Free tier: Apps are public
   - Paid tier: Enable authentication

### 📱 Mobile Optimization

The app is mobile-responsive by default:
- Touch-friendly interface
- Responsive layout
- Works on tablets and phones

### 🎯 Next Steps

After deployment:

1. **Test thoroughly**
   - Upload sample documents
   - Ask various questions
   - Check source citations

2. **Monitor usage**
   - Check analytics daily
   - Monitor API costs
   - Watch memory usage

3. **Gather feedback**
   - Share with users
   - Collect improvement ideas
   - Iterate on features

4. **Scale if needed**
   - Upgrade Streamlit plan
   - Optimize performance
   - Add features

### 📞 Support

- **Streamlit Docs**: https://docs.streamlit.io/
- **Community Forum**: https://discuss.streamlit.io/
- **GitHub Issues**: Report bugs in your repo

---

## Local Testing Before Deploy

Always test locally first:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key-here"
export LLM_PROVIDER="openai"

# Run app
streamlit run streamlit_app.py

# Access at http://localhost:8501
```

## Example GitHub Actions for CI/CD (Optional)

Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/
```

---

**Your RAG Bot is ready to go live! 🚀**
