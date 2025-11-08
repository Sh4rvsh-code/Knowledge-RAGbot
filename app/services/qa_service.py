"""Question-answering service."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from sqlalchemy.orm import Session

from app.models.database import Query as QueryModel
from app.models.schemas import QueryRequest, QueryResponse, SourceInfo, QueryHistoryList, QueryHistory
from app.core.retrieval.retriever import get_retriever
from app.core.llm.orchestrator import LLMOrchestrator
from app.core.llm.remote_llm import get_llm
from app.config import settings
from app.utils.logger import app_logger as logger


class QAService:
    """
    Question-answering service orchestrating retrieval and generation.
    """
    
    def __init__(self):
        """Initialize QA service."""
        self.retriever = get_retriever()
        
        # Initialize LLM
        llm_provider = get_llm()
        self.orchestrator = LLMOrchestrator(llm_provider)
        
        logger.info("QAService initialized")
    
    async def answer_question(
        self,
        request: QueryRequest,
        db: Session
    ) -> QueryResponse:
        """
        Answer a question using RAG pipeline.
        
        Args:
            request: Query request
            db: Database session
            
        Returns:
            QueryResponse with answer and sources
        """
        start_time = time.time()
        
        logger.info(f"Processing query: '{request.query[:50]}...'")
        
        try:
            # 1. Retrieve relevant chunks
            retrieved_chunks = self.retriever.search(
                query=request.query,
                top_k=request.top_k,
                min_score=request.min_score
            )
            
            logger.info(f"Retrieved {len(retrieved_chunks)} chunks")
            
            if not retrieved_chunks:
                answer = "I couldn't find any relevant information in the documents to answer your question."
                sources = []
            else:
                # 2. Generate answer using LLM
                answer = self.orchestrator.answer_question(
                    query=request.query,
                    context_chunks=retrieved_chunks
                )
                
                # 3. Prepare sources
                sources = []
                if request.include_sources:
                    sources = self._prepare_sources(retrieved_chunks)
            
            processing_time = time.time() - start_time
            
            # 4. Save query to database
            query_record = QueryModel(
                query_text=request.query,
                response=answer,
                timestamp=datetime.utcnow(),
                processing_time=processing_time,
                retrieved_chunks=[
                    {"chunk_id": chunk["chunk_id"], "score": chunk["score"]}
                    for chunk in retrieved_chunks
                ],
                top_k=request.top_k,
                llm_provider=settings.llm_provider
            )
            
            db.add(query_record)
            db.commit()
            
            logger.info(f"Query processed in {processing_time:.2f}s")
            
            # 5. Return response
            return QueryResponse(
                query=request.query,
                answer=answer,
                sources=sources,
                processing_time=processing_time,
                retrieved_count=len(retrieved_chunks),
                llm_provider=settings.llm_provider
            )
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            
            # Save error to database
            query_record = QueryModel(
                query_text=request.query,
                timestamp=datetime.utcnow(),
                top_k=request.top_k,
                error_message=str(e)
            )
            db.add(query_record)
            db.commit()
            
            raise
    
    def _prepare_sources(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[SourceInfo]:
        """
        Prepare source citations from retrieved chunks.
        
        Args:
            chunks: Retrieved chunk data
            
        Returns:
            List of SourceInfo objects
        """
        sources = []
        
        for chunk in chunks:
            source = SourceInfo(
                document=chunk["filename"],
                chunk_index=chunk["chunk_index"],
                chunk_text=chunk["chunk_text"],
                score=chunk["score"],
                start_char=chunk["start_char"],
                end_char=chunk["end_char"],
                page=chunk.get("page"),
                metadata=chunk.get("metadata", {})
            )
            sources.append(source)
        
        return sources
    
    def get_query_history(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50
    ) -> QueryHistoryList:
        """
        Get query history.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            QueryHistoryList
        """
        total = db.query(QueryModel).count()
        
        queries = (
            db.query(QueryModel)
            .order_by(QueryModel.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return QueryHistoryList(
            queries=[QueryHistory.model_validate(q) for q in queries],
            total=total
        )
    
    def get_query_by_id(
        self,
        query_id: int,
        db: Session
    ) -> Optional[QueryModel]:
        """Get query by ID."""
        return db.query(QueryModel).filter(QueryModel.id == query_id).first()
    
    def search_similar_queries(
        self,
        query: str,
        db: Session,
        limit: int = 5
    ) -> List[QueryModel]:
        """
        Find similar past queries (simple text search for now).
        
        Args:
            query: Query text
            db: Database session
            limit: Maximum results
            
        Returns:
            List of similar queries
        """
        # Simple LIKE search (can be improved with embedding-based search)
        keywords = query.lower().split()[:3]  # Use first 3 words
        
        if not keywords:
            return []
        
        # Build query with OR conditions
        filters = []
        for keyword in keywords:
            filters.append(QueryModel.query_text.ilike(f"%{keyword}%"))
        
        from sqlalchemy import or_
        
        similar_queries = (
            db.query(QueryModel)
            .filter(or_(*filters))
            .order_by(QueryModel.timestamp.desc())
            .limit(limit)
            .all()
        )
        
        return similar_queries


# Global service instance
_qa_service: Optional[QAService] = None


def get_qa_service() -> QAService:
    """Get or create QA service instance."""
    global _qa_service
    
    if _qa_service is None:
        _qa_service = QAService()
    
    return _qa_service
