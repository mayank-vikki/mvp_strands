"""
==============================================================================
Orchestration Package
==============================================================================
Multi-agent orchestration patterns for the Smart Customer Assistant.

Patterns Available:
    - Swarm: Dynamic handoffs between agents (emergent collaboration)
    - Graph: Deterministic workflow pipelines (structured execution)
    
Usage:
    # Swarm Pattern - agents hand off dynamically
    from orchestration import create_customer_swarm
    swarm = create_customer_swarm()
    result = swarm("Help me find a laptop, check stock, and get deals")
    
    # Graph Pattern - structured pipeline
    from orchestration import create_order_workflow
    workflow = create_order_workflow()
    result = workflow("Process order ORD-1001 for shipping")
==============================================================================
"""

from .swarm_orchestrator import (
    create_customer_swarm,
    process_swarm_result,
    FallbackSwarm,
    create_demo_swarm,
    SWARM_AVAILABLE,
)

from .graph_workflow import (
    create_order_workflow,
    create_research_workflow,
    create_stock_check_workflow,
    process_graph_result,
    WorkflowResult,
    FallbackWorkflow,
    GRAPH_AVAILABLE,
)

__all__ = [
    # Swarm Pattern
    "create_customer_swarm",
    "process_swarm_result",
    "FallbackSwarm",
    "create_demo_swarm",
    "SWARM_AVAILABLE",
    
    # Graph Pattern
    "create_order_workflow",
    "create_research_workflow",
    "create_stock_check_workflow",
    "process_graph_result",
    "WorkflowResult",
    "FallbackWorkflow",
    "GRAPH_AVAILABLE",
]
