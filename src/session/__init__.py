"""
==============================================================================
Session Management Package
==============================================================================
Provides session persistence for maintaining conversation state across
multiple interactions. Supports both local file storage and AWS S3.

Features:
    - Conversation history persistence
    - Agent state storage
    - Multi-turn context awareness
    - Automatic state recovery
    
Session Managers:
    - FileSessionManager: Local filesystem storage (development)
    - S3SessionManager: AWS S3 storage (production)
==============================================================================
"""

from .session_manager import (
    SessionConfig,
    ConversationContext,
    create_session_manager,
    get_or_create_session,
    save_conversation_turn,
    load_conversation_history,
    clear_session,
    SESSION_AVAILABLE,
)

__all__ = [
    "SessionConfig",
    "ConversationContext",
    "create_session_manager",
    "get_or_create_session",
    "save_conversation_turn",
    "load_conversation_history",
    "clear_session",
    "SESSION_AVAILABLE",
]
