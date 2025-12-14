"""
==============================================================================
Agentic Package - LangGraph-based Agent
==============================================================================
This package implements autonomous agent capabilities using LangGraph.

LangGraph provides:
    - Graph-based agent workflows with cycles
    - Built-in state management
    - ReAct pattern support
    - Conditional routing
    - Human-in-the-loop patterns

Usage:
    from agentic import LangGraphAgent, create_langgraph_supervisor
    
    agent = LangGraphAgent()
    result = agent.process("Find me a gaming laptop, check reviews, verify stock")
    
    print(result.final_response)
    print(result.reasoning_trace)
==============================================================================
"""

# LangGraph Agent (Framework-based Implementation)
try:
    from .langgraph_agent import (
        LangGraphAgent,
        LangGraphResult,
        create_langgraph_supervisor,
        LANGGRAPH_AVAILABLE,
    )
except ImportError:
    LANGGRAPH_AVAILABLE = False
    LangGraphAgent = None
    LangGraphResult = None
    create_langgraph_supervisor = None


__all__ = [
    # LangGraph Agent
    "LangGraphAgent",
    "LangGraphResult",
    "create_langgraph_supervisor",
    "LANGGRAPH_AVAILABLE",
]


# Package metadata
__version__ = "1.0.0"
__author__ = "MVP Project Team"
__description__ = "LangGraph-based agentic AI capabilities for autonomous agents"
