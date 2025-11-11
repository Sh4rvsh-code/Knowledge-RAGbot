"""
Cross-encoder reranker for improving retrieval precision.
Uses sentence-transformers CrossEncoder to rerank retrieved candidates.
"""

from typing import List, Dict, Any
import numpy as np

from app.utils.logger import app_logger as logger


class CrossEncoderReranker:
    """
    Rerank retrieved candidates using a cross-encoder model.
    
    Cross-encoders are more accurate than bi-encoders but slower,
    so we use them to rerank top-K candidates from initial retrieval.
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize cross-encoder reranker.
        
        Args:
            model_name: HuggingFace model name for cross-encoder
                       Default: ms-marco-MiniLM-L-6-v2 (fast, good quality)
                       Alternatives:
                       - cross-encoder/ms-marco-MiniLM-L-12-v2 (better, slower)
                       - cross-encoder/ms-marco-TinyBERT-L-2-v2 (faster, lower quality)
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load cross-encoder model."""
        try:
            from sentence_transformers import CrossEncoder
            
            logger.info(f"Loading cross-encoder: {self.model_name}")
            self.model = CrossEncoder(self.model_name)
            logger.info(f"Cross-encoder loaded successfully")
            
        except ImportError:
            logger.error("sentence-transformers not installed. Install: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load cross-encoder: {e}")
            raise
    
    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank candidates using cross-encoder.
        
        Args:
            query: User query
            candidates: List of candidate dicts with 'chunk_text' key
            top_k: Number of top candidates to return
            
        Returns:
            Top-k candidates sorted by cross-encoder score (descending)
        """
        if not candidates:
            return []
        
        if not self.model:
            logger.warning("Cross-encoder not loaded, returning original candidates")
            return candidates[:top_k]
        
        # Prepare query-candidate pairs
        pairs = [[query, c["chunk_text"]] for c in candidates]
        
        # Compute cross-encoder scores (higher = more relevant)
        logger.info(f"Reranking {len(candidates)} candidates with cross-encoder")
        scores = self.model.predict(pairs)
        
        # Add scores to candidates
        for candidate, score in zip(candidates, scores):
            candidate["rerank_score"] = float(score)
            # Keep original bi-encoder score as well
            if "score" in candidate:
                candidate["bi_encoder_score"] = candidate["score"]
            candidate["score"] = float(score)  # Replace with rerank score
        
        # Sort by rerank score (descending)
        candidates_sorted = sorted(
            candidates,
            key=lambda x: x["rerank_score"],
            reverse=True
        )
        
        # Log score changes
        if candidates_sorted:
            logger.info(
                f"Reranking complete. Top score: {candidates_sorted[0]['rerank_score']:.4f}, "
                f"Bottom score: {candidates_sorted[-1]['rerank_score']:.4f}"
            )
        
        return candidates_sorted[:top_k]
    
    def rerank_with_threshold(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Rerank and filter by minimum score threshold.
        
        Args:
            query: User query
            candidates: Candidate chunks
            top_k: Maximum number to return
            min_score: Minimum rerank score (typically -10 to +10 range)
            
        Returns:
            Filtered and sorted candidates
        """
        reranked = self.rerank(query, candidates, top_k=len(candidates))
        
        # Filter by threshold
        filtered = [c for c in reranked if c["rerank_score"] >= min_score]
        
        logger.info(
            f"Filtered {len(reranked)} candidates to {len(filtered)} "
            f"(threshold: {min_score})"
        )
        
        return filtered[:top_k]


# Global reranker instance
_reranker_instance = None


def get_reranker(model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> CrossEncoderReranker:
    """Get or create global reranker instance."""
    global _reranker_instance
    
    if _reranker_instance is None:
        _reranker_instance = CrossEncoderReranker(model_name=model_name)
    
    return _reranker_instance

