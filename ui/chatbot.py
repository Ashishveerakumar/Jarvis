"""
Streamlit Chatbot UI for JARVIS AI Assistant
"""
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional


# Configuration
API_BASE_URL = "http://localhost:9000/api/v1"


# Page configuration
st.set_page_config(
    page_title="JARVIS AI Assistant",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern dark theme
st.markdown("""
<style>
    /* Dark theme with gradients */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #0f3460 0%, #16213e 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid #53a8b6;
        box-shadow: 0 8px 32px rgba(83, 168, 182, 0.3);
    }
    
    .main-title {
        color: #53a8b6;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        text-shadow: 0 0 20px rgba(83, 168, 182, 0.5);
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        color: #e94560;
        text-align: center;
        font-size: 1.1rem;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(15, 52, 96, 0.6) !important;
        border: 1px solid #53a8b6;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stChatMessageContent"] {
        color: #f0f0f0 !important;
    }
    
    /* User message */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #e94560 0%, #c72c41 100%) !important;
        border-color: #e94560;
    }
    
    /* Assistant message */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%) !important;
        border-color: #53a8b6;
    }
    
    /* Input box */
    .stChatInputContainer {
        background: rgba(15, 52, 96, 0.8);
        border-radius: 25px;
        border: 2px solid #53a8b6;
        padding: 0.5rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f3460 0%, #1a1a2e 100%);
        border-right: 2px solid #53a8b6;
    }
    
    [data-testid="stSidebar"] .element-container {
        color: #f0f0f0;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(90deg, #53a8b6 0%, #0f3460 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(83, 168, 182, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(83, 168, 182, 0.5);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.5rem;
        background: linear-gradient(90deg, #53a8b6 0%, #0f3460 100%);
        border: 1px solid #53a8b6;
        color: white;
        box-shadow: 0 4px 12px rgba(83, 168, 182, 0.3);
    }
    
    .source-chip {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        margin: 0.3rem;
        background: rgba(83, 168, 182, 0.2);
        border: 1px solid #53a8b6;
        border-radius: 15px;
        font-size: 0.85rem;
        color: #53a8b6;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #53a8b6 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(15, 52, 96, 0.6);
        border: 1px solid #53a8b6;
        border-radius: 10px;
        color: #f0f0f0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 52, 96, 0.6);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #53a8b6;
        font-weight: bold;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(15, 52, 96, 0.6);
        border-radius: 10px;
        color: #53a8b6 !important;
        font-weight: bold;
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
        # Title with emoji
        st.markdown("### 🌐 JARVIS Control Panel")
        st.markdown("---")
        
        # API Status with custom badges
        st.markdown("#### System Status")
        health = check_api_health()
        if health:
            st.markdown('<div class="status-badge">🟢 System Online</div>', unsafe_allow_html=True)
            
            # Status grid
            col1, col2 = st.columns(2)
            with col1:
                if health.get("llm_loaded"):
                    st.markdown("**🧠 AI Brain**")
                    st.success("Active")
                else:
                    st.markdown("**🧠 AI Brain**")
                    st.error("Inactive")
            with col2:
                if health.get("vector_db_connected"):
                    st.markdown("**💾 Memory**")
                    st.success("Connected")
                else:
                    st.markdown("**💾 Memory**")
                    st.warning("Offline")
            st.session_state.api_connected = True
        else:
            st.markdown('<div class="status-badge" style="background: linear-gradient(90deg, #e94560 0%, #c72c41 100%);">🔴 System Offline</div>', unsafe_allow_html=True)
            st.session_state.api_connected = False
        
        st.markdown("---")
        
        # Knowledge Base Settings
        st.markdown("#### 🗄️ Knowledge Configuration")
        
        st.session_state.use_knowledge_base = st.toggle(
            "Enable Memory Retrieval",
            value=st.session_state.use_knowledge_base,
            help="Access stored knowledge for contextual responses"
        )
        
        st.session_state.category_filter = st.text_input(
            "🏷️ Filter Category",
            value=st.session_state.category_filter or "",
            placeholder="Filter by category",
            help="Only search documents with this category"
        ) or None
        
        # Knowledge base stats
        if st.session_state.api_connected:
            with st.expander("📊 Memory Analytics"):
                stats = get_knowledge_stats()
                if "error" not in stats:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📚 Vectors", stats.get("total_vectors", 0))
                    with col2:
                        st.metric("🔢 Dimensions", stats.get("dimension", 0))
                else:
                    st.write("⚠️ Analytics unavailable")
        
        st.markdown("---")
        
        # Document Ingestion
        st.markdown("#### 📥 Add New Knowledge")
        
        with st.expander("Upload Document"):
            doc_text = st.text_area(
                "📝 Content",
                height=120,
                placeholder="Enter document content..."
            )
            doc_source = st.text_input(
                "🏷️ Source ID",
                placeholder="document_name_001"
            )
            doc_category = st.text_input(
                "📂 Category",
                placeholder="research | notes | docs"
            )
            
            if st.button("⬆️ Upload to Memory", type="primary", use_container_width=True):
                if doc_text and doc_source:
                    with st.spinner("Processing..."):
                        result = ingest_document(
                            doc_text,
                            doc_source,
                            doc_category if doc_category else None
                        )
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.success(f"✅ Stored {result['chunks_created']} chunks")
                else:
                    st.warning("⚠️ Content and Source required")
        
        st.markdown("---")
        
        # Chat Controls
        st.markdown("#### 🎮 Chat Controls")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_chat():
    """Render the main chat interface"""
    # Custom header
    st.markdown("""
        <div class="main-header">
            <div class="main-title">⚡ JARVIS AI ASSISTANT ⚡</div>
            <div class="sub-title">Powered by LLaMA • Enhanced with Vector Memory</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if available
            if message.get("sources"):
                st.markdown("---")
                st.markdown("**📚 Knowledge Sources:**")
                for source in message["sources"]:
                    st.markdown(
                        f'<span class="source-chip">{source["source"]} '
                        f'• Score: {source["relevance"]:.2f}</span>',
                        unsafe_allow_html=True
                    )
    
    # Chat input
    if prompt := st.chat_input("💬 Ask JARVIS anything...", disabled=not st.session_state.api_connected):
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Processing..."):
                response = send_message(prompt)
                
                if "error" in response:
                    st.error(f"⚠️ {response['error']}")
                    assistant_message = f"System Error: {response['error']}"
                else:
                    assistant_message = response.get("response", "Unable to generate response.")
                    st.markdown(assistant_message)
                    
                    # Show sources if used
                    sources = response.get("sources", [])
                    if sources and response.get("context_used"):
                        st.markdown("---")
                        st.markdown("**📚 Knowledge Sources:**")
                        for source in sources:
                            st.markdown(
                                f'<span class="source-chip">{source["source"]} '
                                f'• Score: {source["relevance"]:.2f}</span>',
                                unsafe_allow_html=True
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
            "👋 **Welcome to JARVIS AI Assistant!**\n\n"
            "I'm an advanced AI powered by a self-hosted LLaMA model with vector memory capabilities. "
            "I can answer questions, retrieve knowledge, and provide intelligent responses.\n\n"
            "💡 **Quick Start:**\n"
            "- Open the sidebar (←) to add knowledge documents\n"
            "- Toggle Memory Retrieval to use stored knowledge\n"
            "- Start chatting with me right away!"
        )


def render_search_tab():
    """Render the knowledge search interface"""
    st.markdown("""
        <div class="main-header">
            <div class="main-title">🔍 MEMORY SEARCH</div>
            <div class="sub-title">Advanced Vector Database Query System</div>
        </div>
    """, unsafe_allow_html=True)
    
    search_query = st.text_input(
        "🔎 Search Query",
        placeholder="Enter keywords to search the knowledge base...",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        top_k = st.number_input("📊 Max Results", min_value=1, max_value=20, value=5)
    with col3:
        st.write("")
        st.write("")
        search_btn = st.button("🚀 Search", type="primary", use_container_width=True)
    
    if search_btn and search_query:
        with st.spinner("🔍 Scanning memory..."):
            results = search_knowledge(search_query, top_k)
            
            if "error" in results:
                st.error(f"⚠️ {results['error']}")
            else:
                st.success(f"✅ Found {results['total_results']} results")
                st.markdown("---")
                
                for i, result in enumerate(results.get("results", []), 1):
                    with st.expander(f"🎯 Result #{i} • Relevance: {result['score']:.3f}"):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.markdown(f"**📁 Source:**")
                            st.markdown(f"**🆔 ID:**")
                        with col2:
                            st.markdown(f"`{result.get('source', 'Unknown')}`")
                            st.markdown(f"`{result['id']}`")
                        st.markdown("---")
                        st.markdown(result["text"])


def main():
    """Main application entry point"""
    init_session_state()
    
    # Sidebar
    render_sidebar()
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["💬 Chat Interface", "🔍 Memory Search"])
    
    with tab1:
        render_chat()
    
    with tab2:
        render_search_tab()


if __name__ == "__main__":
    main()
