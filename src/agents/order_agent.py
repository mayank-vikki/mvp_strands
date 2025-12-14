"""
==============================================================================
Order Agent - Specialist for Order Management & Tracking
==============================================================================
This agent handles all order-related queries including tracking,
delivery estimates, and order status updates.

Capabilities:
    - Look up orders by ID
    - Track shipments in real-time
    - Provide delivery estimates
    - Access order history
==============================================================================
"""

from strands import Agent
from strands.models import BedrockModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.order_tools import (
    lookup_order,
    track_shipment,
    estimate_delivery,
    get_order_history
)
from utils.config import config

# =============================================================================
# Agent System Prompt
# =============================================================================

ORDER_AGENT_PROMPT = """
You are an Order Management Specialist AI assistant. Your role is to help 
customers track their orders and get delivery information.

## Your Capabilities:
1. **Order Lookup**: Find orders by order ID (format: ORD-XXXX)
2. **Shipment Tracking**: Provide real-time tracking updates
3. **Delivery Estimates**: Calculate expected delivery dates
4. **Order History**: Show customer's past orders

## Guidelines:
- Always ask for the order ID if not provided
- Order IDs are in format ORD-XXXX (e.g., ORD-1001)
- Be empathetic if there are delays
- Provide accurate timeline information
- Offer proactive solutions for delayed orders

## Response Style:
- Be clear and factual about delivery times
- Express empathy for any inconvenience
- Always provide tracking numbers when available
- Summarize order status in simple terms

## Handling Specific Situations:
- **Delayed orders**: Acknowledge the delay, explain the reason, provide new ETA
- **Processing orders**: Explain that shipping info will be available once shipped
- **Delivered orders**: Confirm delivery date and ask if there are any issues
- **Cancelled orders**: Explain the cancellation and refund status

## Tool Usage:
- Use `lookup_order` to find order details by ID
- Use `track_shipment` for real-time tracking info
- Use `estimate_delivery` for delivery predictions
- Use `get_order_history` when customer can't find their order ID
"""


def create_order_agent(callback_handler=None) -> Agent:
    """
    Create and configure the Order Agent.
    
    The Order Agent specializes in helping customers track their orders
    and get delivery information.
    
    Args:
        callback_handler: Optional callback for streaming responses
        
    Returns:
        Configured Agent instance for order operations
        
    Example:
        >>> agent = create_order_agent()
        >>> response = agent("Where is my order ORD-1001?")
    """
    # Configure Bedrock model
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.5,  # Lower temperature for factual responses
        max_tokens=1024,
    )
    
    # Create agent with order-specific tools
    agent = Agent(
        name="order_agent",
        system_prompt=ORDER_AGENT_PROMPT,
        model=model,
        tools=[
            lookup_order,
            track_shipment,
            estimate_delivery,
            get_order_history
        ],
        callback_handler=callback_handler
    )
    
    return agent


# =============================================================================
# Standalone testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Order Agent Test")
    print("=" * 60)
    
    try:
        agent = create_order_agent()
        
        # Test queries
        test_queries = [
            "Where is my order ORD-1001?",
            "Track my shipment ORD-1002",
            "When will ORD-1004 arrive? It seems delayed."
        ]
        
        for query in test_queries:
            print(f"\n>>> Query: {query}")
            print("-" * 40)
            print("[Requires AWS credentials to run]")
            
    except Exception as e:
        print(f"Error: {e}")
