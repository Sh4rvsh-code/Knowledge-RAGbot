"""Advanced caching system for RAG bot responses."""
import hashlib
import json
import time
from typing import Optional, Dict, Any, List
from functools import lru_cache
import pickle
from pathlib import Path

from app.utils.logger import app_logger as logger


class RAGCache:
    """
    Multi-level cache for RAG system.
    
    Levels:
    1. Query cache - exact query matches
    2. Semantic cache - similar query matches
    3. Embedding cache - cached chunk embeddings
    """
    
    def __init__(self, cache_dir: str = "data/cache", max_size: int = 500, ttl: int = 600):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache
            max_size: Maximum cache entries (reduced to 500)
            ttl: Time to live in seconds (reduced to 10 minutes for freshness)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size = max_size
        self.ttl = ttl
        
        # Track document versions to invalidate cache when docs change
        self.doc_version = self._get_doc_version()
        
        # In-memory cache for fast access
        self.query_cache: Dict[str, Dict[str, Any]] = {}
        self.embedding_cache: Dict[str, Any] = {}
        
        # Load persistent cache
        self._load_cache()
        
        logger.info(f"Initialized RAGCache with max_size={max_size}, ttl={ttl}s (10 min for freshness)")
    
    def _get_query_hash(self, query: str, provider: str = "default") -> str:
        """Generate hash for query with better normalization."""
        # More aggressive normalization to avoid near-duplicates
        # Remove extra spaces, punctuation variations
        import re
        normalized = re.sub(r'\s+', ' ', query.lower().strip())
        # Remove trailing punctuation
        normalized = normalized.rstrip('?.!,;:')
        key = f"{normalized}:{provider}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_doc_version(self) -> str:
        """Get hash of current document collection for cache validation."""
        try:
            from app.models.database import get_db_manager, Document
            db_manager = get_db_manager()
            db = db_manager.get_session()
            try:
                docs = db.query(Document).all()
                # Create version hash from document IDs and upload dates
                version_str = '|'.join(sorted([f"{d.id}:{d.upload_date}" for d in docs]))
                return hashlib.md5(version_str.encode()).hexdigest()
            finally:
                db.close()
        except Exception:
            return "unknown"
    
    def _load_cache(self):
        """Load cache from disk."""
        try:
            cache_file = self.cache_dir / "query_cache.pkl"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    loaded_data = pickle.load(f)
                    # Check if cache has document version
                    if isinstance(loaded_data, dict) and 'doc_version' in loaded_data:
                        # Validate document version
                        if loaded_data['doc_version'] == self.doc_version:
                            self.query_cache = loaded_data.get('cache', {})
                            logger.info(f"Loaded {len(self.query_cache)} cached queries (version match)")
                        else:
                            logger.info("Document version mismatch - cache invalidated")
                            self.query_cache = {}
                    else:
                        # Old format - just load it but mark as potentially stale
                        self.query_cache = loaded_data if isinstance(loaded_data, dict) else {}
                        logger.warning(f"Loaded cache without version check: {len(self.query_cache)} entries")
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
    
    def _save_cache(self):
        """Save cache to disk with document version."""
        try:
            cache_file = self.cache_dir / "query_cache.pkl"
            # Save with document version for validation on load
            cache_data = {
                'doc_version': self.doc_version,
                'cache': self.query_cache
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    def get(self, query: str, provider: str = "default") -> Optional[Dict[str, Any]]:
        """
        Get cached response for query with validation.
        
        Args:
            query: User query
            provider: LLM provider name
            
        Returns:
            Cached response or None
        """
        # Check if documents changed - invalidate cache if so
        current_version = self._get_doc_version()
        if current_version != self.doc_version:
            logger.info("Document collection changed - clearing cache")
            self.clear()
            self.doc_version = current_version
            return None
        
        query_hash = self._get_query_hash(query, provider)
        
        if query_hash in self.query_cache:
            cached = self.query_cache[query_hash]
            
            # Check if expired (TTL reduced to 10 minutes for freshness)
            if time.time() - cached['timestamp'] > self.ttl:
                logger.debug(f"Cache expired for query: {query[:50]}")
                del self.query_cache[query_hash]
                return None
            
            logger.info(f"Cache HIT for query: {query[:50]} (age: {int(time.time() - cached['timestamp'])}s)")
            cached['cache_hit'] = True
            return cached
        
        logger.debug(f"Cache MISS for query: {query[:50]}")
        return None
    
    def set(
        self,
        query: str,
        answer: str,
        sources: List[Dict[str, Any]],
        provider: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Cache query response.
        
        Args:
            query: User query
            answer: Generated answer
            sources: Retrieved source chunks
            provider: LLM provider name
            metadata: Additional metadata
        """
        # Check size limit
        if len(self.query_cache) >= self.max_size:
            # Remove oldest entry (simple LRU)
            oldest = min(self.query_cache.items(), key=lambda x: x[1]['timestamp'])
            del self.query_cache[oldest[0]]
            logger.debug("Cache full, removed oldest entry")
        
        query_hash = self._get_query_hash(query, provider)
        
        self.query_cache[query_hash] = {
            'query': query,
            'answer': answer,
            'sources': sources,
            'provider': provider,
            'timestamp': time.time(),
            'metadata': metadata or {}
        }
        
        logger.info(f"Cached response for query: {query[:50]}")
        
        # Periodically save to disk (every 10 entries)
        if len(self.query_cache) % 10 == 0:
            self._save_cache()
    
    def clear(self):
        """Clear all cache."""
        self.query_cache.clear()
        self.embedding_cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'query_cache_size': len(self.query_cache),
            'embedding_cache_size': len(self.embedding_cache),
            'cache_dir': str(self.cache_dir),
            'max_size': self.max_size,
            'ttl': self.ttl
        }
    
    def invalidate_by_doc(self, doc_id: str):
        """Invalidate cache entries related to a document."""
        # Remove entries that used this document in sources
        to_remove = []
        for query_hash, cached in self.query_cache.items():
            if any(s.get('doc_id') == doc_id for s in cached.get('sources', [])):
                to_remove.append(query_hash)
        
        for query_hash in to_remove:
            del self.query_cache[query_hash]
        
        if to_remove:
            logger.info(f"Invalidated {len(to_remove)} cache entries for doc {doc_id}")
            self._save_cache()


# Global cache instance
_cache_instance = None


def get_cache() -> RAGCache:
    """Get or create global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RAGCache()
    return _cache_instance
