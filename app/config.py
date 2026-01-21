"""
Configuration settings for the Personal Assistant
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Pinecone Configuration
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-east-1"
    pinecone_index_name: str = "personal-assistant"
    
    # Ollama LLM Configuration (self-hosted LLaMA)
    ollama_model: str = "llama2"
    ollama_host: str = "http://localhost:11434"
    max_tokens: int = 2048
    temperature: float = 0.7
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Vector DB Settings
    top_k_results: int = 5
    similarity_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()


settings = get_settings()
