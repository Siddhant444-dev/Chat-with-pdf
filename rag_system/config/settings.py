import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG System"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: Optional[str] = None
    
    # Vector Database (Pinecone)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "rag-system"
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    PERPLEXITY_API_KEY: Optional[str] = None
    
    # Document Processing
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FILE_TYPES: list = [".pdf", ".docx", ".doc", ".txt"]
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    
    # Model Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "perplexity"  # Changed to use Perplexity
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings() 