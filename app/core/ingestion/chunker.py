"""Text chunking strategies for document processing."""
from typing import List, Dict, Any
from dataclasses import dataclass

from app.config import settings
from app.utils.logger import app_logger as logger


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    chunk_text: str
    doc_id: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_text": self.chunk_text,
            "doc_id": self.doc_id,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "metadata": self.metadata
        }


class RecursiveChunker:
    """
    Recursive character-level text chunking with overlap.
    
    Splits text on separators in order: ["\\n\\n", "\\n", ". ", " "]
    Maintains source document references and character offsets for highlighting.
    """
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: List[str] = None
    ):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting (in priority order)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        
        logger.info(
            f"Initialized RecursiveChunker with chunk_size={self.chunk_size}, "
            f"overlap={self.chunk_overlap}"
        )
    
    def chunk(
        self,
        text: str,
        doc_id: str,
        metadata: Dict[str, Any] = None
    ) -> List[Chunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            doc_id: Document identifier
            metadata: Additional metadata to attach to chunks
            
        Returns:
            List of Chunk objects
        """
        if not text:
            logger.warning(f"Empty text provided for doc_id: {doc_id}")
            return []
        
        metadata = metadata or {}
        chunks = []
        
        # Split text recursively
        splits = self._split_text_recursive(text, self.separators)
        
        # Create chunks with overlap
        current_chunk = []
        current_length = 0
        current_start_char = 0
        chunk_index = 0
        
        for i, split in enumerate(splits):
            split_length = len(split)
            
            # Check if adding this split would exceed chunk size
            if current_length + split_length > self.chunk_size and current_chunk:
                # Create chunk from accumulated splits
                chunk_text = "".join(current_chunk)
                chunk_end_char = current_start_char + len(chunk_text)
                
                chunks.append(Chunk(
                    chunk_text=chunk_text,
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    start_char=current_start_char,
                    end_char=chunk_end_char,
                    metadata={**metadata, "chunk_index": chunk_index}
                ))
                
                chunk_index += 1
                
                # Calculate overlap for next chunk
                overlap_text = chunk_text[-self.chunk_overlap:] if len(chunk_text) > self.chunk_overlap else chunk_text
                current_chunk = [overlap_text, split]
                current_length = len(overlap_text) + split_length
                current_start_char = chunk_end_char - len(overlap_text)
            else:
                # Add split to current chunk
                current_chunk.append(split)
                current_length += split_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = "".join(current_chunk)
            chunk_end_char = current_start_char + len(chunk_text)
            
            chunks.append(Chunk(
                chunk_text=chunk_text,
                doc_id=doc_id,
                chunk_index=chunk_index,
                start_char=current_start_char,
                end_char=chunk_end_char,
                metadata={**metadata, "chunk_index": chunk_index}
            ))
        
        logger.info(f"Created {len(chunks)} chunks for doc_id: {doc_id}")
        return chunks
    
    def _split_text_recursive(
        self,
        text: str,
        separators: List[str]
    ) -> List[str]:
        """
        Recursively split text using separators.
        
        Args:
            text: Text to split
            separators: List of separators to try
            
        Returns:
            List of text splits
        """
        if not separators:
            return [text]
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        if separator == "":
            # Base case: split into characters
            return list(text)
        
        # Split by current separator
        splits = text.split(separator)
        
        # If no split occurred, try next separator
        if len(splits) == 1:
            return self._split_text_recursive(text, remaining_separators)
        
        # Recursively split each piece if still too large
        final_splits = []
        for i, split in enumerate(splits):
            # Re-add separator except for last split
            if i < len(splits) - 1:
                split = split + separator
            
            # If split is still too large, split it further
            if len(split) > self.chunk_size:
                final_splits.extend(
                    self._split_text_recursive(split, remaining_separators)
                )
            else:
                final_splits.append(split)
        
        return final_splits
    
    def chunk_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, List[Chunk]]:
        """
        Chunk multiple documents in batch.
        
        Args:
            documents: List of dicts with 'text', 'doc_id', and 'metadata'
            
        Returns:
            Dictionary mapping doc_id to list of chunks
        """
        result = {}
        
        for doc in documents:
            doc_id = doc.get("doc_id")
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            
            chunks = self.chunk(text, doc_id, metadata)
            result[doc_id] = chunks
        
        total_chunks = sum(len(chunks) for chunks in result.values())
        logger.info(f"Chunked {len(documents)} documents into {total_chunks} total chunks")
        
        return result


class FixedSizeChunker:
    """Simple fixed-size chunking with overlap (alternative strategy)."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """Initialize fixed-size chunker."""
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def chunk(
        self,
        text: str,
        doc_id: str,
        metadata: Dict[str, Any] = None
    ) -> List[Chunk]:
        """
        Split text into fixed-size chunks.
        
        Args:
            text: Text to chunk
            doc_id: Document identifier
            metadata: Additional metadata
            
        Returns:
            List of Chunk objects
        """
        metadata = metadata or {}
        chunks = []
        
        start = 0
        chunk_index = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_text = text[start:end]
            
            chunks.append(Chunk(
                chunk_text=chunk_text,
                doc_id=doc_id,
                chunk_index=chunk_index,
                start_char=start,
                end_char=end,
                metadata={**metadata, "chunk_index": chunk_index}
            ))
            
            chunk_index += 1
            start = end - self.chunk_overlap
        
        logger.info(f"Created {len(chunks)} fixed-size chunks for doc_id: {doc_id}")
        return chunks
