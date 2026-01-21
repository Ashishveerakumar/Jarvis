"""
Vector Database Service - Pinecone integration for knowledge storage and retrieval
"""
from typing import List, Dict, Optional, Any
from pinecone import Pinecone, ServerlessSpec
from app.config import settings
from app.services.embedding_service import get_embedding_service
import uuid
import time


class VectorDBService:
    """Service for managing Pinecone vector database operations"""
    
    _instance: Optional["VectorDBService"] = None
    _client: Optional[Pinecone] = None
    _index = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Pinecone client and ensure index exists"""
        if not settings.pinecone_api_key:
            print("Warning: Pinecone API key not set. Vector DB features disabled.")
            return
        
        print("Initializing Pinecone client...")
        self._client = Pinecone(api_key=settings.pinecone_api_key)
        
        # Check if index exists, create if not
        self._ensure_index_exists()
        
        # Connect to the index
        self._index = self._client.Index(settings.pinecone_index_name)
        print(f"Connected to Pinecone index: {settings.pinecone_index_name}")
    
    def _ensure_index_exists(self):
        """Create the index if it doesn't exist"""
        existing_indexes = [idx.name for idx in self._client.list_indexes()]
        
        if settings.pinecone_index_name not in existing_indexes:
            print(f"Creating new index: {settings.pinecone_index_name}")
            self._client.create_index(
                name=settings.pinecone_index_name,
                dimension=settings.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.pinecone_environment
                )
            )
            # Wait for index to be ready
            time.sleep(5)
            print(f"Index {settings.pinecone_index_name} created successfully!")
    
    def is_connected(self) -> bool:
        """Check if connected to Pinecone"""
        return self._index is not None
    
    def upsert_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Store a document in the vector database
        
        Args:
            text: The document text to store
            metadata: Optional metadata to associate with the document
            doc_id: Optional document ID (generated if not provided)
            
        Returns:
            The document ID
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to Pinecone")
        
        # Generate embedding
        embedding_service = get_embedding_service()
        embedding = embedding_service.get_embedding(text)
        
        # Generate ID if not provided
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        
        # Prepare metadata
        full_metadata = metadata or {}
        full_metadata["text"] = text[:1000]  # Store truncated text in metadata
        
        # Upsert to Pinecone
        self._index.upsert(
            vectors=[{
                "id": doc_id,
                "values": embedding,
                "metadata": full_metadata
            }]
        )
        
        return doc_id
    
    def upsert_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Store multiple documents in the vector database
        
        Args:
            documents: List of dicts with 'text' and optional 'metadata', 'id'
            
        Returns:
            List of document IDs
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to Pinecone")
        
        embedding_service = get_embedding_service()
        
        # Extract texts and generate embeddings in batch
        texts = [doc["text"] for doc in documents]
        embeddings = embedding_service.get_embeddings(texts)
        
        # Prepare vectors for upsert
        vectors = []
        doc_ids = []
        
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            doc_id = doc.get("id", str(uuid.uuid4()))
            doc_ids.append(doc_id)
            
            metadata = doc.get("metadata", {})
            metadata["text"] = doc["text"][:1000]
            
            vectors.append({
                "id": doc_id,
                "values": embedding,
                "metadata": metadata
            })
        
        # Batch upsert (Pinecone recommends batches of 100)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self._index.upsert(vectors=batch)
        
        return doc_ids
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of matching documents with scores
        """
        if not self.is_connected():
            return []
        
        # Generate query embedding
        embedding_service = get_embedding_service()
        query_embedding = embedding_service.get_embedding(query)
        
        # Search Pinecone
        results = self._index.query(
            vector=query_embedding,
            top_k=top_k or settings.top_k_results,
            include_metadata=True,
            filter=filter_metadata
        )
        
        # Format results
        formatted_results = []
        for match in results.matches:
            if match.score >= settings.similarity_threshold:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata
                })
        
        return formatted_results
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        if not self.is_connected():
            return False
        
        self._index.delete(ids=[doc_id])
        return True
    
    def delete_all(self) -> bool:
        """Delete all documents in the index"""
        if not self.is_connected():
            return False
        
        self._index.delete(delete_all=True)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if not self.is_connected():
            return {"error": "Not connected"}
        
        return self._index.describe_index_stats()


# Singleton instance
vector_db_service = VectorDBService()


def get_vector_db_service() -> VectorDBService:
    """Get the vector DB service instance"""
    return vector_db_service
