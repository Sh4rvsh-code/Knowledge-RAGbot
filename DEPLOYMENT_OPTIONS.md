# 🚀 Complete Deployment Guide

## Three Ways to Deploy Your RAG Bot

### 🌟 Option 1: Streamlit Cloud (Recommended - FREE)

**Best for:** Quick deployment, demos, small teams

**Pros:**
- ✅ Free tier available
- ✅ Zero infrastructure management
- ✅ Auto-deploys from GitHub
- ✅ Built-in secrets management
- ✅ Public URL instantly

**Deployment Steps:**

```bash
# Run automated deployment
./deploy_streamlit.sh
```

Or manually:
1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect repo and deploy
4. Configure secrets

**📖 Detailed Guide:** [STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)

---

### 🐳 Option 2: Docker (Self-Hosted)

**Best for:** Production, custom infrastructure, full control

**Deployment Steps:**

```bash
# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:8501
```

**Features:**
- ✅ FastAPI backend + Streamlit frontend
- ✅ Complete isolation
- ✅ Easy scaling
- ✅ Production-ready

**📖 Detailed Guide:** See `docker-compose.yml` and `Dockerfile`

---

### ☁️ Option 3: Cloud Platforms

#### AWS (EC2 + S3)

```bash
# 1. Launch EC2 instance (t2.medium)
# 2. Install Docker
# 3. Clone repo and run

sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# Clone and deploy
git clone https://github.com/YOUR_USERNAME/Knowledge-RAGbot.git
cd Knowledge-RAGbot
docker-compose up -d
```

#### Google Cloud Platform (Cloud Run)

```bash
# 1. Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/rag-bot

# 2. Deploy to Cloud Run
gcloud run deploy rag-bot \
  --image gcr.io/PROJECT_ID/rag-bot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure (Container Instances)

```bash
# 1. Build and push to ACR
az acr build --registry myregistry --image rag-bot:v1 .

# 2. Deploy to ACI
az container create \
  --resource-group myResourceGroup \
  --name rag-bot \
  --image myregistry.azurecr.io/rag-bot:v1 \
  --cpu 2 \
  --memory 4 \
  --ports 8501
```

---

## 📊 Comparison Matrix

| Feature | Streamlit Cloud | Docker | AWS/GCP/Azure |
|---------|----------------|--------|---------------|
| **Cost** | Free/$20/mo | Server costs | $20-100+/mo |
| **Setup Time** | 10 minutes | 30 minutes | 1-2 hours |
| **Difficulty** | ⭐ Easy | ⭐⭐ Medium | ⭐⭐⭐ Hard |
| **Scaling** | Limited | Manual | Auto-scale |
| **Custom Domain** | $20/mo | Yes | Yes |
| **Storage** | 1 GB | Unlimited | Unlimited |
| **Memory** | 1-4 GB | Configurable | Configurable |
| **Best For** | Demos, MVP | Dev/Staging | Production |

---

## 🎯 Recommended Path

### For Most Users (Getting Started)

1. **Start with Streamlit Cloud** (FREE)
   - Deploy in 10 minutes
   - Test with real users
   - Validate your use case

2. **Monitor Usage**
   - Track user count
   - Monitor API costs
   - Check performance

3. **Upgrade When Needed**
   - More than 100 users/day → Cloud platform
   - Need custom domain → Paid plan
   - Large files → Self-hosted

### For Production (Enterprise)

1. **Use Docker + Cloud Platform**
   - Better performance
   - More control
   - Scalability
   - Custom infrastructure

---

## 🚀 Quick Start Commands

### Streamlit Cloud
```bash
./deploy_streamlit.sh
# Follow prompts, then configure secrets in dashboard
```

### Docker Local
```bash
docker-compose up -d
# Access at http://localhost:8501
```

### Docker Production
```bash
# Build
docker build -t rag-bot .

# Run with environment variables
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY="your-key" \
  -e LLM_PROVIDER="openai" \
  -v $(pwd)/data:/app/data \
  rag-bot
```

---

## ⚙️ Configuration for Each Platform

### Streamlit Cloud Secrets
```toml
# In Streamlit Cloud dashboard → Secrets
OPENAI_API_KEY = "sk-..."
LLM_PROVIDER = "openai"
DATABASE_URL = "sqlite:///./data/rag.db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

### Docker Environment
```bash
# .env file
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
DATABASE_URL=sqlite:///./data/rag.db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Cloud Platform Environment
```bash
# Set in cloud console or CLI
export OPENAI_API_KEY="sk-..."
export LLM_PROVIDER="openai"
export DATABASE_URL="sqlite:///./data/rag.db"
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

---

## 🔒 Security Checklist

- [ ] API keys in secrets/environment (never in code)
- [ ] HTTPS enabled (automatic on cloud platforms)
- [ ] Rate limiting configured
- [ ] CORS properly set
- [ ] Regular security updates
- [ ] Monitor API usage
- [ ] Backup database regularly

---

## 📈 Scaling Strategy

### Phase 1: MVP (0-100 users)
- **Platform:** Streamlit Cloud Free
- **Cost:** $0 + API costs
- **Setup:** 10 minutes

### Phase 2: Growth (100-1,000 users)
- **Platform:** Streamlit Cloud Pro or Docker + VPS
- **Cost:** $20-50/month + API costs
- **Setup:** 1 hour

### Phase 3: Scale (1,000+ users)
- **Platform:** AWS/GCP/Azure with auto-scaling
- **Cost:** $100-500/month + API costs
- **Setup:** 4-8 hours
- **Features:**
  - Load balancing
  - Database replication
  - CDN for static files
  - Redis caching
  - Monitoring & alerts

---

## 🎓 Learning Path

### Beginner → Deploy to Streamlit Cloud
1. Read [STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)
2. Run `./deploy_streamlit.sh`
3. Configure secrets
4. Test your app

### Intermediate → Docker Deployment
1. Read Docker documentation
2. Test locally: `docker-compose up`
3. Deploy to VPS or cloud
4. Configure CI/CD

### Advanced → Production Scaling
1. Choose cloud provider
2. Set up infrastructure as code (Terraform)
3. Implement monitoring (Datadog, New Relic)
4. Configure auto-scaling
5. Set up staging/production environments

---

## 📞 Support & Resources

### Documentation
- [STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md) - Streamlit deployment
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Step-by-step checklist
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

### Community
- [Streamlit Forums](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/YOUR_USERNAME/Knowledge-RAGbot/issues)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/streamlit)

### Tools
- `./deploy_streamlit.sh` - Automated Streamlit deployment
- `./test_deployment.sh` - Pre-deployment tests
- `./verify_setup.py` - System verification
- `docker-compose.yml` - Docker orchestration

---

## 🎉 Success Metrics

Track these after deployment:

- ✅ App is accessible via public URL
- ✅ Documents upload successfully
- ✅ Questions return accurate answers
- ✅ Response time < 30 seconds
- ✅ No critical errors in logs
- ✅ API costs within budget
- ✅ Users can complete full workflow

---

## 🚀 Deploy Now!

Choose your path and get started:

**Quick & Easy (10 min):**
```bash
./deploy_streamlit.sh
```

**Full Control (30 min):**
```bash
docker-compose up -d
```

**Production (2 hours):**
Follow cloud platform guide above

---

**Need help?** Open an issue or check the documentation!

**Ready to scale?** Contact us for enterprise support.

**Want to contribute?** PRs welcome!

---

Made with ❤️ by the RAG Bot team
