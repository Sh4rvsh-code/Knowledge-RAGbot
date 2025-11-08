#!/bin/bash
# Quick deployment script for Streamlit Cloud

set -e

echo "🚀 RAG Bot - Quick Deployment to Streamlit Cloud"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: Initialize Git
echo -e "\n${YELLOW}Step 1: Initializing Git Repository${NC}"
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✅ Git initialized${NC}"
else
    echo -e "${GREEN}✅ Git already initialized${NC}"
fi

# Step 2: Create .gitignore if needed
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
env/
.venv

# Environment variables
.env
.streamlit/secrets.toml

# Data files
data/uploads/*
data/faiss_index/*
data/*.db

# IDE
.vscode/
.idea/
.DS_Store

# Testing
.pytest_cache/
*.log

# Models cache
models/
.cache/
EOF
    echo -e "${GREEN}✅ .gitignore created${NC}"
fi

# Step 3: Get GitHub username
echo -e "\n${YELLOW}Step 2: GitHub Configuration${NC}"
read -p "Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "Error: GitHub username required"
    exit 1
fi

# Step 4: Get repository name
read -p "Enter repository name [Knowledge-RAGbot]: " REPO_NAME
REPO_NAME=${REPO_NAME:-Knowledge-RAGbot}

# Step 5: Add and commit files
echo -e "\n${YELLOW}Step 3: Committing Files${NC}"
git add .
git commit -m "Initial commit: RAG Bot for Streamlit deployment" || echo "No changes to commit"
echo -e "${GREEN}✅ Files committed${NC}"

# Step 6: Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Remote already configured${NC}"
else
    echo -e "\n${YELLOW}Step 4: Configuring Remote${NC}"
    git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
    echo -e "${GREEN}✅ Remote configured${NC}"
fi

# Step 7: Create main branch
git branch -M main

# Step 8: Instructions for creating GitHub repo
echo -e "\n${BLUE}================================================${NC}"
echo -e "${BLUE}IMPORTANT: Create GitHub Repository${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Repository name: ${REPO_NAME}"
echo "3. Description: AI-powered RAG document Q&A system"
echo "4. Make it PUBLIC (or get Streamlit paid plan)"
echo "5. DO NOT initialize with README"
echo "6. Click 'Create repository'"
echo ""
read -p "Press ENTER after creating the repository..."

# Step 9: Push to GitHub
echo -e "\n${YELLOW}Step 5: Pushing to GitHub${NC}"
echo "Pushing to: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
git push -u origin main || {
    echo -e "${YELLOW}If push failed, you may need to authenticate${NC}"
    echo "Try: git push -u origin main"
    exit 1
}
echo -e "${GREEN}✅ Code pushed to GitHub${NC}"

# Step 10: Streamlit Cloud Instructions
echo -e "\n${BLUE}================================================${NC}"
echo -e "${BLUE}Deploy to Streamlit Cloud${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "1. Go to: https://share.streamlit.io/"
echo "2. Sign in with GitHub"
echo "3. Click 'New app'"
echo "4. Repository: ${GITHUB_USERNAME}/${REPO_NAME}"
echo "5. Branch: main"
echo "6. Main file path: streamlit_app.py"
echo "7. Click 'Deploy'"
echo ""
echo "8. After deployment starts, configure secrets:"
echo "   - Go to app settings"
echo "   - Click 'Secrets'"
echo "   - Add (choose one):"
echo ""
echo "   For OpenAI:"
echo "   OPENAI_API_KEY = \"sk-your-key-here\""
echo "   LLM_PROVIDER = \"openai\""
echo ""
echo "   For Anthropic:"
echo "   ANTHROPIC_API_KEY = \"sk-ant-your-key-here\""
echo "   LLM_PROVIDER = \"anthropic\""
echo ""
echo "   Also add:"
echo "   DATABASE_URL = \"sqlite:///./data/rag.db\""
echo "   EMBEDDING_MODEL = \"sentence-transformers/all-MiniLM-L6-v2\""
echo ""
echo "9. Save secrets and wait for deployment (5-10 minutes)"
echo ""
echo -e "${GREEN}Your app will be live at:${NC}"
echo -e "${GREEN}https://${REPO_NAME,,}.streamlit.app${NC}"
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✅ Deployment script complete!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Need help? Check:"
echo "- STREAMLIT_DEPLOY.md - Detailed deployment guide"
echo "- DEPLOYMENT_CHECKLIST.md - Step-by-step checklist"
echo ""
echo "Good luck! 🚀"
