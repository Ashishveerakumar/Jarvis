"""
Knowledge Service - Handles document ingestion and knowledge retrieval
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import os
from app.services.vector_db_service import get_vector_db_service
from app.services.embedding_service import get_embedding_service


class KnowledgeService:
    """Service for managing the knowledge base"""
    
    def __init__(self):
        self.vector_db = get_vector_db_service()
        self.embedding_service = get_embedding_service()
        
        # Supported file extensions
        self.supported_extensions = {".txt", ".md", ".json", ".csv", ".pdf"}
    
    def ingest_text(
        self,
        text: str,
        source: Optional[str] = None,
        category: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[str]:
        """
        Ingest text into the knowledge base
        
        Args:
            text: Text content to ingest
            source: Source identifier for the text
            category: Category tag for filtering
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of document IDs created
        """
        # Split text into chunks
        chunks = self._chunk_text(text, chunk_size, chunk_overlap)
        
        # Prepare documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": source or "manual_input",
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            if category:
                metadata["category"] = category
            
            documents.append({
                "text": chunk,
                "metadata": metadata
            })
        
        # Store in vector database
        doc_ids = self.vector_db.upsert_documents(documents)
        return doc_ids
    
    def ingest_file(
        self,
        file_path: str,
        category: Optional[str] = None
    ) -> List[str]:
        """
        Ingest a file into the knowledge base
        
        Args:
            file_path: Path to the file
            category: Category tag for filtering
            
        Returns:
            List of document IDs created
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        # Read file content
        content = self._read_file(path)
        
        # Ingest the content
        return self.ingest_text(
            text=content,
            source=str(path),
            category=category
        )
    
    def ingest_directory(
        self,
        directory_path: str,
        category: Optional[str] = None,
        recursive: bool = True
    ) -> Dict[str, List[str]]:
        """
        Ingest all supported files from a directory
        
        Args:
            directory_path: Path to the directory
            category: Category tag for all files
            recursive: Whether to process subdirectories
            
        Returns:
            Dict mapping file paths to their document IDs
        """
        path = Path(directory_path)
        
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid directory: {directory_path}")
        
        results = {}
        
        # Get all files
        if recursive:
            files = path.rglob("*")
        else:
            files = path.glob("*")
        
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    doc_ids = self.ingest_file(str(file_path), category)
                    results[str(file_path)] = doc_ids
                except Exception as e:
                    print(f"Error ingesting {file_path}: {e}")
        
        return results
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> str:
        """
        Retrieve relevant context for a query
        
        Args:
            query: The search query
            top_k: Number of results to retrieve
            category: Optional category filter
            
        Returns:
            Combined context string
        """
        # Build metadata filter
        filter_metadata = None
        if category:
            filter_metadata = {"category": category}
        
        # Search vector database
        results = self.vector_db.search(
            query=query,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        if not results:
            return ""
        
        # Combine results into context string
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "unknown")
            text = result["text"]
            score = result["score"]
            context_parts.append(f"[Source: {source}] (Relevance: {score:.2f})\n{text}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def _chunk_text(
        self,
        text: str,
        chunk_size: int,
        overlap: int
    ) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Handle paragraphs longer than chunk_size
                if len(para) > chunk_size:
                    words = para.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) <= chunk_size:
                            temp_chunk += word + " "
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = word + " "
                    if temp_chunk:
                        current_chunk = temp_chunk
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Add overlap between chunks
        if overlap > 0 and len(chunks) > 1:
            overlapped_chunks = [chunks[0]]
            for i in range(1, len(chunks)):
                prev_words = chunks[i-1].split()[-overlap:]
                overlapped_chunks.append(" ".join(prev_words) + " " + chunks[i])
            chunks = overlapped_chunks
        
        return chunks
    
    def _read_file(self, path: Path) -> str:
        """Read file content based on file type"""
        suffix = path.suffix.lower()
        
        if suffix in {".txt", ".md"}:
            return path.read_text(encoding="utf-8")
        
        elif suffix == ".json":
            import json
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        
        elif suffix == ".csv":
            import csv
            lines = []
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    lines.append(", ".join(row))
            return "\n".join(lines)
        
        elif suffix == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(path))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                raise ImportError("pypdf is required for PDF support. Install with: pip install pypdf")
        
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        return self.vector_db.get_stats()
    
    def clear_knowledge_base(self) -> bool:
        """Clear all documents from the knowledge base"""
        return self.vector_db.delete_all()


# Create service instance
knowledge_service = KnowledgeService()


def get_knowledge_service() -> KnowledgeService:
    """Get the knowledge service instance"""
    return knowledge_service
