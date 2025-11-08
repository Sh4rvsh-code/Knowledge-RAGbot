#!/bin/bash
# Quick start script for RAG Document Q&A System

set -e

echo "================================================"
echo "RAG Document Q&A System - Quick Start"
echo "================================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY (for OpenAI GPT models)"
    echo "   - ANTHROPIC_API_KEY (for Claude models)"
    echo ""
    read -p "Press Enter to continue after editing .env file..."
fi

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/uploads data/faiss_index logs

# Run database migrations (create tables)
echo "Initializing database..."
python3 -c "from app.models.database import get_db_manager; get_db_manager().create_tables()"

echo ""
echo "================================================"
echo "✅ Setup complete!"
echo "================================================"
echo ""
echo "To start the server:"
echo "  python3 -m uvicorn app.main:app --reload"
echo ""
echo "Or use:"
echo "  python3 app/main.py"
echo ""
echo "The API will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "================================================"
