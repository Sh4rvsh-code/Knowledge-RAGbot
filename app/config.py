"""Application configuration using Pydantic settings."""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application Settings
    app_name: str = Field(default="RAG Document Q&A System", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_reload: bool = Field(default=False, alias="API_RELOAD")
    
    # LLM Configuration
    llm_provider: Literal["gemini", "openai", "anthropic", "huggingface", "local", "free"] = Field(
        default="gemini", 
        alias="LLM_PROVIDER"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", alias="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, alias="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=500, alias="OPENAI_MAX_TOKENS")
    
    # Anthropic Configuration
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", alias="ANTHROPIC_MODEL")
    
    # Google Gemini Configuration (FREE with generous limits!)
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")
    
    # Hugging Face Configuration (FREE!)
    huggingface_api_key: str = Field(default="", alias="HUGGINGFACE_API_KEY")
    huggingface_model: str = Field(default="google/flan-t5-xxl", alias="HUGGINGFACE_MODEL")
    
    # Local LLM Configuration
    local_model_name: str = Field(default="google/flan-t5-small", alias="LOCAL_MODEL_NAME")
    local_model_max_length: int = Field(default=512, alias="LOCAL_MODEL_MAX_LENGTH")
    
    # Embedding Model
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL"
    )
    embedding_batch_size: int = Field(default=32, alias="EMBEDDING_BATCH_SIZE")
    
    # Chunking Configuration
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")
    
    # Retrieval Configuration
    top_k_results: int = Field(default=5, alias="TOP_K_RESULTS")
    similarity_threshold: float = Field(default=0.3, alias="SIMILARITY_THRESHOLD")
    
    # File Storage
    upload_dir: str = Field(default="data/uploads", alias="UPLOAD_DIR")
    max_upload_size_mb: int = Field(default=50, alias="MAX_UPLOAD_SIZE_MB")
    data_dir: str = Field(default="data", alias="DATA_DIR")
    
    # FAISS Index
    faiss_index_dir: str = Field(default="data/faiss_index", alias="FAISS_INDEX_DIR")
    faiss_index_type: str = Field(default="IndexFlatIP", alias="FAISS_INDEX_TYPE")
    index_dir: str = Field(default="data/faiss_index", alias="INDEX_DIR")  # Alias for faiss_index_dir
    
    # Database
    database_url: str = Field(default="sqlite:///data/database.db", alias="DATABASE_URL")
    
    # CORS Settings
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:8501"],
        alias="CORS_ORIGINS"
    )
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_upload_size_mb * 1024 * 1024
    
    @property
    def faiss_index_path(self) -> str:
        """Full path to FAISS index file."""
        return os.path.join(self.faiss_index_dir, "index.faiss")
    
    @property
    def faiss_metadata_path(self) -> str:
        """Full path to FAISS metadata file."""
        return os.path.join(self.faiss_index_dir, "metadata.pkl")
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.faiss_index_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Create data directory
        os.makedirs("data", exist_ok=True)


# Global settings instance
settings = Settings()

# Ensure all directories exist
settings.ensure_directories()
