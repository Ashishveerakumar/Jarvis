"""
Sample data ingestion script - Populates knowledge base with example content
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.knowledge_service import get_knowledge_service


# Sample knowledge base content
SAMPLE_DOCUMENTS = [
    {
        "text": """
        Personal Assistant User Guide
        
        This personal assistant is powered by a self-hosted LLaMA language model. 
        It can understand natural language queries and provide helpful responses.
        
        Key Features:
        1. Natural Language Understanding - Ask questions in plain English
        2. Knowledge Base Integration - The assistant can search through stored documents
        3. Context-Aware Responses - Uses relevant information to provide accurate answers
        4. Conversation Memory - Maintains context within a conversation
        
        How to Use:
        - Simply type your question in the chat interface
        - The assistant will search the knowledge base for relevant information
        - It will then generate a response based on the context and its training
        """,
        "source": "user_guide",
        "category": "documentation"
    },
    {
        "text": """
        Technical Specifications
        
        Language Model: LLaMA 2 (7B or 13B parameters)
        Quantization: GGUF format with Q4_K_M quantization
        Inference: llama-cpp-python for efficient CPU/GPU inference
        
        Vector Database: Pinecone
        - Dimension: 384 (using all-MiniLM-L6-v2 embeddings)
        - Metric: Cosine similarity
        - Index Type: Serverless
        
        Embedding Model: sentence-transformers/all-MiniLM-L6-v2
        - Fast and efficient for semantic search
        - 384-dimensional embeddings
        - Optimized for similarity tasks
        
        Backend: FastAPI
        - Async API endpoints
        - OpenAPI documentation
        - CORS enabled
        
        Frontend: Streamlit
        - Interactive chat interface
        - Real-time responses
        - Knowledge base management
        """,
        "source": "tech_specs",
        "category": "documentation"
    },
    {
        "text": """
        Frequently Asked Questions
        
        Q: How do I add documents to the knowledge base?
        A: You can add documents through the Streamlit UI sidebar or by using the 
        /api/v1/knowledge/ingest API endpoint.
        
        Q: What file formats are supported?
        A: The system supports .txt, .md, .json, .csv, and .pdf files.
        
        Q: How does the semantic search work?
        A: Documents are converted to vector embeddings using sentence-transformers.
        When you ask a question, your query is also converted to an embedding, and
        the most similar documents are retrieved from Pinecone.
        
        Q: Can I use a different LLM?
        A: Yes! Any GGUF-format model compatible with llama-cpp-python will work.
        Popular alternatives include Mistral, Mixtral, and Phi-2.
        
        Q: Is my data private?
        A: Yes, the LLM runs locally on your machine. Only document embeddings
        are stored in Pinecone (the actual text is stored in metadata).
        """,
        "source": "faq",
        "category": "documentation"
    },
    {
        "text": """
        Project Roadmap 2024
        
        Q1 2024:
        - Initial release with basic chat functionality
        - Pinecone integration for knowledge storage
        - Streamlit-based UI
        
        Q2 2024:
        - Multi-conversation support
        - Improved document chunking
        - PDF and Office document support
        
        Q3 2024:
        - Voice input/output capabilities
        - Mobile-responsive UI
        - Plugin system for extensions
        
        Q4 2024:
        - Multi-model support (GPT, Claude, etc.)
        - Team collaboration features
        - Analytics and usage tracking
        """,
        "source": "roadmap",
        "category": "planning"
    }
]


def ingest_sample_data():
    """Ingest sample documents into the knowledge base"""
    print("=" * 60)
    print("Sample Data Ingestion")
    print("=" * 60)
    print()
    
    knowledge_service = get_knowledge_service()
    
    total_chunks = 0
    
    for i, doc in enumerate(SAMPLE_DOCUMENTS, 1):
        print(f"Ingesting document {i}/{len(SAMPLE_DOCUMENTS)}: {doc['source']}")
        
        try:
            doc_ids = knowledge_service.ingest_text(
                text=doc["text"],
                source=doc["source"],
                category=doc.get("category")
            )
            
            chunks = len(doc_ids)
            total_chunks += chunks
            print(f"  ✅ Created {chunks} chunks")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print()
    print("=" * 60)
    print(f"Ingestion complete! Total chunks created: {total_chunks}")
    print("=" * 60)


if __name__ == "__main__":
    ingest_sample_data()
