"""Optional reranking logic for improving retrieval quality."""
from typing import List, Dict, Any
import numpy as np

from app.utils.logger import app_logger as logger


class CrossEncoderRanker:
    """
    Rerank retrieved results using a cross-encoder model.
    
    Cross-encoders can provide more accurate relevance scores
    but are slower than bi-encoders (used for initial retrieval).
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize cross-encoder ranker.
        
        Args:
            model_name: Cross-encoder model name
        """
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)
            self.enabled = True
            logger.info(f"Initialized CrossEncoderRanker with model: {model_name}")
        except ImportError:
            logger.warning("sentence-transformers not available, reranking disabled")
            self.enabled = False
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank results using cross-encoder.
        
        Args:
            query: Query text
            results: List of search results
            top_k: Number of top results to return
            
        Returns:
            Reranked results
        """
        if not self.enabled or not results:
            return results
        
        # Prepare pairs for cross-encoder
        pairs = [(query, result["chunk_text"]) for result in results]
        
        # Get cross-encoder scores
        scores = self.model.predict(pairs)
        
        # Add rerank scores to results
        for result, score in zip(results, scores):
            result["rerank_score"] = float(score)
        
        # Sort by rerank score
        reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
        
        # Return top_k results
        if top_k:
            reranked = reranked[:top_k]
        
        logger.info(f"Reranked {len(results)} results")
        return reranked


class MMRRanker:
    """
    Maximal Marginal Relevance (MMR) for diversity in results.
    
    Balances relevance and diversity to avoid redundant results.
    """
    
    def __init__(self, lambda_param: float = 0.5):
        """
        Initialize MMR ranker.
        
        Args:
            lambda_param: Trade-off between relevance and diversity (0-1)
        """
        self.lambda_param = lambda_param
        logger.info(f"Initialized MMRRanker with lambda={lambda_param}")
    
    def rerank(
        self,
        results: List[Dict[str, Any]],
        top_k: int = None,
        embeddings: List[np.ndarray] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank using MMR for diversity.
        
        Args:
            results: Search results with scores
            top_k: Number of results to return
            embeddings: Optional embeddings for similarity calculation
            
        Returns:
            Reranked results with diversity
        """
        if not results:
            return results
        
        top_k = top_k or len(results)
        
        # If no embeddings provided, use simple diversity based on doc_id
        if embeddings is None:
            return self._simple_diversity(results, top_k)
        
        # MMR algorithm
        selected = []
        remaining = list(range(len(results)))
        
        # Start with highest scoring result
        selected.append(remaining.pop(0))
        
        while remaining and len(selected) < top_k:
            # Calculate MMR score for each remaining result
            mmr_scores = []
            
            for idx in remaining:
                # Relevance score (original score)
                relevance = results[idx]["score"]
                
                # Max similarity to already selected results
                max_sim = 0
                for sel_idx in selected:
                    sim = self._cosine_similarity(
                        embeddings[idx],
                        embeddings[sel_idx]
                    )
                    max_sim = max(max_sim, sim)
                
                # MMR score
                mmr_score = (
                    self.lambda_param * relevance -
                    (1 - self.lambda_param) * max_sim
                )
                mmr_scores.append(mmr_score)
            
            # Select result with highest MMR score
            best_idx = remaining[np.argmax(mmr_scores)]
            selected.append(best_idx)
            remaining.remove(best_idx)
        
        # Return selected results in order
        reranked = [results[idx] for idx in selected]
        logger.info(f"Reranked {len(results)} results using MMR")
        
        return reranked
    
    def _simple_diversity(
        self,
        results: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Simple diversity based on document distribution."""
        doc_counts = {}
        diverse_results = []
        
        # First pass: one from each document
        for result in results:
            doc_id = result["doc_id"]
            if doc_id not in doc_counts:
                diverse_results.append(result)
                doc_counts[doc_id] = 1
                
                if len(diverse_results) >= top_k:
                    return diverse_results
        
        # Second pass: add more results
        for result in results:
            if result not in diverse_results:
                diverse_results.append(result)
                
                if len(diverse_results) >= top_k:
                    break
        
        return diverse_results
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
