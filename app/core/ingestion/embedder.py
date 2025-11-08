"""Embedding generation using sentence-transformers."""
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import hashlib
import pickle
from pathlib import Path

from app.config import settings
from app.utils.logger import app_logger as logger


class Embedder:
    """
    Generate embeddings for text chunks using sentence-transformers.
    
    Supports batch processing and caching for efficiency.
    """
    
    def __init__(
        self,
        model_name: str = None,
        batch_size: int = None,
        cache_dir: str = ".cache/embeddings"
    ):
        """
        Initialize embedder.
        
        Args:
            model_name: Name of sentence-transformers model
            batch_size: Batch size for processing
            cache_dir: Directory to cache embeddings
        """
        self.model_name = model_name or settings.embedding_model
        self.batch_size = batch_size or settings.embedding_batch_size
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        
        logger.info(
            f"Embedder initialized with dimension={self.embedding_dimension}, "
            f"batch_size={self.batch_size}"
        )
    
    def embed_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            normalize: Whether to normalize the embedding
            
        Returns:
            Embedding vector as numpy array
        """
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        return embedding
    
    def embed_chunks(
        self,
        chunks: List[str],
        normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for multiple text chunks with batch processing.
        
        Args:
            chunks: List of text chunks
            normalize: Whether to normalize embeddings
            show_progress: Show progress bar
            
        Returns:
            2D numpy array of embeddings (num_chunks x embedding_dim)
        """
        if not chunks:
            logger.warning("Empty chunks list provided")
            return np.array([])
        
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        
        # Generate embeddings in batches
        embeddings = self.model.encode(
            chunks,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            show_progress_bar=show_progress
        )
        
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
    
    def embed_query(self, query: str, normalize: bool = True) -> np.ndarray:
        """
        Generate embedding for a search query.
        
        Args:
            query: Query text
            normalize: Whether to normalize the embedding
            
        Returns:
            Query embedding vector
        """
        return self.embed_text(query, normalize=normalize)
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    def embed_with_cache(
        self,
        text: str,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embedding with caching.
        
        Args:
            text: Input text
            normalize: Whether to normalize
            
        Returns:
            Embedding vector
        """
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        # Check cache
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    embedding = pickle.load(f)
                logger.debug(f"Loaded embedding from cache: {cache_key}")
                return embedding
            except Exception as e:
                logger.warning(f"Failed to load cached embedding: {e}")
        
        # Generate new embedding
        embedding = self.embed_text(text, normalize=normalize)
        
        # Save to cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
            logger.debug(f"Saved embedding to cache: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to save embedding to cache: {e}")
        
        return embedding
    
    def embed_batch_with_cache(
        self,
        texts: List[str],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for batch with caching.
        
        Args:
            texts: List of texts
            normalize: Whether to normalize
            
        Returns:
            2D array of embeddings
        """
        embeddings = []
        texts_to_embed = []
        text_indices = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        embedding = pickle.load(f)
                    embeddings.append((i, embedding))
                except Exception:
                    texts_to_embed.append(text)
                    text_indices.append(i)
            else:
                texts_to_embed.append(text)
                text_indices.append(i)
        
        # Generate embeddings for uncached texts
        if texts_to_embed:
            logger.info(f"Generating {len(texts_to_embed)} new embeddings (cached: {len(embeddings)})")
            new_embeddings = self.embed_chunks(texts_to_embed, normalize=normalize)
            
            # Save to cache and add to results
            for idx, text, embedding in zip(text_indices, texts_to_embed, new_embeddings):
                embeddings.append((idx, embedding))
                
                # Save to cache
                try:
                    cache_key = self._get_cache_key(text)
                    cache_file = self.cache_dir / f"{cache_key}.pkl"
                    with open(cache_file, 'wb') as f:
                        pickle.dump(embedding, f)
                except Exception as e:
                    logger.warning(f"Failed to cache embedding: {e}")
        
        # Sort by original index and extract embeddings
        embeddings.sort(key=lambda x: x[0])
        result = np.array([emb for _, emb in embeddings])
        
        return result
    
    def clear_cache(self):
        """Clear the embedding cache."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Embedding cache cleared")
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dimension
    
    def cosine_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score
        """
        # Normalize if not already
        emb1_norm = embedding1 / (np.linalg.norm(embedding1) + 1e-10)
        emb2_norm = embedding2 / (np.linalg.norm(embedding2) + 1e-10)
        
        # Compute dot product
        similarity = np.dot(emb1_norm, emb2_norm)
        return float(similarity)


# Global embedder instance (singleton pattern)
_embedder_instance: Optional[Embedder] = None


def get_embedder() -> Embedder:
    """Get or create global embedder instance."""
    global _embedder_instance
    
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    
    return _embedder_instance
