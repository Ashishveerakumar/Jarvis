"""
Streamlit Chatbot UI for Personal Assistant
"""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional


# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"


# Page configuration
st.set_page_config(
    page_title="Personal Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better chat appearance
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .source-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        background-color: #e8f5e9;
        border-radius: 0.25rem;
        font-size: 0.8rem;
    }
    .stSidebar {
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "use_knowledge_base" not in st.session_state:
        st.session_state.use_knowledge_base = True
    if "category_filter" not in st.session_state:
        st.session_state.category_filter = None
    if "api_connected" not in st.session_state:
        st.session_state.api_connected = False


def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data
        return None
    except Exception:
        return None


def send_message(message: str) -> dict:
    """Send a message to the API and get a response"""
    try:
        payload = {
            "message": message,
            "use_knowledge_base": st.session_state.use_knowledge_base,
            "category_filter": st.session_state.category_filter,
            "stream": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json=payload,
            timeout=120  # LLM responses can take time
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The model may be processing a complex query."}
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to the API. Make sure the server is running."}
    except Exception as e:
        return {"error": str(e)}


def ingest_document(text: str, source: str, category: Optional[str] = None) -> dict:
    """Ingest a document into the knowledge base"""
    try:
        payload = {
            "text": text,
            "source": source,
            "category": category
        }
        
        response = requests.post(
            f"{API_BASE_URL}/knowledge/ingest",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def search_knowledge(query: str, top_k: int = 5) -> dict:
    """Search the knowledge base"""
    try:
        payload = {
            "query": query,
            "top_k": top_k,
            "category": st.session_state.category_filter
        }
        
        response = requests.post(
            f"{API_BASE_URL}/knowledge/search",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_knowledge_stats() -> dict:
    """Get knowledge base statistics"""
    try:
        response = requests.get(f"{API_BASE_URL}/knowledge/stats", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": "Could not fetch stats"}
    except Exception:
        return {"error": "Could not connect to API"}


def render_sidebar():
    """Render the sidebar with settings and knowledge management"""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # API Status
        st.subheader("API Status")
        health = check_api_health()
        if health:
            st.success("✅ Connected")
            col1, col2 = st.columns(2)
            with col1:
                if health.get("llm_loaded"):
                    st.write("🧠 LLM: Ready")
                else:
                    st.write("🧠 LLM: Not loaded")
            with col2:
                if health.get("vector_db_connected"):
                    st.write("📊 DB: Connected")
                else:
                    st.write("📊 DB: Offline")
            st.session_state.api_connected = True
        else:
            st.error("❌ API Offline")
            st.session_state.api_connected = False
        
        st.divider()
        
        # Knowledge Base Settings
        st.subheader("📚 Knowledge Base")
        
        st.session_state.use_knowledge_base = st.toggle(
            "Use Knowledge Base",
            value=st.session_state.use_knowledge_base,
            help="Enable/disable context retrieval from knowledge base"
        )
        
        st.session_state.category_filter = st.text_input(
            "Category Filter",
            value=st.session_state.category_filter or "",
            placeholder="Filter by category",
            help="Only search documents with this category"
        ) or None
        
        # Knowledge base stats
        if st.session_state.api_connected:
            with st.expander("📊 Knowledge Base Stats"):
                stats = get_knowledge_stats()
                if "error" not in stats:
                    st.metric("Total Vectors", stats.get("total_vectors", 0))
                    st.metric("Dimension", stats.get("dimension", 0))
                else:
                    st.write("Could not load stats")
        
        st.divider()
        
        # Document Ingestion
        st.subheader("📄 Add Knowledge")
        
        with st.expander("Add Document"):
            doc_text = st.text_area(
                "Document Text",
                height=150,
                placeholder="Paste your document content here..."
            )
            doc_source = st.text_input(
                "Source Name",
                placeholder="e.g., meeting_notes_2024"
            )
            doc_category = st.text_input(
                "Category",
                placeholder="e.g., meetings, research, notes"
            )
            
            if st.button("Add to Knowledge Base", type="primary"):
                if doc_text and doc_source:
                    with st.spinner("Ingesting document..."):
                        result = ingest_document(
                            doc_text,
                            doc_source,
                            doc_category if doc_category else None
                        )
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success(f"✅ Added {result['chunks_created']} chunks")
                else:
                    st.warning("Please provide both text and source name")
        
        st.divider()
        
        # Chat Controls
        st.subheader("💬 Chat Controls")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()


def render_chat():
    """Render the main chat interface"""
    st.title("🤖 Personal Assistant")
    st.caption("Powered by self-hosted LLaMA with Pinecone knowledge retrieval")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message.get("sources"):
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.markdown(
                            f"<span class='source-badge'>{source['source']} "
                            f"(relevance: {source['relevance']:.2f})</span>",
                            unsafe_allow_html=True
                        )
    
    # Chat input
    if prompt := st.chat_input("Ask me anything...", disabled=not st.session_state.api_connected):
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(prompt)
                
                if "error" in response:
                    st.error(response["error"])
                    assistant_message = f"Sorry, I encountered an error: {response['error']}"
                else:
                    assistant_message = response.get("response", "I couldn't generate a response.")
                    st.markdown(assistant_message)
                    
                    # Show sources if used
                    sources = response.get("sources", [])
                    if sources and response.get("context_used"):
                        with st.expander("📚 Sources"):
                            for source in sources:
                                st.markdown(
                                    f"**{source['source']}** - "
                                    f"Relevance: {source['relevance']:.2f}"
                                )
                
                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "sources": response.get("sources") if "error" not in response else None
                })
    
    # Show welcome message if no messages
    if not st.session_state.messages:
        st.info(
            "👋 Welcome! I'm your personal assistant powered by a self-hosted LLaMA model. "
            "I can answer questions and use the knowledge base to provide context-aware responses. "
            "Try adding some documents to the knowledge base using the sidebar!"
        )


def render_search_tab():
    """Render the knowledge search interface"""
    st.title("🔍 Knowledge Base Search")
    
    search_query = st.text_input(
        "Search Query",
        placeholder="Enter your search query..."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        top_k = st.number_input("Results", min_value=1, max_value=20, value=5)
    
    if st.button("Search", type="primary") and search_query:
        with st.spinner("Searching..."):
            results = search_knowledge(search_query, top_k)
            
            if "error" in results:
                st.error(results["error"])
            else:
                st.subheader(f"Results ({results['total_results']} found)")
                
                for i, result in enumerate(results.get("results", []), 1):
                    with st.expander(f"Result {i} - Score: {result['score']:.3f}"):
                        st.write(f"**Source:** {result.get('source', 'Unknown')}")
                        st.write(f"**ID:** {result['id']}")
                        st.markdown("---")
                        st.write(result["text"])


def main():
    """Main application entry point"""
    init_session_state()
    
    # Sidebar
    render_sidebar()
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["💬 Chat", "🔍 Search Knowledge"])
    
    with tab1:
        render_chat()
    
    with tab2:
        render_search_tab()


if __name__ == "__main__":
    main()
