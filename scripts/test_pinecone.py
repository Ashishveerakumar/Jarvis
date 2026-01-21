"""
Script to initialize and test the Pinecone connection
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.services.vector_db_service import get_vector_db_service
from app.services.embedding_service import get_embedding_service


def test_pinecone_connection():
    """Test Pinecone connection and basic operations"""
    print("=" * 60)
    print("Pinecone Connection Test")
    print("=" * 60)
    print()
    
    # Test embedding service
    print("1. Testing Embedding Service...")
    embedding_service = get_embedding_service()
    test_embedding = embedding_service.get_embedding("Hello, world!")
    print(f"   ✅ Embedding generated successfully")
    print(f"   📊 Dimension: {len(test_embedding)}")
    print()
    
    # Test vector database
    print("2. Testing Vector Database Connection...")
    vector_db = get_vector_db_service()
    
    if not vector_db.is_connected():
        print("   ❌ Not connected to Pinecone")
        print("   Please check your PINECONE_API_KEY in .env")
        return False
    
    print("   ✅ Connected to Pinecone")
    print()
    
    # Get stats
    print("3. Getting Index Stats...")
    stats = vector_db.get_stats()
    print(f"   📊 Total vectors: {stats.get('total_vector_count', 0)}")
    print(f"   📏 Dimension: {stats.get('dimension', 'N/A')}")
    print()
    
    # Test upsert
    print("4. Testing Document Upsert...")
    doc_id = vector_db.upsert_document(
        text="This is a test document for the personal assistant.",
        metadata={"source": "test", "category": "testing"}
    )
    print(f"   ✅ Document upserted with ID: {doc_id}")
    print()
    
    # Test search
    print("5. Testing Search...")
    results = vector_db.search("test document personal assistant")
    print(f"   ✅ Search returned {len(results)} results")
    if results:
        print(f"   📝 Top result score: {results[0]['score']:.4f}")
    print()
    
    # Clean up test document
    print("6. Cleaning up test document...")
    vector_db.delete_document(doc_id)
    print("   ✅ Test document deleted")
    print()
    
    print("=" * 60)
    print("All tests passed! Pinecone is configured correctly.")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    test_pinecone_connection()
