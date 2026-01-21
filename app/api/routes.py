"""
API Routes for the Personal Assistant
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    KnowledgeStats,
    HealthResponse
)
from app.services.llm_service import get_llm_service
from app.services.knowledge_service import get_knowledge_service
from app.services.vector_db_service import get_vector_db_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check the health status of all services"""
    llm_service = get_llm_service()
    vector_db = get_vector_db_service()
    
    return HealthResponse(
        status="healthy",
        llm_loaded=llm_service.is_loaded(),
        vector_db_connected=vector_db.is_connected()
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get a response from the assistant.
    Optionally uses knowledge base for context-aware responses.
    """
    llm_service = get_llm_service()
    knowledge_service = get_knowledge_service()
    
    context = None
    sources = None
    context_used = False
    
    # Retrieve relevant context from knowledge base
    if request.use_knowledge_base:
        context = knowledge_service.retrieve_context(
            query=request.message,
            category=request.category_filter
        )
        if context:
            context_used = True
            # Get sources for transparency
            results = get_vector_db_service().search(
                query=request.message,
                top_k=3
            )
            sources = [
                {
                    "source": r["metadata"].get("source", "unknown"),
                    "relevance": r["score"]
                }
                for r in results
            ]
    
    # Generate response
    if request.stream:
        return StreamingResponse(
            _stream_response(
                llm_service,
                request.message,
                context,
                request.max_tokens,
                request.temperature
            ),
            media_type="text/event-stream"
        )
    
    response_text = llm_service.generate_response(
        prompt=request.message,
        context=context,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
        stream=False
    )
    
    return ChatResponse(
        response=response_text,
        sources=sources,
        context_used=context_used
    )


async def _stream_response(llm_service, message, context, max_tokens, temperature):
    """Stream response tokens as SSE events"""
    generator = llm_service.generate_response(
        prompt=message,
        context=context,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True
    )
    
    for token in generator:
        yield f"data: {json.dumps({'token': token})}\n\n"
    
    yield "data: [DONE]\n\n"


@router.post("/knowledge/ingest", response_model=DocumentIngestResponse)
async def ingest_document(request: DocumentIngestRequest):
    """Ingest a document into the knowledge base"""
    knowledge_service = get_knowledge_service()
    
    try:
        doc_ids = knowledge_service.ingest_text(
            text=request.text,
            source=request.source,
            category=request.category
        )
        
        return DocumentIngestResponse(
            success=True,
            document_ids=doc_ids,
            chunks_created=len(doc_ids),
            message=f"Successfully ingested document into {len(doc_ids)} chunks"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    """Search the knowledge base"""
    vector_db = get_vector_db_service()
    
    results = vector_db.search(
        query=request.query,
        top_k=request.top_k,
        filter_metadata={"category": request.category} if request.category else None
    )
    
    search_results = [
        SearchResult(
            id=r["id"],
            text=r["text"],
            score=r["score"],
            source=r["metadata"].get("source"),
            metadata=r["metadata"]
        )
        for r in results
    ]
    
    return SearchResponse(
        results=search_results,
        query=request.query,
        total_results=len(search_results)
    )


@router.get("/knowledge/stats", response_model=KnowledgeStats)
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    vector_db = get_vector_db_service()
    
    try:
        stats = vector_db.get_stats()
        
        return KnowledgeStats(
            total_vectors=stats.get("total_vector_count", 0),
            dimension=stats.get("dimension", 384),
            index_fullness=stats.get("index_fullness", 0.0),
            namespaces={
                ns: data.get("vector_count", 0) 
                for ns, data in stats.get("namespaces", {}).items()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/clear")
async def clear_knowledge_base():
    """Clear all documents from the knowledge base"""
    knowledge_service = get_knowledge_service()
    
    try:
        success = knowledge_service.clear_knowledge_base()
        if success:
            return {"message": "Knowledge base cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear knowledge base")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
