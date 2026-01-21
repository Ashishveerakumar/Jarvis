"""
Embedding Service - Generates embeddings for text using sentence-transformers
"""
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from app.config import settings


class EmbeddingService:
    """Service for generating text embeddings"""
    
    _instance: Optional["EmbeddingService"] = None
    _model: Optional[SentenceTransformer] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        print(f"Loading embedding model: {settings.embedding_model}...")
        self._model = SentenceTransformer(settings.embedding_model)
        print("Embedding model loaded successfully!")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        return self._model.get_sentence_embedding_dimension()


# Singleton instance
embedding_service = EmbeddingService()


def get_embedding_service() -> EmbeddingService:
    """Get the embedding service instance"""
    return embedding_service
