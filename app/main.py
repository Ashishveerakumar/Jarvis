"""
FastAPI Application - Personal Assistant Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("=" * 50)
    print("Personal Assistant Starting...")
    print("=" * 50)
    
    # Initialize services (they will load on first access)
    # This is done lazily to improve startup time
    
    print(f"Server running on http://{settings.host}:{settings.port}")
    print("=" * 50)
    
    yield
    
    # Shutdown
    print("Personal Assistant Shutting Down...")


app = FastAPI(
    title="Personal Assistant API",
    description="""
    A personal assistant powered by a self-hosted LLM (LLaMA) 
    with knowledge retrieval using Pinecone vector database.
    
    ## Features
    
    - **Chat**: Conversational interface with context-aware responses
    - **Knowledge Base**: Store and retrieve information using vector search
    - **Document Ingestion**: Add documents to the knowledge base
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["assistant"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Personal Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
