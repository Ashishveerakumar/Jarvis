"""
Conversation Service - Manages conversation history and context
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    """A single message in a conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    sources: Optional[List[Dict]] = None
    
    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "sources": self.sources
        }


@dataclass
class Conversation:
    """A conversation with message history"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    title: Optional[str] = None
    
    def add_message(self, role: str, content: str, sources: Optional[List[Dict]] = None):
        """Add a message to the conversation"""
        message = Message(role=role, content=content, sources=sources)
        self.messages.append(message)
        
        # Auto-generate title from first user message
        if self.title is None and role == "user":
            self.title = content[:50] + ("..." if len(content) > 50 else "")
        
        return message
    
    def get_context_string(self, max_messages: int = 10) -> str:
        """Get conversation history as a string for context"""
        recent_messages = self.messages[-max_messages:]
        
        context_parts = []
        for msg in recent_messages:
            prefix = "Human" if msg.role == "user" else "Assistant"
            context_parts.append(f"{prefix}: {msg.content}")
        
        return "\n\n".join(context_parts)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "messages": [m.to_dict() for m in self.messages]
        }


class ConversationManager:
    """Manages multiple conversations"""
    
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.current_conversation_id: Optional[str] = None
    
    def create_conversation(self) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation()
        self.conversations[conversation.id] = conversation
        self.current_conversation_id = conversation.id
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def get_current_conversation(self) -> Optional[Conversation]:
        """Get the current active conversation"""
        if self.current_conversation_id:
            return self.conversations.get(self.current_conversation_id)
        return None
    
    def get_or_create_current(self) -> Conversation:
        """Get current conversation or create a new one"""
        conversation = self.get_current_conversation()
        if conversation is None:
            conversation = self.create_conversation()
        return conversation
    
    def switch_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Switch to a different conversation"""
        if conversation_id in self.conversations:
            self.current_conversation_id = conversation_id
            return self.conversations[conversation_id]
        return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            if self.current_conversation_id == conversation_id:
                self.current_conversation_id = None
            return True
        return False
    
    def list_conversations(self) -> List[Dict]:
        """List all conversations"""
        return [
            {
                "id": c.id,
                "title": c.title or "New Conversation",
                "created_at": c.created_at.isoformat(),
                "message_count": len(c.messages)
            }
            for c in sorted(
                self.conversations.values(),
                key=lambda x: x.created_at,
                reverse=True
            )
        ]
    
    def clear_all(self):
        """Clear all conversations"""
        self.conversations.clear()
        self.current_conversation_id = None


# Global conversation manager instance
conversation_manager = ConversationManager()


def get_conversation_manager() -> ConversationManager:
    """Get the conversation manager instance"""
    return conversation_manager
