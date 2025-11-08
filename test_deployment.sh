#!/bin/bash
# Pre-deployment test script for Streamlit
# Run this before deploying to catch issues early

set -e

echo "🧪 Running Pre-Deployment Tests for Streamlit..."
echo "================================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version | cut -d' ' -f2)
echo "Python version: $python_version"
if [[ "$python_version" < "3.10" ]]; then
    echo -e "${RED}❌ Python 3.10+ required${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python version OK${NC}"

# Check if required files exist
echo -e "\n${YELLOW}Checking required files...${NC}"
required_files=(
    "streamlit_app.py"
    "requirements.txt"
    "packages.txt"
    ".streamlit/config.toml"
    ".streamlit/secrets.toml.example"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        exit 1
    fi
done

# Check if .gitignore includes secrets
echo -e "\n${YELLOW}Checking .gitignore...${NC}"
if grep -q "secrets.toml" .gitignore; then
    echo -e "${GREEN}✅ secrets.toml in .gitignore${NC}"
else
    echo -e "${RED}❌ secrets.toml not in .gitignore${NC}"
    exit 1
fi

# Check for sensitive data in git
echo -e "\n${YELLOW}Checking for sensitive data...${NC}"
if git ls-files | grep -q "secrets.toml$"; then
    echo -e "${RED}❌ WARNING: secrets.toml is tracked by git!${NC}"
    echo "Run: git rm --cached .streamlit/secrets.toml"
    exit 1
else
    echo -e "${GREEN}✅ No secrets in git${NC}"
fi

# Install dependencies in virtual environment
echo -e "\n${YELLOW}Testing dependency installation...${NC}"
if [ ! -d "venv_test" ]; then
    python3 -m venv venv_test
fi

source venv_test/bin/activate

echo "Installing requirements..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Dependency installation failed${NC}"
    deactivate
    exit 1
fi

# Test imports
echo -e "\n${YELLOW}Testing Python imports...${NC}"
python3 << EOF
import sys
sys.path.insert(0, '.')

try:
    import streamlit
    import sentence_transformers
    import faiss
    import fitz  # PyMuPDF
    import docx
    import sqlalchemy
    import openai
    import anthropic
    print("✅ All critical imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    deactivate
    exit 1
fi

# Test app syntax
echo -e "\n${YELLOW}Testing streamlit_app.py syntax...${NC}"
python3 -m py_compile streamlit_app.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ streamlit_app.py syntax OK${NC}"
else
    echo -e "${RED}❌ streamlit_app.py has syntax errors${NC}"
    deactivate
    exit 1
fi

# Test app initialization (dry run)
echo -e "\n${YELLOW}Testing app initialization...${NC}"
timeout 10s streamlit run streamlit_app.py --server.headless true &
APP_PID=$!
sleep 5

if ps -p $APP_PID > /dev/null; then
    echo -e "${GREEN}✅ App starts successfully${NC}"
    kill $APP_PID 2>/dev/null
else
    echo -e "${RED}❌ App failed to start${NC}"
    deactivate
    exit 1
fi

# Clean up
deactivate
rm -rf venv_test

# Check file sizes
echo -e "\n${YELLOW}Checking file sizes...${NC}"
total_size=$(du -sh . | cut -f1)
echo "Total repository size: $total_size"

large_files=$(find . -type f -size +50M 2>/dev/null)
if [ -n "$large_files" ]; then
    echo -e "${RED}⚠️  Warning: Large files detected (>50MB):${NC}"
    echo "$large_files"
    echo "Consider using Git LFS or external storage"
fi

# Check requirements.txt
echo -e "\n${YELLOW}Analyzing requirements.txt...${NC}"
if grep -q "torch" requirements.txt; then
    echo -e "${YELLOW}⚠️  PyTorch detected - this increases deployment time${NC}"
    echo "Consider using torch-cpu or removing if not needed"
fi

# Estimate deployment time
echo -e "\n${YELLOW}Estimated deployment metrics:${NC}"
req_count=$(wc -l < requirements.txt | tr -d ' ')
echo "📦 Dependencies: $req_count packages"
echo "⏱️  First deployment: ~5-10 minutes"
echo "⏱️  Subsequent deploys: ~2-3 minutes"

# Final checklist
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Pre-Deployment Tests Passed!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}Before deploying to Streamlit Cloud:${NC}"
echo "1. ✅ Commit all changes: git add . && git commit -m 'Ready for deployment'"
echo "2. ✅ Push to GitHub: git push origin main"
echo "3. ✅ Go to https://share.streamlit.io/"
echo "4. ✅ Create new app from your GitHub repo"
echo "5. ✅ Set main file to: streamlit_app.py"
echo "6. ✅ Add secrets (API keys) in Streamlit Cloud dashboard"
echo "7. ✅ Deploy and monitor logs"

echo -e "\n${YELLOW}Remember to add these secrets in Streamlit Cloud:${NC}"
echo "- OPENAI_API_KEY or ANTHROPIC_API_KEY"
echo "- LLM_PROVIDER (openai/anthropic/local)"
echo "- DATABASE_URL"
echo "- EMBEDDING_MODEL"

echo -e "\n${GREEN}Good luck with your deployment! 🚀${NC}"
