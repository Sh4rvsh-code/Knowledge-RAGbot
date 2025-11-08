"""Utility helper functions."""
import hashlib
import uuid
from typing import Optional
from datetime import datetime


def generate_uuid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


def generate_doc_id(filename: str, timestamp: Optional[datetime] = None) -> str:
    """Generate a unique document ID based on filename and timestamp."""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    content = f"{filename}_{timestamp.isoformat()}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA256 hash of file content."""
    return hashlib.sha256(file_content).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def normalize_score(score: float, min_score: float = 0.0, max_score: float = 1.0) -> float:
    """Normalize score to 0-1 range."""
    if max_score == min_score:
        return 0.0
    return (score - min_score) / (max_score - min_score)
