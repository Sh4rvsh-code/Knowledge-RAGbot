#!/bin/bash
# Run script for RAG Document Q&A System

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the FastAPI server
echo "Starting RAG Document Q&A System..."
echo "Server will be available at http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
