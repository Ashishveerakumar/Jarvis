# Personal Assistant

A personal assistant powered by a self-hosted LLaMA LLM (via Ollama) with knowledge retrieval using Pinecone vector database and a Streamlit chatbot interface.

## Features

- **Self-Hosted LLaMA LLM**: Uses Ollama to run LLaMA models locally (llama2, mistral, codellama, etc.)
- **Knowledge Base**: Store and retrieve information using Pinecone vector database
- **Semantic Search**: Find relevant context using sentence-transformers embeddings
- **Conversational Interface**: Beautiful Streamlit chatbot UI
- **Document Ingestion**: Add documents to the knowledge base for context-aware responses
- **RESTful API**: FastAPI backend with comprehensive endpoints

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI                              │
│                    (Chatbot Interface)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   LLM Service   │  │ Knowledge Svc   │  │ Embedding Svc   │  │
│  │   (Ollama)      │  │ (Ingestion)     │  │ (Transformers)  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│           │                   │                    │             │
│           ▼                   ▼                    ▼             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                   Vector DB Service                         │ │
│  │                    (Pinecone)                               │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.10+
- Ollama installed and running (for self-hosted LLaMA)
- Pinecone account and API key

## Installation

### 1. Install Ollama

Download and install Ollama from [ollama.ai/download](https://ollama.ai/download)

After installation, pull a LLaMA model:
```bash
# Pull LLaMA 2 (7B parameters, ~4GB)
ollama pull llama2

# Or pull Mistral (fast alternative)
ollama pull mistral
```

### 2. Clone and Setup Environment

```bash
cd personal-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Get Pinecone API Key

1. Create a free account at [Pinecone.io](https://www.pinecone.io/)
2. Go to API Keys section
3. Copy your API key

### 4. Configure Environment

```bash
# Copy example environment file
copy .env.example .env

# Edit .env with your settings
```

Required configuration:
```env
# Ollama Configuration (self-hosted LLaMA)
OLLAMA_MODEL=llama2
OLLAMA_HOST=http://localhost:11434

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=personal-assistant
```

### 5. Setup Pinecone

1. Create a free account at [Pinecone.io](https://www.pinecone.io/)
2. Create a new project
3. Copy your API key to the `.env` file
4. The index will be created automatically on first run

## Running the Application

### Start the Backend API

```bash
# From the project root
cd personal-assistant

# Start FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

### Start the Chatbot UI

In a new terminal:

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Start Streamlit UI
streamlit run ui/chatbot.py
```

The UI will be available at: http://localhost:8501

## API Endpoints

### Chat
- `POST /api/v1/chat` - Send a message and get a response

### Knowledge Base
- `POST /api/v1/knowledge/ingest` - Add a document to the knowledge base
- `POST /api/v1/knowledge/search` - Search the knowledge base
- `GET /api/v1/knowledge/stats` - Get knowledge base statistics
- `DELETE /api/v1/knowledge/clear` - Clear the knowledge base

### Health
- `GET /api/v1/health` - Check service health

## Usage Examples

### Adding Knowledge via API

```python
import requests

# Add a document to the knowledge base
response = requests.post(
    "http://localhost:8000/api/v1/knowledge/ingest",
    json={
        "text": "The company was founded in 2020 and is headquartered in San Francisco.",
        "source": "company_info",
        "category": "about"
    }
)
print(response.json())
```

### Chatting via API

```python
import requests

# Send a message
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={
        "message": "When was the company founded?",
        "use_knowledge_base": True
    }
)
print(response.json()["response"])
```

### Using the Streamlit UI

1. Open http://localhost:8501 in your browser
2. Use the sidebar to:
   - Check API connection status
   - Toggle knowledge base usage
   - Add documents to the knowledge base
3. Type messages in the chat input
4. View sources used for responses

## Project Structure

```
personal-assistant/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── main.py             # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py       # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py      # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── llm_service.py       # Ollama/LLaMA integration
│       ├── embedding_service.py  # Sentence transformers
│       ├── vector_db_service.py  # Pinecone integration
│       └── knowledge_service.py  # Knowledge management
├── ui/
│   └── chatbot.py          # Streamlit chatbot interface
├── scripts/
│   ├── download_model.py   # Download LLaMA models via Ollama
│   ├── test_pinecone.py    # Test Pinecone connection
│   └── ingest_sample_data.py  # Sample data ingestion
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .gitignore
└── README.md
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_MODEL` | LLaMA model to use | `llama2` |
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_ENVIRONMENT` | Pinecone region | `us-east-1` |
| `PINECONE_INDEX_NAME` | Index name | `personal-assistant` |
| `MAX_TOKENS` | Max response tokens | `2048` |
| `TEMPERATURE` | Sampling temperature | `0.7` |
| `EMBEDDING_MODEL` | Sentence transformer model | `sentence-transformers/all-MiniLM-L6-v2` |
| `TOP_K_RESULTS` | Number of search results | `5` |
| `SIMILARITY_THRESHOLD` | Minimum similarity score | `0.7` |

## Available LLaMA Models (via Ollama)

- `llama2` - LLaMA 2 7B (recommended, ~4GB)
- `llama2:13b` - LLaMA 2 13B (~8GB)
- `llama2:70b` - LLaMA 2 70B (~40GB)
- `mistral` - Mistral 7B (fast alternative)
- `codellama` - Code-specialized LLaMA

Run `ollama list` to see installed models, or `python scripts/download_model.py --list`.

## Troubleshooting

### Ollama not connecting
- Ensure Ollama is installed and running
- Check that the Ollama service is active
- Verify the model is downloaded: `ollama list`

### Pinecone connection issues
- Verify your API key is correct
- Check your internet connection
- Ensure the index name doesn't contain special characters

### Slow responses
- Try `mistral` for faster responses
- Reduce `MAX_TOKENS` setting
- Use a GPU for faster inference

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
