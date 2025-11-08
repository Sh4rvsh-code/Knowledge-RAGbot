"""Semantic retrieval using embeddings and FAISS index."""
from typing import List, Dict, Any, Optional
import numpy as np

from app.core.ingestion.embedder import get_embedder
from app.core.ingestion.indexer import get_index_manager
from app.models.database import get_db_manager, Chunk, Document
from app.config import settings
from app.utils.logger import app_logger as logger


class SemanticRetriever:
    """
    Retrieve relevant document chunks using semantic similarity search.
    
    Uses embeddings and FAISS for efficient vector search.
    """
    
    def __init__(
        self,
        top_k: int = None,
        similarity_threshold: float = None
    ):
        """
        Initialize semantic retriever.
        
        Args:
            top_k: Number of results to retrieve
            similarity_threshold: Minimum similarity score
        """
        self.embedder = get_embedder()
        self.index_manager = get_index_manager(
            dimension=self.embedder.get_dimension()
        )
        self.db_manager = get_db_manager()
        
        self.top_k = top_k or settings.top_k_results
        self.similarity_threshold = similarity_threshold or settings.similarity_threshold
        
        logger.info(
            f"Initialized SemanticRetriever with top_k={self.top_k}, "
            f"threshold={self.similarity_threshold}"
        )
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for query.
        
        Args:
            query: Query text
            
        Returns:
            Query embedding vector
        """
        return self.embedder.embed_query(query, normalize=True)
    
    def search(
        self,
        query: str,
        top_k: int = None,
        min_score: float = None,
        doc_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks using semantic similarity.
        
        Args:
            query: Query text
            top_k: Number of results to return (overrides default)
            min_score: Minimum similarity score (overrides default)
            doc_ids: Optional list of document IDs to filter by
            
        Returns:
            List of results with chunk text, metadata, and scores
        """
        top_k = top_k or self.top_k
        min_score = min_score if min_score is not None else self.similarity_threshold
        
        logger.info(f"Searching for query: '{query[:50]}...' (top_k={top_k})")
        
        # Generate query embedding
        query_embedding = self.embed_query(query)
        
        # Search in FAISS index
        faiss_results = self.index_manager.search(query_embedding, top_k=top_k * 2)
        
        # Enrich results with database metadata
        results = []
        db = self.db_manager.get_session()
        
        try:
            for faiss_result in faiss_results:
                score = faiss_result["score"]
                
                # Filter by score threshold
                if score < min_score:
                    continue
                
                # Get chunk from database using faiss_id
                faiss_id = faiss_result["faiss_id"]
                chunk = db.query(Chunk).filter(Chunk.faiss_id == faiss_id).first()
                
                if not chunk:
                    logger.warning(f"Chunk not found for faiss_id: {faiss_id}")
                    continue
                
                # Filter by doc_ids if specified
                if doc_ids and chunk.doc_id not in doc_ids:
                    continue
                
                # Get document info
                document = db.query(Document).filter(Document.id == chunk.doc_id).first()
                
                if not document:
                    logger.warning(f"Document not found for doc_id: {chunk.doc_id}")
                    continue
                
                # Build result
                result = {
                    "chunk_id": chunk.id,
                    "chunk_text": chunk.chunk_text,
                    "chunk_index": chunk.chunk_index,
                    "doc_id": chunk.doc_id,
                    "filename": document.filename,
                    "file_type": document.file_type,
                    "score": score,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "metadata": chunk.chunk_metadata or {}
                }
                
                # Add page number if available (for PDFs)
                if chunk.chunk_metadata and "page_number" in chunk.chunk_metadata:
                    result["page"] = chunk.chunk_metadata["page_number"]
                
                results.append(result)
                
                # Stop if we have enough results
                if len(results) >= top_k:
                    break
            
            logger.info(f"Retrieved {len(results)} results above threshold {min_score}")
            
        finally:
            db.close()
        
        return results
    
    def search_by_embedding(
        self,
        query_embedding: np.ndarray,
        top_k: int = None,
        min_score: float = None
    ) -> List[Dict[str, Any]]:
        """
        Search using pre-computed query embedding.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results
            min_score: Minimum score threshold
            
        Returns:
            List of results
        """
        top_k = top_k or self.top_k
        min_score = min_score if min_score is not None else self.similarity_threshold
        
        # Search in FAISS
        faiss_results = self.index_manager.search(query_embedding, top_k=top_k * 2)
        
        # Enrich with database metadata
        results = []
        db = self.db_manager.get_session()
        
        try:
            for faiss_result in faiss_results:
                score = faiss_result["score"]
                
                if score < min_score:
                    continue
                
                faiss_id = faiss_result["faiss_id"]
                chunk = db.query(Chunk).filter(Chunk.faiss_id == faiss_id).first()
                
                if not chunk:
                    continue
                
                document = db.query(Document).filter(Document.id == chunk.doc_id).first()
                
                if not document:
                    continue
                
                result = {
                    "chunk_id": chunk.id,
                    "chunk_text": chunk.chunk_text,
                    "chunk_index": chunk.chunk_index,
                    "doc_id": chunk.doc_id,
                    "filename": document.filename,
                    "file_type": document.file_type,
                    "score": score,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "metadata": chunk.chunk_metadata or {}
                }
                
                results.append(result)
                
                if len(results) >= top_k:
                    break
        
        finally:
            db.close()
        
        return results
    
    def deduplicate_results(
        self,
        results: List[Dict[str, Any]],
        max_per_document: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate results to avoid too many chunks from same document.
        
        Args:
            results: List of search results
            max_per_document: Maximum chunks per document
            
        Returns:
            Deduplicated results
        """
        doc_counts = {}
        deduplicated = []
        
        for result in results:
            doc_id = result["doc_id"]
            count = doc_counts.get(doc_id, 0)
            
            if count < max_per_document:
                deduplicated.append(result)
                doc_counts[doc_id] = count + 1
        
        logger.info(f"Deduplicated {len(results)} results to {len(deduplicated)}")
        return deduplicated
    
    def get_context_window(
        self,
        results: List[Dict[str, Any]],
        max_tokens: int = 3000
    ) -> str:
        """
        Combine retrieved chunks into a context window for LLM.
        
        Args:
            results: Search results
            max_tokens: Maximum tokens (approximate)
            
        Returns:
            Combined context string
        """
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # Rough approximation: 1 token ≈ 4 chars
        
        for i, result in enumerate(results):
            chunk_text = result["chunk_text"]
            filename = result["filename"]
            
            # Format chunk with source
            chunk_part = f"[Source {i+1}: {filename}]\n{chunk_text}\n"
            chunk_chars = len(chunk_part)
            
            # Check if adding this chunk would exceed limit
            if total_chars + chunk_chars > max_chars and context_parts:
                break
            
            context_parts.append(chunk_part)
            total_chars += chunk_chars
        
        context = "\n".join(context_parts)
        logger.info(f"Built context window with {len(context_parts)} chunks ({total_chars} chars)")
        
        return context


# Global retriever instance
_retriever_instance: Optional[SemanticRetriever] = None


def get_retriever() -> SemanticRetriever:
    """Get or create global retriever instance."""
    global _retriever_instance
    
    if _retriever_instance is None:
        _retriever_instance = SemanticRetriever()
    
    return _retriever_instance
