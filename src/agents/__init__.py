"""
==============================================================================
Agents Package - 7-Agent Multi-Agent System
==============================================================================
This package contains all agent implementations for the Smart Customer
Assistant (SCA) system.

Agent Hierarchy:
    - Supervisor: Main orchestrator (routes to 7 specialists)
    - ProductAgent: Product search, recommendations, comparisons
    - OrderAgent: Order tracking, status, delivery
    - SupportAgent: FAQ, policies, returns, escalations
    - InventoryAgent: Stock levels, warehouses, availability
    - PricingAgent: Deals, coupons, price history
    - ReviewsAgent: Ratings, reviews, sentiment analysis
    - LogisticsAgent: Shipping options, carriers, delivery slots

Multi-Agent Patterns:
    - Agents-as-Tools: Supervisor routes via tool calls (default)
    - Swarm: Dynamic agent handoffs (emergent collaboration)
    - Graph: Structured workflow pipelines (deterministic)
==============================================================================
"""

from .supervisor import (
    create_supervisor, 
    get_customer_assistant,
    get_handoff_tracker,
    clear_handoff_tracker
)
from .product_agent import create_product_agent
from .order_agent import create_order_agent
from .support_agent import create_support_agent
from .inventory_agent import create_inventory_agent
from .pricing_agent import create_pricing_agent
from .reviews_agent import create_reviews_agent
from .logistics_agent import create_logistics_agent

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Main entry point
    "get_customer_assistant",
    
    # Supervisor
    "create_supervisor",
    
    # Specialist agent factories
    "create_product_agent", 
    "create_order_agent",
    "create_support_agent",
    "create_inventory_agent",
    "create_pricing_agent",
    "create_reviews_agent",
    "create_logistics_agent",
]
