"""
==============================================================================
Session Management for Strands Agents
==============================================================================
Provides session persistence using Strands SDK's built-in session managers
with support for both local file storage and AWS S3.

Usage:
    from session import create_session_manager, SessionConfig
    
    # For development (local files)
    config = SessionConfig(storage_type="file", session_id="user-123")
    session_manager = create_session_manager(config)
    
    # For production (S3)
    config = SessionConfig(
        storage_type="s3",
        session_id="user-123",
        s3_bucket="my-sessions-bucket"
    )
    session_manager = create_session_manager(config)
    
    # Use with agent
    agent = Agent(session_manager=session_manager)
==============================================================================
"""

import os
import json
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path

# Try to import Strands session managers
try:
    from strands.session.file_session_manager import FileSessionManager
    from strands.session.s3_session_manager import S3SessionManager
    STRANDS_SESSIONS_AVAILABLE = True
except ImportError:
    STRANDS_SESSIONS_AVAILABLE = False
    FileSessionManager = None
    S3SessionManager = None

# Module-level flag for availability
SESSION_AVAILABLE = True  # Module itself is always available


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SessionConfig:
    """Configuration for session management."""
    
    # Storage type: "file" or "s3"
    storage_type: str = "file"
    
    # Session identification
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # File storage settings
    storage_dir: str = "./sessions"
    
    # S3 storage settings
    s3_bucket: Optional[str] = None
    s3_prefix: str = "sca-sessions/"
    aws_region: str = "us-east-1"
    
    # Session behavior
    max_history_length: int = 50  # Max conversation turns to keep
    auto_save: bool = True
    
    def __post_init__(self):
        """Generate session_id if not provided."""
        if not self.session_id:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_id = f"session_{timestamp}_{uuid.uuid4().hex[:8]}"


# =============================================================================
# Session Manager Factory
# =============================================================================

def create_session_manager(config: SessionConfig):
    """
    Create a session manager based on configuration.
    
    Args:
        config: SessionConfig with storage settings
        
    Returns:
        FileSessionManager or S3SessionManager instance
        
    Raises:
        ImportError: If Strands session managers not available
        ValueError: If invalid storage_type specified
    """
    if not STRANDS_SESSIONS_AVAILABLE:
        print("Warning: Strands session managers not available, using fallback")
        return FallbackSessionManager(config)
    
    if config.storage_type == "file":
        return FileSessionManager(
            session_id=config.session_id,
            storage_dir=config.storage_dir
        )
    
    elif config.storage_type == "s3":
        if not config.s3_bucket:
            raise ValueError("s3_bucket is required for S3 session storage")
        
        return S3SessionManager(
            session_id=config.session_id,
            bucket=config.s3_bucket,
            prefix=config.s3_prefix,
            region_name=config.aws_region
        )
    
    else:
        raise ValueError(f"Invalid storage_type: {config.storage_type}")


# =============================================================================
# Fallback Session Manager (when Strands not available)
# =============================================================================

class FallbackSessionManager:
    """
    Fallback session manager for when Strands SDK session managers
    are not available. Provides basic file-based persistence.
    """
    
    def __init__(self, config: SessionConfig):
        """Initialize fallback session manager."""
        self.config = config
        self.session_id = config.session_id
        self.storage_dir = Path(config.storage_dir)
        self.session_file = self.storage_dir / f"{self.session_id}.json"
        self._ensure_storage_dir()
        self._session_data = self._load_or_create()
    
    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_or_create(self) -> Dict[str, Any]:
        """Load existing session or create new one."""
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                return json.load(f)
        
        return {
            "session_id": self.session_id,
            "user_id": self.config.user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "state": {},
            "metadata": {}
        }
    
    def save(self):
        """Save session to file."""
        self._session_data["updated_at"] = datetime.now().isoformat()
        with open(self.session_file, 'w') as f:
            json.dump(self._session_data, f, indent=2, default=str)
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self._session_data["messages"].append(message)
        
        # Trim if exceeds max length
        max_len = self.config.max_history_length
        if len(self._session_data["messages"]) > max_len:
            self._session_data["messages"] = self._session_data["messages"][-max_len:]
        
        if self.config.auto_save:
            self.save()
    
    def get_messages(self) -> List[Dict]:
        """Get all messages in conversation history."""
        return self._session_data.get("messages", [])
    
    def set_state(self, key: str, value: Any):
        """Set a state value."""
        self._session_data["state"][key] = value
        if self.config.auto_save:
            self.save()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        return self._session_data["state"].get(key, default)
    
    def clear(self):
        """Clear session data."""
        self._session_data = {
            "session_id": self.session_id,
            "user_id": self.config.user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "state": {},
            "metadata": {}
        }
        self.save()


# =============================================================================
# Convenience Functions
# =============================================================================

# Global session cache
_session_cache: Dict[str, Any] = {}


def get_or_create_session(
    session_id: str = None,
    user_id: str = None,
    storage_type: str = "file",
    **kwargs
) -> Any:
    """
    Get existing session or create new one.
    
    Args:
        session_id: Optional session identifier
        user_id: Optional user identifier
        storage_type: "file" or "s3"
        **kwargs: Additional SessionConfig parameters
        
    Returns:
        Session manager instance
    """
    cache_key = session_id or f"user_{user_id}" or "default"
    
    if cache_key not in _session_cache:
        config = SessionConfig(
            session_id=session_id,
            user_id=user_id,
            storage_type=storage_type,
            **kwargs
        )
        _session_cache[cache_key] = create_session_manager(config)
    
    return _session_cache[cache_key]


def save_conversation_turn(
    session_manager,
    user_message: str,
    assistant_response: str,
    metadata: Dict = None
):
    """
    Save a complete conversation turn (user + assistant).
    
    Args:
        session_manager: Session manager instance
        user_message: User's input
        assistant_response: Assistant's response
        metadata: Optional metadata (e.g., agent used, tools called)
    """
    if isinstance(session_manager, FallbackSessionManager):
        session_manager.add_message("user", user_message)
        session_manager.add_message("assistant", assistant_response, metadata)
    # For Strands session managers, persistence is automatic


def load_conversation_history(session_manager) -> List[Dict]:
    """
    Load conversation history from session.
    
    Args:
        session_manager: Session manager instance
        
    Returns:
        List of message dictionaries
    """
    if isinstance(session_manager, FallbackSessionManager):
        return session_manager.get_messages()
    
    # For Strands session managers, access via agent.messages
    return []


def clear_session(session_manager):
    """
    Clear all session data.
    
    Args:
        session_manager: Session manager instance
    """
    if isinstance(session_manager, FallbackSessionManager):
        session_manager.clear()


# =============================================================================
# Session Context for Multi-Agent Systems
# =============================================================================

@dataclass
class ConversationContext:
    """
    Context object passed between agents in multi-agent systems.
    
    This provides shared state without exposing it to the LLM,
    useful for tracking user preferences, session data, etc.
    """
    session_id: str
    user_id: Optional[str] = None
    
    # User preferences learned during conversation
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Items discussed in current session
    discussed_products: List[str] = field(default_factory=list)
    discussed_orders: List[str] = field(default_factory=list)
    
    # Agent handoff history
    agent_history: List[str] = field(default_factory=list)
    
    # Custom state for tools
    tool_state: Dict[str, Any] = field(default_factory=dict)
    
    def add_agent_visit(self, agent_name: str):
        """Record that an agent was visited."""
        self.agent_history.append(agent_name)
    
    def add_discussed_product(self, product_id: str):
        """Track a product that was discussed."""
        if product_id not in self.discussed_products:
            self.discussed_products.append(product_id)
    
    def add_discussed_order(self, order_id: str):
        """Track an order that was discussed."""
        if order_id not in self.discussed_orders:
            self.discussed_orders.append(order_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "preferences": self.preferences,
            "discussed_products": self.discussed_products,
            "discussed_orders": self.discussed_orders,
            "agent_history": self.agent_history,
            "tool_state": self.tool_state
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        """Create from dictionary."""
        return cls(**data)
