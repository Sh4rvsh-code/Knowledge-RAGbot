"""Question-answering endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.schemas import QueryRequest, QueryResponse, QueryHistoryList
from app.services.qa_service import QAService
from app.api.dependencies import get_db, get_qa_svc
from app.utils.logger import app_logger as logger

router = APIRouter(prefix="/api/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    db: Session = Depends(get_db),
    qa_service: QAService = Depends(get_qa_svc)
):
    """
    Ask a question and get an answer based on uploaded documents.
    
    The system will:
    1. Find relevant document chunks using semantic search
    2. Generate an answer using LLM with retrieved context
    3. Return the answer with source citations
    
    Example:
    ```json
    {
        "query": "What are the main findings?",
        "top_k": 5,
        "min_score": 0.7,
        "include_sources": true
    }
    ```
    """
    logger.info(f"Query request: '{request.query[:50]}...'")
    
    try:
        response = await qa_service.answer_question(request, db)
        return response
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


@router.get("/queries", response_model=QueryHistoryList)
async def get_query_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    qa_service: QAService = Depends(get_qa_svc)
):
    """
    Get query history.
    
    Returns a list of past queries with their responses.
    """
    return qa_service.get_query_history(db=db, skip=skip, limit=limit)


@router.get("/queries/{query_id}")
async def get_query_by_id(
    query_id: int,
    db: Session = Depends(get_db),
    qa_service: QAService = Depends(get_qa_svc)
):
    """
    Get a specific query by ID.
    """
    query = qa_service.get_query_by_id(query_id, db)
    
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    
    return {
        "id": query.id,
        "query_text": query.query_text,
        "response": query.response,
        "timestamp": query.timestamp,
        "processing_time": query.processing_time,
        "retrieved_chunks": query.retrieved_chunks,
        "top_k": query.top_k,
        "llm_provider": query.llm_provider
    }
