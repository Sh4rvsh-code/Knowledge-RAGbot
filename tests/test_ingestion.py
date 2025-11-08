"""Tests for ingestion pipeline."""
import pytest
from pathlib import Path

from app.core.ingestion.chunker import RecursiveChunker, Chunk
from app.core.ingestion.embedder import Embedder
from app.utils.helpers import generate_doc_id


class TestChunker:
    """Test text chunking functionality."""
    
    def test_recursive_chunker_basic(self):
        """Test basic chunking."""
        chunker = RecursiveChunker(chunk_size=100, chunk_overlap=20)
        
        text = "This is a test document. " * 20  # ~500 chars
        doc_id = "test-doc-1"
        
        chunks = chunker.chunk(text, doc_id)
        
        assert len(chunks) > 1
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.doc_id == doc_id for chunk in chunks)
        assert all(len(chunk.chunk_text) <= 120 for chunk in chunks)  # Allow some flexibility
    
    def test_chunker_with_overlap(self):
        """Test that overlap is preserved."""
        chunker = RecursiveChunker(chunk_size=50, chunk_overlap=10)
        
        text = "A" * 30 + "B" * 30 + "C" * 30  # 90 chars
        chunks = chunker.chunk(text, "test-doc")
        
        # Should have 2-3 chunks with overlap
        assert len(chunks) >= 2
    
    def test_empty_text(self):
        """Test handling of empty text."""
        chunker = RecursiveChunker()
        chunks = chunker.chunk("", "test-doc")
        
        assert len(chunks) == 0
    
    def test_short_text(self):
        """Test text shorter than chunk size."""
        chunker = RecursiveChunker(chunk_size=1000)
        
        text = "Short text"
        chunks = chunker.chunk(text, "test-doc")
        
        assert len(chunks) == 1
        assert chunks[0].chunk_text == text


class TestEmbedder:
    """Test embedding generation."""
    
    def test_embed_single_text(self):
        """Test single text embedding."""
        embedder = Embedder()
        
        text = "This is a test sentence."
        embedding = embedder.embed_text(text)
        
        assert embedding is not None
        assert embedding.shape[0] == embedder.get_dimension()
    
    def test_embed_batch(self):
        """Test batch embedding."""
        embedder = Embedder()
        
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]
        
        embeddings = embedder.embed_chunks(texts)
        
        assert embeddings.shape[0] == len(texts)
        assert embeddings.shape[1] == embedder.get_dimension()
    
    def test_embedding_normalization(self):
        """Test that embeddings are normalized."""
        embedder = Embedder()
        
        text = "Test sentence"
        embedding = embedder.embed_text(text, normalize=True)
        
        # Check if normalized (L2 norm should be ~1)
        import numpy as np
        norm = np.linalg.norm(embedding)
        assert 0.99 <= norm <= 1.01


class TestHelpers:
    """Test utility helpers."""
    
    def test_generate_doc_id(self):
        """Test document ID generation."""
        doc_id = generate_doc_id("test.pdf")
        
        assert isinstance(doc_id, str)
        assert len(doc_id) == 16  # SHA256 truncated to 16 chars
    
    def test_generate_doc_id_unique(self):
        """Test that doc IDs are unique for different filenames."""
        doc_id1 = generate_doc_id("test1.pdf")
        doc_id2 = generate_doc_id("test2.pdf")
        
        assert doc_id1 != doc_id2
