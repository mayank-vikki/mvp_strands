"""
==============================================================================
Swarm Multi-Agent Orchestration
==============================================================================
Implements the Swarm pattern from Strands SDK where agents collaborate
autonomously with dynamic handoffs based on task requirements.

Unlike Agents-as-Tools where a supervisor explicitly routes queries,
Swarm agents can hand off to each other based on their own judgment,
enabling emergent collaboration.

Key Features:
    - Dynamic handoffs between agents
    - Shared working memory
    - No central controller - agents self-organize
    - Collective intelligence through context sharing

Usage:
    from orchestration import create_customer_swarm
    
    swarm = create_customer_swarm()
    result = swarm("I need a laptop, check if it's in stock, and shipping options")
==============================================================================
"""

import logging
from typing import List, Optional, Dict, Any

from strands import Agent
from strands.models import BedrockModel

# Try to import Swarm from strands
try:
    from strands.multiagent import Swarm
    SWARM_AVAILABLE = True
except ImportError:
    SWARM_AVAILABLE = False
    Swarm = None

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config

# Enable logging for multi-agent debugging
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)


# =============================================================================
# Swarm Agent Definitions
# =============================================================================

def _create_swarm_product_agent() -> Agent:
    """Create Product Agent for Swarm with handoff awareness."""
    from tools.product_tools import (
        search_products, get_recommendations,
        compare_products, get_product_details
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )
    
    return Agent(
        name="product_specialist",
        system_prompt="""You are a Product Specialist in a collaborative team of e-commerce experts.

Your expertise: Product search, recommendations, comparisons, specifications.

When to hand off to other agents:
- Hand off to INVENTORY_SPECIALIST if customer asks about stock availability
- Hand off to PRICING_SPECIALIST if customer asks about deals or discounts
- Hand off to REVIEWS_SPECIALIST if customer wants to know customer opinions
- Hand off to LOGISTICS_SPECIALIST if customer asks about shipping

After completing your product-related task, evaluate if another specialist
should continue helping the customer. Use the handoff tool if needed.

Always provide helpful, accurate product information.""",
        model=model,
        tools=[search_products, get_recommendations, 
               compare_products, get_product_details]
    )


def _create_swarm_order_agent() -> Agent:
    """Create Order Agent for Swarm with handoff awareness."""
    from tools.order_tools import (
        lookup_order, track_shipment,
        estimate_delivery, get_order_history
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )
    
    return Agent(
        name="order_specialist",
        system_prompt="""You are an Order Specialist in a collaborative team of e-commerce experts.

Your expertise: Order status, tracking, delivery estimates, order history.

When to hand off to other agents:
- Hand off to LOGISTICS_SPECIALIST for detailed shipping/carrier questions
- Hand off to SUPPORT_SPECIALIST for returns, refunds, or policy questions
- Hand off to PRODUCT_SPECIALIST if customer wants to reorder or find similar products

After completing your order-related task, evaluate if another specialist
should continue helping the customer. Use the handoff tool if needed.

Always provide accurate, helpful order information.""",
        model=model,
        tools=[lookup_order, track_shipment, estimate_delivery, get_order_history]
    )


def _create_swarm_support_agent() -> Agent:
    """Create Support Agent for Swarm with handoff awareness."""
    from tools.support_tools import (
        search_faq, get_policy_info,
        check_return_eligibility, escalate_to_human
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )
    
    return Agent(
        name="support_specialist",
        system_prompt="""You are a Customer Support Specialist in a collaborative team.

Your expertise: FAQ, policies, returns, refunds, human escalation.

When to hand off to other agents:
- Hand off to ORDER_SPECIALIST if customer needs specific order details
- Hand off to PRODUCT_SPECIALIST if customer wants product recommendations
- Hand off to LOGISTICS_SPECIALIST for shipping-related support

You are the escalation point - if issues are complex, use escalate_to_human.
After handling support queries, evaluate if another specialist should help.

Always be empathetic and solution-oriented.""",
        model=model,
        tools=[search_faq, get_policy_info, check_return_eligibility, escalate_to_human]
    )


def _create_swarm_inventory_agent() -> Agent:
    """Create Inventory Agent for Swarm with handoff awareness."""
    from tools.inventory_tools import (
        check_stock_availability, get_warehouse_info,
        check_restock_status, get_inventory_alerts,
        find_nearest_warehouse
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )
    
    return Agent(
        name="inventory_specialist",
        system_prompt="""You are an Inventory Specialist in a collaborative team.

Your expertise: Stock levels, warehouse locations, restock dates, availability.

When to hand off to other agents:
- Hand off to PRODUCT_SPECIALIST if customer wants product details/alternatives
- Hand off to LOGISTICS_SPECIALIST if customer asks about shipping from warehouse
- Hand off to PRICING_SPECIALIST if customer asks about deals on available items

After checking inventory, evaluate if the customer needs help with
ordering, shipping, or finding alternatives. Use handoff if needed.

Provide accurate stock information and helpful alternatives.""",
        model=model,
        tools=[check_stock_availability, get_warehouse_info, check_restock_status,
               get_inventory_alerts, find_nearest_warehouse]
    )


def _create_swarm_pricing_agent() -> Agent:
    """Create Pricing Agent for Swarm with handoff awareness."""
    from tools.pricing_tools import (
        get_active_deals, validate_coupon,
        get_price_history, get_lightning_deals,
        calculate_best_price
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )
    
    return Agent(
        name="pricing_specialist",
        system_prompt="""You are a Pricing Specialist in a collaborative team.

Your expertise: Deals, coupons, discounts, price history, best prices.

When to hand off to other agents:
- Hand off to PRODUCT_SPECIALIST if customer wants more product details
- Hand off to INVENTORY_SPECIALIST if customer asks about availability of deal items
- Hand off to LOGISTICS_SPECIALIST if customer wants to know total cost with shipping

After providing pricing information, evaluate if the customer needs help
ordering or checking availability. Use handoff if needed.

Help customers find the best value.""",
        model=model,
        tools=[get_active_deals, validate_coupon, get_price_history,
               get_lightning_deals, calculate_best_price]
    )


def _create_swarm_reviews_agent() -> Agent:
    """Create Reviews Agent for Swarm with handoff awareness."""
    from tools.reviews_tools import (
        get_product_reviews, get_rating_summary,
        search_reviews, get_review_highlights,
        compare_product_ratings
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )
    
    return Agent(
        name="reviews_specialist",
        system_prompt="""You are a Reviews Specialist in a collaborative team.

Your expertise: Customer reviews, ratings, sentiment, review analysis.

When to hand off to other agents:
- Hand off to PRODUCT_SPECIALIST for detailed specs after reviews
- Hand off to PRICING_SPECIALIST if customer wants to buy after seeing reviews
- Hand off to INVENTORY_SPECIALIST if customer asks about availability

After providing review information, evaluate if customer wants to
proceed with purchase or needs more information. Use handoff if needed.

Provide balanced, insightful review summaries.""",
        model=model,
        tools=[get_product_reviews, get_rating_summary, search_reviews,
               get_review_highlights, compare_product_ratings]
    )


def _create_swarm_logistics_agent() -> Agent:
    """Create Logistics Agent for Swarm with handoff awareness."""
    from tools.logistics_tools import (
        get_shipping_options, get_detailed_tracking,
        get_delivery_slots, calculate_shipping_cost,
        get_carrier_info
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )
    
    return Agent(
        name="logistics_specialist",
        system_prompt="""You are a Logistics Specialist in a collaborative team.

Your expertise: Shipping options, tracking, delivery slots, carriers.

When to hand off to other agents:
- Hand off to ORDER_SPECIALIST for order-specific tracking
- Hand off to SUPPORT_SPECIALIST for delivery issues or complaints
- Hand off to PRICING_SPECIALIST if customer asks about total cost with shipping

After providing shipping information, evaluate if customer needs help
with ordering or has other questions. Use handoff if needed.

Provide clear, accurate shipping information.""",
        model=model,
        tools=[get_shipping_options, get_detailed_tracking, get_delivery_slots,
               calculate_shipping_cost, get_carrier_info]
    )


# =============================================================================
# Swarm Factory
# =============================================================================

def create_customer_swarm(
    entry_agent: str = "product_specialist",
    max_handoffs: int = 10,
    max_iterations: int = 15,
    execution_timeout: float = 300.0
) -> Optional[Any]:
    """
    Create a collaborative Swarm of customer service agents.
    
    The Swarm enables agents to hand off to each other dynamically
    based on the customer's evolving needs during a conversation.
    
    Args:
        entry_agent: Which agent receives the initial query
                    ("product_specialist", "order_specialist", etc.)
        max_handoffs: Maximum agent-to-agent handoffs allowed
        max_iterations: Maximum total iterations across all agents
        execution_timeout: Total timeout in seconds
        
    Returns:
        Swarm instance or None if Swarm not available
        
    Example:
        swarm = create_customer_swarm(entry_agent="product_specialist")
        result = swarm("I want a gaming laptop, is it in stock, and deals?")
        # This might flow: Product → Inventory → Pricing
    """
    if not SWARM_AVAILABLE:
        print("Warning: Strands Swarm not available. Install strands-agents>=1.19")
        return None
    
    # Create all specialist agents
    agents = [
        _create_swarm_product_agent(),
        _create_swarm_order_agent(),
        _create_swarm_support_agent(),
        _create_swarm_inventory_agent(),
        _create_swarm_pricing_agent(),
        _create_swarm_reviews_agent(),
        _create_swarm_logistics_agent()
    ]
    
    # Find entry point agent
    entry_point = None
    for agent in agents:
        if agent.name == entry_agent:
            entry_point = agent
            break
    
    if not entry_point:
        entry_point = agents[0]  # Default to first agent
    
    # Create the Swarm
    swarm = Swarm(
        agents,
        entry_point=entry_point,
        max_handoffs=max_handoffs,
        max_iterations=max_iterations,
        execution_timeout=execution_timeout,
        node_timeout=60.0,  # 1 minute per agent
        # Detect and prevent ping-pong handoffs
        repetitive_handoff_detection_window=6,
        repetitive_handoff_min_unique_agents=3
    )
    
    return swarm


# =============================================================================
# Swarm Result Handler
# =============================================================================

def process_swarm_result(result) -> Dict[str, Any]:
    """
    Process Swarm execution result into a structured format.
    
    Args:
        result: SwarmResult from Swarm execution
        
    Returns:
        Dictionary with processed results
    """
    return {
        "status": str(result.status),
        "final_response": str(result) if result else "No response",
        "agents_involved": [
            node.node_id for node in getattr(result, 'node_history', [])
        ],
        "total_iterations": getattr(result, 'execution_count', 0),
        "execution_time_ms": getattr(result, 'execution_time', 0),
        "token_usage": getattr(result, 'accumulated_usage', {}),
    }


# =============================================================================
# Fallback Swarm (Demo Mode)
# =============================================================================

class FallbackSwarm:
    """
    Fallback Swarm implementation for when Strands Swarm is not available.
    Simulates handoffs using sequential agent calls.
    """
    
    def __init__(self, agents: List[Agent], entry_point: Agent = None):
        """Initialize fallback swarm."""
        self.agents = {agent.name: agent for agent in agents}
        self.entry_point = entry_point or agents[0]
        self.handoff_history = []
    
    def __call__(self, task: str) -> str:
        """Execute task with simulated handoffs."""
        current_agent = self.entry_point
        context = f"User request: {task}"
        max_steps = 5
        
        for step in range(max_steps):
            self.handoff_history.append(current_agent.name)
            
            # Get response from current agent
            response = current_agent(context)
            response_text = str(response)
            
            # Check if response suggests handoff (simplified detection)
            next_agent = self._detect_handoff_suggestion(response_text)
            
            if next_agent and next_agent in self.agents:
                context = f"Previous agent ({current_agent.name}) said: {response_text}\n\nContinue helping with: {task}"
                current_agent = self.agents[next_agent]
            else:
                # No handoff needed, return response
                return response_text
        
        return response_text
    
    def _detect_handoff_suggestion(self, response: str) -> Optional[str]:
        """Detect if response suggests handoff to another agent."""
        handoff_keywords = {
            "product_specialist": ["product", "search", "recommend"],
            "order_specialist": ["order", "tracking", "delivery status"],
            "support_specialist": ["return", "refund", "policy", "help"],
            "inventory_specialist": ["stock", "availability", "warehouse"],
            "pricing_specialist": ["deal", "discount", "coupon", "price"],
            "reviews_specialist": ["review", "rating", "feedback"],
            "logistics_specialist": ["shipping", "carrier", "delivery time"]
        }
        
        response_lower = response.lower()
        
        # Check for explicit handoff mentions
        for agent_name, keywords in handoff_keywords.items():
            if any(f"hand off to {kw}" in response_lower or 
                   f"transfer to {kw}" in response_lower 
                   for kw in keywords):
                return agent_name
        
        return None


def create_demo_swarm() -> FallbackSwarm:
    """
    Create a demo swarm for testing without AWS credentials.
    Uses fallback implementation with simulated handoffs.
    """
    # Create simple demo agents
    from strands import Agent
    
    demo_agents = []
    agent_configs = [
        ("product_specialist", "You are a product specialist. Help with product queries."),
        ("order_specialist", "You are an order specialist. Help with order queries."),
        ("support_specialist", "You are a support specialist. Help with support queries."),
        ("inventory_specialist", "You are an inventory specialist. Help with stock queries."),
        ("pricing_specialist", "You are a pricing specialist. Help with pricing queries."),
        ("reviews_specialist", "You are a reviews specialist. Help with review queries."),
        ("logistics_specialist", "You are a logistics specialist. Help with shipping queries."),
    ]
    
    for name, prompt in agent_configs:
        agent = Agent(name=name, system_prompt=prompt)
        demo_agents.append(agent)
    
    return FallbackSwarm(demo_agents, demo_agents[0])


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Swarm Multi-Agent Pattern - Customer Service Team")
    print("=" * 70)
    
    print("\nSwarm Available:", SWARM_AVAILABLE)
    
    if SWARM_AVAILABLE:
        print("\nCreating customer service swarm...")
        swarm = create_customer_swarm(entry_agent="product_specialist")
        print("Swarm created successfully!")
        print("\nExample usage:")
        print('  result = swarm("I want a gaming laptop, check stock and any deals")')
        print("  # Flow: Product → Inventory → Pricing")
    else:
        print("\nStrands Swarm not available. Using fallback implementation.")
        print("Install strands-agents>=1.19 for full Swarm support.")
