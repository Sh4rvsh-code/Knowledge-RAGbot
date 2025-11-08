"""Tests for retrieval functionality."""
import pytest
import numpy as np

from app.core.retrieval.ranker import MMRRanker


class TestMMRRanker:
    """Test MMR ranking for diversity."""
    
    def test_mmr_simple_diversity(self):
        """Test simple diversity ranking."""
        ranker = MMRRanker(lambda_param=0.5)
        
        results = [
            {"doc_id": "doc1", "score": 0.9, "chunk_text": "Test 1"},
            {"doc_id": "doc1", "score": 0.85, "chunk_text": "Test 2"},
            {"doc_id": "doc2", "score": 0.8, "chunk_text": "Test 3"},
            {"doc_id": "doc2", "score": 0.75, "chunk_text": "Test 4"},
        ]
        
        reranked = ranker._simple_diversity(results, top_k=3)
        
        # Should prefer diversity (one from each doc first)
        assert len(reranked) == 3
        doc_ids = [r["doc_id"] for r in reranked[:2]]
        assert "doc1" in doc_ids
        assert "doc2" in doc_ids


class TestRetrieval:
    """Test retrieval components."""
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        ranker = MMRRanker()
        
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        vec3 = np.array([0.0, 1.0, 0.0])
        
        # Same vectors
        sim1 = ranker._cosine_similarity(vec1, vec2)
        assert 0.99 <= sim1 <= 1.01
        
        # Orthogonal vectors
        sim2 = ranker._cosine_similarity(vec1, vec3)
        assert -0.01 <= sim2 <= 0.01
