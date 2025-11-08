"""FAISS index management for vector similarity search."""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
import pickle
from pathlib import Path

from app.config import settings
from app.utils.logger import app_logger as logger


class FaissIndexManager:
    """
    Manage FAISS index for efficient vector similarity search.
    
    Supports adding, searching, saving, loading, and deleting vectors.
    """
    
    def __init__(
        self,
        dimension: int = None,
        index_type: str = None,
        index_path: str = None
    ):
        """
        Initialize FAISS index manager.
        
        Args:
            dimension: Embedding dimension
            index_type: Type of FAISS index (IndexFlatIP or IndexFlatL2)
            index_path: Path to save/load index
        """
        self.dimension = dimension
        self.index_type = index_type or settings.faiss_index_type
        self.index_path = Path(index_path or settings.faiss_index_path)
        self.metadata_path = Path(settings.faiss_metadata_path)
        
        self.index: Optional[faiss.Index] = None
        self.metadata: Dict[int, Dict[str, Any]] = {}
        self.current_id = 0
        
        logger.info(f"Initialized FaissIndexManager with type={self.index_type}")
    
    def create_index(self, dimension: int = None):
        """
        Create a new FAISS index.
        
        Args:
            dimension: Embedding dimension
        """
        if dimension:
            self.dimension = dimension
        
        if not self.dimension:
            raise ValueError("Dimension must be specified")
        
        logger.info(f"Creating FAISS index with dimension={self.dimension}")
        
        if self.index_type == "IndexFlatIP":
            # Inner product (cosine similarity for normalized vectors)
            self.index = faiss.IndexFlatIP(self.dimension)
        elif self.index_type == "IndexFlatL2":
            # L2 distance
            self.index = faiss.IndexFlatL2(self.dimension)
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
        
        self.metadata = {}
        self.current_id = 0
        
        logger.info(f"Created {self.index_type} index")
    
    def add_vectors(
        self,
        embeddings: np.ndarray,
        metadata_list: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add vectors to the index with metadata.
        
        Args:
            embeddings: 2D array of embeddings (num_vectors x dimension)
            metadata_list: List of metadata dicts for each vector
            
        Returns:
            List of assigned vector IDs
        """
        if self.index is None:
            raise ValueError("Index not created. Call create_index() first.")
        
        if len(embeddings) != len(metadata_list):
            raise ValueError("Number of embeddings must match metadata list length")
        
        # Ensure embeddings are contiguous float32
        embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
        
        # Get starting ID
        start_id = self.current_id
        
        # Add to index
        self.index.add(embeddings)
        
        # Store metadata
        vector_ids = []
        for i, meta in enumerate(metadata_list):
            vec_id = start_id + i
            self.metadata[vec_id] = meta
            vector_ids.append(vec_id)
        
        self.current_id += len(embeddings)
        
        logger.info(f"Added {len(embeddings)} vectors to index (total: {self.index.ntotal})")
        
        return vector_ids
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of results with metadata and scores
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty or not created")
            return []
        
        # Ensure query is 2D and float32
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        query_embedding = np.ascontiguousarray(query_embedding, dtype=np.float32)
        
        # Search
        top_k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Prepare results
        results = []
        for i in range(top_k):
            idx = int(indices[0][i])
            distance = float(distances[0][i])
            
            if idx == -1:  # No more results
                break
            
            # Convert distance to similarity score
            if self.index_type == "IndexFlatIP":
                # For inner product, higher is better (already similarity)
                score = distance
            else:
                # For L2, lower is better (convert to similarity)
                score = 1.0 / (1.0 + distance)
            
            result = {
                "faiss_id": idx,
                "score": score,
                "distance": distance,
                **self.metadata.get(idx, {})
            }
            results.append(result)
        
        logger.info(f"Found {len(results)} results for query")
        
        return results
    
    def delete_by_doc_id(self, doc_id: str) -> int:
        """
        Delete all vectors associated with a document.
        
        Note: FAISS doesn't support deletion, so we rebuild the index.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            Number of vectors deleted
        """
        if self.index is None:
            return 0
        
        # Find vectors to keep
        vectors_to_keep = []
        metadata_to_keep = []
        
        for vec_id, meta in self.metadata.items():
            if meta.get("doc_id") != doc_id:
                # This vector should be kept
                # We need to extract the vector from the index
                vectors_to_keep.append(vec_id)
                metadata_to_keep.append(meta)
        
        deleted_count = len(self.metadata) - len(vectors_to_keep)
        
        if deleted_count > 0:
            logger.info(f"Deleting {deleted_count} vectors for doc_id: {doc_id}")
            
            # Rebuild index
            if vectors_to_keep:
                # Extract vectors to keep
                embeddings_to_keep = []
                for vec_id in vectors_to_keep:
                    # Reconstruct vector from index
                    vec = self.index.reconstruct(vec_id)
                    embeddings_to_keep.append(vec)
                
                # Create new index
                self.create_index(self.dimension)
                
                # Re-add kept vectors
                if embeddings_to_keep:
                    embeddings_array = np.array(embeddings_to_keep)
                    self.add_vectors(embeddings_array, metadata_to_keep)
            else:
                # No vectors left, create empty index
                self.create_index(self.dimension)
            
            logger.info(f"Deleted {deleted_count} vectors")
        
        return deleted_count
    
    def save_index(self, path: str = None):
        """
        Save index and metadata to disk.
        
        Args:
            path: Optional custom path (uses default if not provided)
        """
        if self.index is None:
            raise ValueError("No index to save")
        
        index_path = Path(path) if path else self.index_path
        metadata_path = index_path.parent / "metadata.pkl"
        
        # Ensure directory exists
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(index_path))
        
        # Save metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                "metadata": self.metadata,
                "current_id": self.current_id,
                "dimension": self.dimension,
                "index_type": self.index_type
            }, f)
        
        logger.info(f"Saved index to {index_path}")
    
    def load_index(self, path: str = None) -> bool:
        """
        Load index and metadata from disk.
        
        Args:
            path: Optional custom path (uses default if not provided)
            
        Returns:
            True if loaded successfully, False otherwise
        """
        index_path = Path(path) if path else self.index_path
        metadata_path = index_path.parent / "metadata.pkl"
        
        if not index_path.exists():
            logger.warning(f"Index file not found: {index_path}")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_path))
            
            # Load metadata
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data["metadata"]
                    self.current_id = data["current_id"]
                    self.dimension = data["dimension"]
                    self.index_type = data.get("index_type", self.index_type)
            
            logger.info(f"Loaded index from {index_path} ({self.index.ntotal} vectors)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index stats
        """
        if self.index is None:
            return {
                "total_vectors": 0,
                "dimension": self.dimension,
                "index_type": self.index_type,
                "is_trained": False
            }
        
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "is_trained": self.index.is_trained,
            "metadata_count": len(self.metadata)
        }
    
    def clear(self):
        """Clear the index and metadata."""
        if self.dimension:
            self.create_index(self.dimension)
        else:
            self.index = None
            self.metadata = {}
            self.current_id = 0
        
        logger.info("Index cleared")


# Global index manager instance
_index_manager: Optional[FaissIndexManager] = None


def get_index_manager(dimension: int = None) -> FaissIndexManager:
    """Get or create global index manager instance."""
    global _index_manager
    
    if _index_manager is None:
        _index_manager = FaissIndexManager(dimension=dimension)
        
        # Try to load existing index
        if not _index_manager.load_index():
            # Create new index if dimension provided
            if dimension:
                _index_manager.create_index(dimension)
    
    return _index_manager
