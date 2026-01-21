"""
LLM Service - Handles inference with self-hosted LLaMA via Ollama
"""
from typing import Optional, List, Generator
import ollama
from app.config import settings


class LLMService:
    """Service for managing the self-hosted LLM (LLaMA via Ollama)"""
    
    _instance: Optional["LLMService"] = None
    _is_connected: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._is_connected:
            self._check_connection()
    
    def _check_connection(self):
        """Check connection to Ollama server"""
        try:
            # Try to list models to check connection
            models_response = ollama.list()
            self._is_connected = True
            
            # Handle both old and new Ollama API response formats
            models_list = models_response.get('models', []) if isinstance(models_response, dict) else getattr(models_response, 'models', [])
            model_names = []
            for m in models_list:
                # Handle both dict and object formats
                if isinstance(m, dict):
                    name = m.get('name') or m.get('model', '')
                else:
                    name = getattr(m, 'name', '') or getattr(m, 'model', '')
                if name:
                    model_names.append(name)
            
            print(f"Connected to Ollama. Available models: {model_names}")
            
            # Check if the configured model is available
            if settings.ollama_model not in model_names and f"{settings.ollama_model}:latest" not in model_names:
                print(f"Warning: Model '{settings.ollama_model}' not found. Available: {model_names}")
                print(f"Run 'ollama pull {settings.ollama_model}' to download it.")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")
            print("Please ensure Ollama is installed and running.")
            print("Download from: https://ollama.ai/download")
            self._is_connected = False
    
    def is_loaded(self) -> bool:
        """Check if Ollama is connected"""
        return self._is_connected
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        """
        Generate a response using LLaMA via Ollama
        
        Args:
            prompt: User's query/prompt
            context: Retrieved context from vector database
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response
            
        Returns:
            Generated response string or generator for streaming
        """
        if not self.is_loaded():
            return "Ollama not connected. Please ensure Ollama is installed and running."
        
        # Build the full prompt with system instructions and context
        messages = self._build_messages(prompt, context)
        
        options = {
            "temperature": temperature or settings.temperature,
        }
        if max_tokens:
            options["num_predict"] = max_tokens
        
        try:
            if stream:
                return self._stream_response(messages, options)
            else:
                response = ollama.chat(
                    model=settings.ollama_model,
                    messages=messages,
                    options=options
                )
                return response['message']['content'].strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _stream_response(
        self,
        messages: List[dict],
        options: dict
    ) -> Generator[str, None, None]:
        """Stream response tokens"""
        try:
            stream = ollama.chat(
                model=settings.ollama_model,
                messages=messages,
                options=options,
                stream=True
            )
            
            for chunk in stream:
                if chunk.get('message', {}).get('content'):
                    yield chunk['message']['content']
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def _build_messages(self, user_query: str, context: Optional[str] = None) -> List[dict]:
        """
        Build messages for Ollama chat
        
        Args:
            user_query: The user's question
            context: Retrieved context from knowledge base
            
        Returns:
            List of message dictionaries
        """
        system_prompt = """You are a helpful, knowledgeable personal assistant. 
You provide accurate, concise, and helpful responses based on the context provided.
If the context doesn't contain relevant information, use your general knowledge to answer.
Always be polite and professional."""
        
        if context:
            system_prompt += f"""

Here is some relevant information from the knowledge base:
---
{context}
---

Use this information to help answer the user's question."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        return messages
    
    def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            models = ollama.list()
            return [m['name'] for m in models.get('models', [])]
        except Exception:
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull/download a model"""
        try:
            ollama.pull(model_name)
            return True
        except Exception as e:
            print(f"Error pulling model: {e}")
            return False


# Singleton instance
llm_service = LLMService()


def get_llm_service() -> LLMService:
    """Get the LLM service instance"""
    return llm_service
