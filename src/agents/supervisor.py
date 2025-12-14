"""
==============================================================================
Supervisor Agent - Multi-Agent Orchestrator (7 Specialists)
==============================================================================
This is the main orchestrator that routes customer queries to the appropriate
specialist agent using the Strands "Agents-as-Tools" pattern.

Architecture (7-Agent System):
    
    Customer Query → Supervisor → Appropriate Specialist → Response

Specialist Agents:
    1. Product Agent   - Search, recommendations, comparisons
    2. Order Agent     - Order status, tracking, history
    3. Support Agent   - FAQ, policies, returns, escalation
    4. Inventory Agent - Stock levels, warehouses, availability
    5. Pricing Agent   - Deals, coupons, price history
    6. Reviews Agent   - Ratings, reviews, sentiment
    7. Logistics Agent - Shipping, carriers, delivery slots
==============================================================================
"""

from strands import Agent
from strands.models import BedrockModel
from strands import tool

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config

# =============================================================================
# Specialist Agent Cache (Lazy Loading for all 7 agents)
# =============================================================================

_specialist_agents = {}


def _get_product_agent():
    """Lazy load Product Agent."""
    if "product" not in _specialist_agents:
        from agents.product_agent import create_product_agent
        _specialist_agents["product"] = create_product_agent()
    return _specialist_agents["product"]


def _get_order_agent():
    """Lazy load Order Agent."""
    if "order" not in _specialist_agents:
        from agents.order_agent import create_order_agent
        _specialist_agents["order"] = create_order_agent()
    return _specialist_agents["order"]


def _get_support_agent():
    """Lazy load Support Agent."""
    if "support" not in _specialist_agents:
        from agents.support_agent import create_support_agent
        _specialist_agents["support"] = create_support_agent()
    return _specialist_agents["support"]


def _get_inventory_agent():
    """Lazy load Inventory Agent."""
    if "inventory" not in _specialist_agents:
        from agents.inventory_agent import create_inventory_agent
        _specialist_agents["inventory"] = create_inventory_agent()
    return _specialist_agents["inventory"]


def _get_pricing_agent():
    """Lazy load Pricing Agent."""
    if "pricing" not in _specialist_agents:
        from agents.pricing_agent import create_pricing_agent
        _specialist_agents["pricing"] = create_pricing_agent()
    return _specialist_agents["pricing"]


def _get_reviews_agent():
    """Lazy load Reviews Agent."""
    if "reviews" not in _specialist_agents:
        from agents.reviews_agent import create_reviews_agent
        _specialist_agents["reviews"] = create_reviews_agent()
    return _specialist_agents["reviews"]


def _get_logistics_agent():
    """Lazy load Logistics Agent."""
    if "logistics" not in _specialist_agents:
        from agents.logistics_agent import create_logistics_agent
        _specialist_agents["logistics"] = create_logistics_agent()
    return _specialist_agents["logistics"]


# =============================================================================
# Agent-as-Tool Wrappers (7 Specialists)
# =============================================================================

# Global handoff tracker - Streamlit app can read this to show activity
_handoff_tracker = []

def get_handoff_tracker():
    """Get the current handoff tracker list."""
    return _handoff_tracker

def clear_handoff_tracker():
    """Clear the handoff tracker for new query."""
    global _handoff_tracker
    _handoff_tracker = []

def _log_handoff(from_agent: str, to_agent: str, query: str):
    """Log agent handoffs to tracker (for Streamlit UI display)."""
    from datetime import datetime
    
    # Add to global tracker for Streamlit
    _handoff_tracker.append({
        "type": "handoff",
        "from": from_agent,
        "to": to_agent,
        "query": query[:100],
        "time": datetime.now().strftime("%H:%M:%S")
    })
    
    # Terminal logging removed - all activity shown in Streamlit UI

def _log_response(agent: str, response: str):
    """Log agent response to tracker (for Streamlit UI display)."""
    from datetime import datetime
    
    # Add to global tracker for Streamlit
    _handoff_tracker.append({
        "type": "response",
        "agent": agent,
        "response": response[:200],
        "time": datetime.now().strftime("%H:%M:%S")
    })
    
    # Terminal logging removed - all activity shown in Streamlit UI

@tool
def ask_product_specialist(query: str) -> str:
    """
    Delegate product-related queries to the Product Specialist agent.
    
    Use for: Product search, recommendations, comparisons, specifications,
    finding products by features or price range.
    
    Args:
        query: The customer's product-related question
        
    Returns:
        Product specialist's response with search results or recommendations
    """
    try:
        _log_handoff("Supervisor", "Product Specialist", query)
        agent = _get_product_agent()
        response = agent(query)
        _log_response("Product Specialist", str(response))
        return str(response)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[PRODUCT AGENT ERROR]: {error_details}")
        return f"Error from Product Agent: {str(e)}"


@tool
def ask_order_specialist(query: str) -> str:
    """
    Delegate order-related queries to the Order Specialist agent.
    
    Use for: Order status lookup, basic tracking, order history,
    order modifications, cancellations.
    
    Args:
        query: The customer's order-related question
        
    Returns:
        Order specialist's response with order details
    """
    _log_handoff("Supervisor", "Order Specialist", query)
    agent = _get_order_agent()
    response = agent(query)
    _log_response("Order Specialist", str(response))
    return str(response)


@tool
def ask_support_specialist(query: str) -> str:
    """
    Delegate support queries to the Customer Support Specialist agent.
    
    Use for: FAQ questions, policy inquiries, return eligibility,
    general help, human escalation requests.
    
    Args:
        query: The customer's support question
        
    Returns:
        Support specialist's response with help information
    """
    _log_handoff("Supervisor", "Support Specialist", query)
    agent = _get_support_agent()
    response = agent(query)
    _log_response("Support Specialist", str(response))
    return str(response)


@tool
def ask_inventory_specialist(query: str) -> str:
    """
    Delegate inventory queries to the Inventory Specialist agent.
    
    Use for: Stock availability, warehouse information, restock dates,
    inventory alerts, finding nearest warehouse with stock.
    
    Args:
        query: The customer's inventory-related question
        
    Returns:
        Inventory specialist's response with stock information
    """
    _log_handoff("Supervisor", "Inventory Specialist", query)
    agent = _get_inventory_agent()
    response = agent(query)
    _log_response("Inventory Specialist", str(response))
    return str(response)


@tool
def ask_pricing_specialist(query: str) -> str:
    """
    Delegate pricing queries to the Pricing Specialist agent.
    
    Use for: Active deals and promotions, coupon validation,
    price history, lightning deals, calculating best price.
    
    Args:
        query: The customer's pricing-related question
        
    Returns:
        Pricing specialist's response with deal/discount information
    """
    _log_handoff("Supervisor", "Pricing Specialist", query)
    agent = _get_pricing_agent()
    response = agent(query)
    _log_response("Pricing Specialist", str(response))
    return str(response)


@tool
def ask_reviews_specialist(query: str) -> str:
    """
    Delegate review queries to the Reviews Specialist agent.
    
    Use for: Product reviews, ratings, customer feedback,
    review summaries, comparing products by reviews.
    
    Args:
        query: The customer's review-related question
        
    Returns:
        Reviews specialist's response with rating/review information
    """
    _log_handoff("Supervisor", "Reviews Specialist", query)
    agent = _get_reviews_agent()
    response = agent(query)
    _log_response("Reviews Specialist", str(response))
    return str(response)


@tool
def ask_logistics_specialist(query: str) -> str:
    """
    Delegate shipping queries to the Logistics Specialist agent.
    
    Use for: Shipping options and costs, detailed package tracking,
    delivery time slots, carrier information.
    
    Args:
        query: The customer's shipping/logistics question
        
    Returns:
        Logistics specialist's response with shipping information
    """
    _log_handoff("Supervisor", "Logistics Specialist", query)
    agent = _get_logistics_agent()
    response = agent(query)
    _log_response("Logistics Specialist", str(response))
    return str(response)


# =============================================================================
# Supervisor System Prompt (7-Agent System)
# =============================================================================

SUPERVISOR_PROMPT = """
You are the Smart Customer Assistant (SCA) Supervisor - an intelligent AI 
orchestrator for a large e-commerce platform similar to Amazon.

You have access to 7 specialist agents, each expert in their domain.
Your job is to analyze queries and call the APPROPRIATE specialists - often MULTIPLE specialists for complex queries.

## Available Specialists:

### 1. Product Specialist (`ask_product_specialist`)
Expert in: Product search, recommendations, comparisons, specifications
Use when: Customer wants to find, search, browse, compare products
Keywords: laptop, phone, product, recommend, compare, search, features, specs, "under $X", "gaming", "best"

### 2. Order Specialist (`ask_order_specialist`)
Expert in: Order status, tracking, history, modifications
Use when: Customer asks about existing orders
Keywords: order, ORD-, status, where is my, cancel, modify

### 3. Support Specialist (`ask_support_specialist`)
Expert in: FAQ, policies, returns, refunds, human escalation
Use when: Customer asks about policies or needs help
Keywords: return policy, help, refund, exchange, talk to human, FAQ

### 4. Inventory Specialist (`ask_inventory_specialist`)
Expert in: Stock availability, warehouses, restock dates
Use when: Customer asks if something is available or in stock
Keywords: in stock, available, out of stock, when back, warehouse, "check if", "is it available"

### 5. Pricing Specialist (`ask_pricing_specialist`)
Expert in: Deals, coupons, discounts, price history
Use when: Customer asks about prices, deals, or discounts
Keywords: deal, coupon, discount, sale, price history, promo code

### 6. Reviews Specialist (`ask_reviews_specialist`)
Expert in: Customer reviews, ratings, sentiment analysis
Use when: Customer wants to know what others think
Keywords: review, rating, stars, what do customers say, feedback

### 7. Logistics Specialist (`ask_logistics_specialist`)
Expert in: Shipping options, tracking details, delivery scheduling
Use when: Customer asks about shipping or delivery
Keywords: shipping, delivery, carrier, tracking, "shipping to", "delivery options", zip code

## CRITICAL ROUTING RULES:

### Rule 1: ALWAYS call MULTIPLE specialists for multi-part queries
When a query contains multiple distinct needs, you MUST call ALL relevant specialists.

### Rule 2: Identify ALL parts of the query
Break down the query into its components and match each to a specialist.

### Rule 3: Call specialists in logical order
Get product info first, then check inventory, then logistics, etc.

## MULTI-PART QUERY EXAMPLES (IMPORTANT!):

Example 1: "I want a gaming laptop under $1500, check if it's in stock, and what are shipping options to 90210?"
- Part 1: "gaming laptop under $1500" → ask_product_specialist
- Part 2: "check if it's in stock" → ask_inventory_specialist  
- Part 3: "shipping options to 90210" → ask_logistics_specialist
→ YOU MUST CALL ALL THREE SPECIALISTS!

Example 2: "Find me headphones, any deals on them, and what do reviews say?"
- Part 1: "Find headphones" → ask_product_specialist
- Part 2: "any deals" → ask_pricing_specialist
- Part 3: "what do reviews say" → ask_reviews_specialist
→ YOU MUST CALL ALL THREE SPECIALISTS!

Example 3: "Is the Gaming Pro X1 in stock and can you ship to New York?"
- Part 1: "in stock" → ask_inventory_specialist
- Part 2: "ship to New York" → ask_logistics_specialist
→ YOU MUST CALL BOTH SPECIALISTS!

## Single Query Examples:
| Query Example | Route To |
|--------------|----------|
| "Show me gaming laptops" | Product Specialist only |
| "Where is my order ORD-1003?" | Order Specialist only |
| "What's your return policy?" | Support Specialist only |

## Response Synthesis:
After calling all relevant specialists:
1. Combine their responses into ONE cohesive answer
2. Present information in a logical flow
3. Don't mention internal routing to the customer
4. Be conversational and helpful

## REMEMBER:
- For queries with "and", "also", "check if", multiple questions → Call MULTIPLE specialists
- Parse the ENTIRE query before deciding which specialists to call
- When in doubt, call more specialists rather than fewer
- Always provide complete answers covering ALL parts of the customer's question
"""


# =============================================================================
# Supervisor Agent Creation
# =============================================================================

def create_supervisor(callback_handler=None) -> Agent:
    """
    Create the Supervisor Agent with all 7 specialist tools.
    
    This is the main orchestrator that routes queries to appropriate
    specialist agents using the "Agents-as-Tools" pattern.
    
    Args:
        callback_handler: Optional callback for streaming responses
        
    Returns:
        Configured Supervisor Agent
    """
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=2048,
    )
    
    supervisor = Agent(
        name="supervisor",
        system_prompt=SUPERVISOR_PROMPT,
        model=model,
        tools=[
            ask_product_specialist,
            ask_order_specialist,
            ask_support_specialist,
            ask_inventory_specialist,
            ask_pricing_specialist,
            ask_reviews_specialist,
            ask_logistics_specialist
        ],
        callback_handler=callback_handler
    )
    
    return supervisor


# =============================================================================
# Main Entry Point
# =============================================================================

def get_customer_assistant(callback_handler=None) -> Agent:
    """
    Get the main customer assistant (convenience wrapper).
    
    This is the primary interface for the Smart Customer Assistant.
    
    Args:
        callback_handler: Optional callback for streaming responses
        
    Returns:
        The supervisor agent ready to handle customer queries
    """
    return create_supervisor(callback_handler)


# =============================================================================
# Standalone Testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Smart Customer Assistant (SCA) - Supervisor Agent")
    print("=" * 70)
    print()
    print("Architecture: Supervisor -> [Product | Order | Support] Agents")
    print("Pattern: Agents-as-Tools (Multi-Agent Orchestration)")
    print()
    print("-" * 70)
    print("Test Scenarios:")
    print("-" * 70)
    
    test_scenarios = [
        ("Product Query", "I need a laptop for programming under $1200"),
        ("Order Query", "Where is my order ORD-1003?"),
        ("Support Query", "What is your return policy?"),
        ("Mixed Query", "Can I return order ORD-1001 and get a different laptop?"),
    ]
    
    for category, query in test_scenarios:
        print(f"\n[{category}]")
        print(f"  Query: {query}")
        print(f"  [Requires AWS credentials to run]")
    
    print()
    print("-" * 70)
    print("To run: Ensure AWS credentials are configured")
    print("-" * 70)
