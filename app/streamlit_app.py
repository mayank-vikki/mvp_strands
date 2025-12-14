"""
==============================================================================
Smart Customer Assistant (SCA) - Streamlit UI
==============================================================================
This is the main user interface for the multi-agent customer assistant.

Features:
    - Chat interface with conversation history
    - Agent activity panel showing routing decisions
    - Demo mode for testing without AWS credentials
    - Clean, professional appearance
    - Multiple orchestration patterns (Agents-as-Tools, Swarm, Graph)
    - Session management for conversation persistence

Run with: streamlit run app/streamlit_app.py
==============================================================================
"""

import streamlit as st
import sys
import os
import uuid
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Dict, Any

# Add src directory to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
sys.path.insert(0, SRC_DIR)

# Try importing orchestration modules
try:
    from orchestration import (
        create_customer_swarm, 
        create_order_workflow,
        create_research_workflow,
        create_stock_check_workflow,
        SWARM_AVAILABLE, 
        GRAPH_AVAILABLE
    )
    ORCHESTRATION_AVAILABLE = True
except ImportError:
    ORCHESTRATION_AVAILABLE = False
    SWARM_AVAILABLE = False
    GRAPH_AVAILABLE = False

# Try importing session management
try:
    from session import create_session_manager, SessionConfig, ConversationContext
    SESSION_AVAILABLE = True
except ImportError:
    SESSION_AVAILABLE = False

# Try importing response models
try:
    from models import OrchestrationPattern, AgentType
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Smart Customer Assistant",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# Custom CSS for Better Appearance
# =============================================================================

st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #232f3e 0%, #37475a 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
    }
    
    /* Agent activity card */
    .agent-card {
        background-color: #fff3e0;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #ff9800;
    }
    
    /* Status indicators */
    .status-active { color: #4caf50; }
    .status-idle { color: #9e9e9e; }
    
    /* Thinking container (ChatGPT-style) */
    .thinking-container {
        background-color: #f7f7f8;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9em;
        color: #6e6e80;
        border-left: 3px solid #d1d5db;
    }
    
    .thinking-step {
        margin: 6px 0;
        padding: 4px 0;
        display: flex;
        align-items: flex-start;
    }
    
    .thinking-step-icon {
        margin-right: 8px;
        font-size: 1.1em;
    }
    
    .thinking-step-content {
        flex: 1;
    }
    
    .thinking-step-time {
        font-size: 0.85em;
        color: #9ca3af;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Session State Initialization
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "agent_activity" not in st.session_state:
    st.session_state.agent_activity = []
    
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = True  # Default to demo mode

if "agentic_mode" not in st.session_state:
    st.session_state.agentic_mode = False  # Default to basic mode

if "use_langgraph" not in st.session_state:
    st.session_state.use_langgraph = True  # LangGraph is now the only implementation

# New session state for orchestration patterns
if "orchestration_pattern" not in st.session_state:
    st.session_state.orchestration_pattern = "agents_as_tools"  # Default

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]  # Short session ID

if "graph_workflow" not in st.session_state:
    st.session_state.graph_workflow = "order"  # Default workflow for Graph pattern

if "handoff_history" not in st.session_state:
    st.session_state.handoff_history = []  # Track Swarm handoffs

if "agentic_trace" not in st.session_state:
    st.session_state.agentic_trace = []  # Track agentic reasoning


# =============================================================================
# Demo Response Generator (No AWS Required)
# =============================================================================

def get_demo_response(query: str) -> tuple[str, list]:
    """
    Generate demo responses for testing without AWS credentials.
    
    This simulates what the multi-agent system would do by analyzing
    keywords and returning pre-written responses.
    
    Args:
        query: The user's query
        
    Returns:
        Tuple of (response text, list of agent activities)
    """
    query_lower = query.lower()
    activities = []
    
    # Product-related queries
    if any(word in query_lower for word in ["laptop", "product", "recommend", "compare", "search", "buy"]):
        activities.append({
            "agent": "Supervisor",
            "action": "Analyzed query → Routing to Product Specialist",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        activities.append({
            "agent": "Product Agent",
            "action": "Searching products and generating recommendations",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        if "gaming" in query_lower:
            response = """Based on your gaming needs, here are my top recommendations:

**1. Gaming Pro X1** - $1,299.99 ⭐ 4.7
- 15.6" 144Hz display, RTX 4060, 16GB RAM
- Perfect for AAA gaming and streaming

**2. Gaming Laptop Z** - $1,449.99 ⭐ 4.8  
- 17.3" 165Hz display, RTX 4070, 32GB RAM
- Best for serious gamers

Both offer excellent performance for modern games. Would you like me to compare them in detail?"""
        elif "programming" in query_lower or "coding" in query_lower:
            response = """For programming, I recommend these laptops:

**1. UltraBook Pro 15** - $999.99 ⭐ 4.5
- 15.6" FHD, i7 processor, 16GB RAM, 512GB SSD
- Great for general development

**2. Developer Station** - $1,199.99 ⭐ 4.6
- 14" 2K display, 32GB RAM, 1TB SSD
- Ideal for heavy IDEs and Docker

Would you like more details on either option?"""
        else:
            response = """Here are some popular products matching your search:

**Laptops:**
- UltraBook Pro 15 - $999.99 (4.5⭐)
- Gaming Pro X1 - $1,299.99 (4.7⭐)
- Budget Laptop 14 - $449.99 (4.2⭐)

**Accessories:**
- Wireless Mouse Pro - $49.99 (4.6⭐)
- Mechanical Keyboard - $129.99 (4.8⭐)

Would you like details on any specific product?"""
    
    # Order-related queries
    elif any(word in query_lower for word in ["order", "track", "delivery", "shipping", "ord-"]):
        activities.append({
            "agent": "Supervisor",
            "action": "Analyzed query → Routing to Order Specialist",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        activities.append({
            "agent": "Order Agent",
            "action": "Looking up order information",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        if "ord-1001" in query_lower:
            response = """📦 **Order ORD-1001 Status**

**Status:** ✅ Delivered
**Delivered:** January 15, 2025

**Items:**
- UltraBook Pro 15 (x1) - $999.99

The order was delivered successfully. If you have any issues, I can check return eligibility."""
        elif "ord-1003" in query_lower:
            response = """📦 **Order ORD-1003 Status**

**Status:** 🚚 Shipped (In Transit)
**Carrier:** FedEx
**Tracking:** FX987654321

**Estimated Delivery:** January 21-22, 2025

**Items:**
- Gaming Pro X1 (x1) - $1,299.99

Your package is on its way! Would you like more tracking details?"""
        else:
            response = """I can help you track your order! Here are your recent orders:

| Order ID | Status | Date |
|----------|--------|------|
| ORD-1001 | ✅ Delivered | Jan 10 |
| ORD-1002 | 🚚 Shipped | Jan 15 |
| ORD-1003 | 🚚 In Transit | Jan 17 |

Please provide an order ID (e.g., ORD-1003) for detailed tracking."""
    
    # Support-related queries
    elif any(word in query_lower for word in ["return", "refund", "policy", "help", "faq", "human", "support"]):
        activities.append({
            "agent": "Supervisor",
            "action": "Analyzed query → Routing to Support Specialist",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        activities.append({
            "agent": "Support Agent",
            "action": "Searching FAQ and policy database",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        if "return" in query_lower:
            response = """📋 **Return Policy**

**Standard Returns:**
- Return within 30 days of delivery
- Item must be unused and in original packaging
- Free returns on most items

**Electronics:**
- 15-day return window for opened items
- 30 days if unopened

**Process:**
1. Go to Your Orders
2. Select the item to return
3. Print the prepaid shipping label
4. Drop off at any UPS location

Would you like me to check if a specific order is eligible for return?"""
        elif "human" in query_lower:
            response = """I understand you'd like to speak with a human agent.

🎧 **Contact Options:**
- **Phone:** 1-800-123-4567 (24/7)
- **Live Chat:** Click "Chat with Us" on our website
- **Email:** support@example.com (24-48hr response)

Is there anything I can help with while you wait?"""
        else:
            response = """I'm here to help! Here are some quick answers:

**Common Questions:**
- 📦 **Shipping:** Free on orders over $50
- 🔄 **Returns:** 30 days, hassle-free
- 💳 **Payment:** All major cards + PayPal
- 📞 **Support:** Available 24/7

What would you like to know more about?"""
    
    # Inventory-related queries (NEW)
    elif any(word in query_lower for word in ["stock", "available", "availability", "warehouse", "inventory", "in stock", "out of stock"]):
        activities.append({
            "agent": "Supervisor",
            "action": "Analyzed query → Routing to Inventory Specialist",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        activities.append({
            "agent": "Inventory Agent",
            "action": "Checking stock levels and warehouse availability",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        response = """📦 **Stock Availability Check**

**UltraBook Pro 15** (PROD-001)
| Warehouse | Stock | Status |
|-----------|-------|--------|
| 🏭 WH-WEST (Seattle) | 45 units | ✅ In Stock |
| 🏭 WH-EAST (NYC) | 32 units | ✅ In Stock |
| 🏭 WH-CENTRAL (Chicago) | 12 units | ⚠️ Low Stock |
| 🏭 WH-SOUTH (Dallas) | 0 units | ❌ Out of Stock |

**Nearest Fulfillment Center:** WH-WEST (Seattle)
- Expected restock for WH-SOUTH: Jan 25, 2025

Would you like me to check a specific product or location?"""
    
    # Pricing/deals queries (NEW)
    elif any(word in query_lower for word in ["deal", "discount", "coupon", "promo", "sale", "price", "lightning", "offer"]):
        activities.append({
            "agent": "Supervisor",
            "action": "Analyzed query → Routing to Pricing Specialist",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        activities.append({
            "agent": "Pricing Agent",
            "action": "Finding deals, validating coupons, calculating best prices",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        if "coupon" in query_lower or "promo" in query_lower or "save10" in query_lower:
            response = """🎟️ **Coupon Validation**

**Code: SAVE10** ✅ Valid!
- Type: Percentage Discount
- Value: 10% off
- Minimum purchase: $50
- Expires: February 28, 2025
- Categories: Electronics, Accessories

**Other Active Codes:**
- `WELCOME20` - 20% off first order
- `FREESHIP` - Free shipping over $25
- `TECH15` - 15% off laptops (ends Jan 31)

Would you like me to calculate the best price with these discounts?"""
        else:
            response = """🔥 **Current Deals & Offers**

**⚡ Lightning Deals (Limited Time!):**
- Gaming Pro X1: $1,299 → **$1,099** (15% off) - 2hrs left!
- Wireless Mouse Pro: $49.99 → **$34.99** (30% off) - 4hrs left!

**📅 Active Promotions:**
| Product | Original | Sale | Savings |
|---------|----------|------|---------|
| UltraBook Pro 15 | $999.99 | $899.99 | $100 off |
| Mechanical Keyboard | $129.99 | $99.99 | $30 off |
| USB-C Hub | $79.99 | $59.99 | 25% off |

**Price History Alert:** UltraBook Pro is at its lowest price in 30 days! 📉

Would you like to apply a coupon code?"""
    
    # Reviews queries (NEW)
    elif any(word in query_lower for word in ["review", "rating", "stars", "feedback", "opinion", "rated", "recommend"]):
        activities.append({
            "agent": "Supervisor",
            "action": "Analyzed query → Routing to Reviews Specialist",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        activities.append({
            "agent": "Reviews Agent",
            "action": "Analyzing ratings, reviews, and customer sentiment",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        response = """⭐ **Product Reviews Summary**

**Gaming Pro X1** - Overall: 4.7/5.0 (127 reviews)

**Rating Breakdown:**
- ⭐⭐⭐⭐⭐ 78% (99 reviews)
- ⭐⭐⭐⭐ 15% (19 reviews)
- ⭐⭐⭐ 5% (6 reviews)
- ⭐⭐ 1% (2 reviews)
- ⭐ 1% (1 review)

**✅ Pros (mentioned frequently):**
- "Excellent performance" (45 mentions)
- "Great display quality" (38 mentions)
- "Good value for money" (29 mentions)

**⚠️ Cons (mentioned):**
- "Gets hot under load" (8 mentions)
- "Battery could be better" (5 mentions)

**Featured Review:**
> "Best gaming laptop I've owned! RTX 4060 handles everything..." - ★★★★★ Verified Purchase

Would you like to see specific reviews or compare ratings with other products?"""
    
    # Logistics/shipping queries (NEW)
    elif any(word in query_lower for word in ["ship", "carrier", "fedex", "ups", "usps", "delivery slot", "logistics", "next day", "express"]):
        activities.append({
            "agent": "Supervisor",
            "action": "Analyzed query → Routing to Logistics Specialist",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        activities.append({
            "agent": "Logistics Agent",
            "action": "Calculating shipping options, carriers, and delivery windows",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        response = """🚚 **Shipping Options to Your Area**

**Available Carriers & Speeds:**
| Carrier | Speed | Est. Delivery | Cost |
|---------|-------|---------------|------|
| 📦 Amazon Logistics | Same Day | Today by 9pm | $12.99 |
| 🟤 UPS | Next Day | Tomorrow | $9.99 |
| 🟣 FedEx | 2-Day | Jan 22 | $7.99 |
| 🔵 USPS | Standard | Jan 24-26 | FREE |

**📅 Available Delivery Slots (Tomorrow):**
- 🌅 Morning: 8am - 12pm
- ☀️ Afternoon: 12pm - 5pm
- 🌙 Evening: 5pm - 9pm

**💚 For orders over $50:** Free standard shipping!

Would you like detailed tracking for an existing shipment?"""
    
    # Greeting or general
    else:
        activities.append({
            "agent": "Supervisor",
            "action": "Handling general conversation",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        response = """Hello! 👋 I'm your Smart Customer Assistant powered by **7 AI specialists**.

I can help you with:
- 🛍️ **Products** - Search, compare, get recommendations
- 📦 **Orders** - Track shipments, check status
- ❓ **Support** - Returns, policies, FAQ
- 📊 **Inventory** - Check stock, warehouse availability
- 💰 **Pricing** - Deals, coupons, price history
- ⭐ **Reviews** - Ratings, customer feedback, comparisons
- 🚚 **Logistics** - Shipping options, delivery slots, carriers

What can I help you with today?"""
    
    return response, activities


# =============================================================================
# Swarm Pattern Demo Response
# =============================================================================

def get_swarm_demo_response(query: str) -> tuple[str, list, list]:
    """
    Demo response showing Swarm pattern with dynamic handoffs.
    
    Returns:
        Tuple of (response, activities, handoffs)
    """
    activities = []
    handoffs = []
    query_lower = query.lower()
    
    # Determine initial agent and handoff chain based on query
    if any(word in query_lower for word in ["order", "track", "status", "delivery"]):
        # Order query with potential handoffs
        activities.append({
            "agent": "Swarm Coordinator",
            "action": "Initialized swarm with Order Agent",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        handoffs.append({
            "from": "Coordinator",
            "to": "Order Agent",
            "reason": "Query about order/tracking",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        activities.append({
            "agent": "Order Agent",
            "action": "Retrieved order details, needs logistics info",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        handoffs.append({
            "from": "Order Agent",
            "to": "Logistics Agent",
            "reason": "Need shipping status details",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        activities.append({
            "agent": "Logistics Agent",
            "action": "Provided carrier and delivery window",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        handoffs.append({
            "from": "Logistics Agent",
            "to": "Order Agent",
            "reason": "Returning consolidated response",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        response = """🔄 **Swarm Pattern Response** (3 handoffs)

**Order Status** (via Order Agent → Logistics Agent chain):

📦 **Order #ORD-1003**
- Status: **Out for Delivery**
- Carrier: UPS (handed off from Order Agent)
- Tracking: 1Z999AA10123456784

🚚 **Logistics Details** (from Logistics Agent handoff):
- Driver: En route, 2 stops away
- ETA: Today by 3:00 PM
- Delivery Window: 2:00 PM - 4:00 PM

**Handoff Chain:**
```
Coordinator → Order Agent → Logistics Agent → Order Agent
```

_Dynamic routing allowed Order Agent to request Logistics expertise mid-conversation._"""

    elif any(word in query_lower for word in ["product", "laptop", "recommend", "compare"]):
        # Product query with reviews and pricing handoffs
        activities.append({
            "agent": "Swarm Coordinator",
            "action": "Initialized swarm with Product Agent",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        handoffs.append({
            "from": "Coordinator",
            "to": "Product Agent",
            "reason": "Product inquiry detected",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        activities.append({
            "agent": "Product Agent",
            "action": "Found matching products, requesting reviews",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        handoffs.append({
            "from": "Product Agent",
            "to": "Reviews Agent",
            "reason": "Need customer sentiment data",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        activities.append({
            "agent": "Reviews Agent",
            "action": "Analyzed ratings, handing off for pricing",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        handoffs.append({
            "from": "Reviews Agent",
            "to": "Pricing Agent",
            "reason": "Include current deals",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        activities.append({
            "agent": "Pricing Agent",
            "action": "Applied discounts, returning to coordinator",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        response = """🔄 **Swarm Pattern Response** (4 handoffs)

**Product Recommendation** (multi-agent collaboration):

🎮 **Gaming Pro X1** - $1,199 (via Product → Reviews → Pricing chain)

| Attribute | Details | Source Agent |
|-----------|---------|--------------|
| Specs | RTX 4060, 16GB RAM | Product Agent |
| Rating | ⭐ 4.7/5 (127 reviews) | Reviews Agent |
| Price | ~~$1,399~~ **$1,199** | Pricing Agent |
| Sentiment | 89% positive | Reviews Agent |

**Handoff Chain:**
```
Coordinator → Product → Reviews → Pricing → Coordinator
```

_Each agent contributed specialized knowledge through dynamic handoffs._"""

    else:
        # General query - single agent handles it
        activities.append({
            "agent": "Swarm Coordinator",
            "action": "Initialized swarm with Support Agent",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        handoffs.append({
            "from": "Coordinator",
            "to": "Support Agent",
            "reason": "General inquiry",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        activities.append({
            "agent": "Support Agent",
            "action": "Handled query directly (no handoffs needed)",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        response = """🔄 **Swarm Pattern Response** (1 handoff)

Hello! I'm the Support Agent in a Swarm-based system.

**About Swarm Pattern:**
- Agents can **dynamically hand off** to each other
- No fixed routing - agents decide in real-time
- Enables complex multi-step workflows
- Each agent knows when to escalate

**Available Agents in Swarm:**
🛍️ Product | 📦 Order | ❓ Support | 📊 Inventory | 💰 Pricing | ⭐ Reviews | 🚚 Logistics

Try asking about orders (Order → Logistics chain) or products (Product → Reviews → Pricing chain)!"""

    return response, activities, handoffs


# =============================================================================
# Graph Workflow Demo Response
# =============================================================================

def get_graph_demo_response(query: str, workflow: str) -> tuple[str, list, list]:
    """
    Demo response showing Graph workflow execution.
    
    Returns:
        Tuple of (response, activities, workflow_steps)
    """
    activities = []
    workflow_steps = []
    
    if workflow == "order":
        # Order Fulfillment Pipeline
        activities.append({
            "agent": "Graph Engine",
            "action": "Starting Order Fulfillment Workflow",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        steps = [
            ("Order Agent", "validate_order", "Order validated: ORD-1003"),
            ("Inventory Agent", "check_stock", "Stock confirmed: 5 units available"),
            ("Logistics Agent", "calculate_shipping", "UPS Next-Day selected"),
            ("Order Agent", "confirm_fulfillment", "Fulfillment confirmed")
        ]
        
        for agent, step, result in steps:
            workflow_steps.append({
                "step": step,
                "agent": agent,
                "result": result,
                "status": "✅"
            })
            activities.append({
                "agent": agent,
                "action": f"Step: {step} → {result}",
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        response = """📊 **Graph Workflow: Order Fulfillment Pipeline**

```
[Order Agent] → [Inventory Agent] → [Logistics Agent] → [Confirmation]
     ↓                  ↓                  ↓                  ↓
  Validate          Check Stock       Calc Shipping      Confirm
```

**Execution Steps:**

| Step | Agent | Status | Result |
|------|-------|--------|--------|
| 1. validate_order | Order Agent | ✅ | Order ORD-1003 validated |
| 2. check_stock | Inventory Agent | ✅ | 5 units available |
| 3. calculate_shipping | Logistics Agent | ✅ | UPS Next-Day: $9.99 |
| 4. confirm_fulfillment | Order Agent | ✅ | Ready to ship |

**Workflow Metadata:**
- Pattern: Sequential with conditional edges
- Execution Time: 1.2s
- All nodes completed successfully

_Graph pattern ensures deterministic execution order._"""

    elif workflow == "research":
        # Product Research Pipeline
        activities.append({
            "agent": "Graph Engine",
            "action": "Starting Product Research Workflow",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        steps = [
            ("Product Agent", "search_products", "Found 3 matching products"),
            ("Reviews Agent", "analyze_sentiment", "Aggregated 450 reviews"),
            ("Pricing Agent", "compare_prices", "Price comparison complete"),
            ("Product Agent", "generate_recommendation", "Top pick: Gaming Pro X1")
        ]
        
        for agent, step, result in steps:
            workflow_steps.append({
                "step": step,
                "agent": agent,
                "result": result,
                "status": "✅"
            })
            activities.append({
                "agent": agent,
                "action": f"Step: {step} → {result}",
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        response = """📊 **Graph Workflow: Product Research Pipeline**

```
[Product Agent] ──┬── [Reviews Agent] ───┬── [Recommendation]
                  │                      │
                  └── [Pricing Agent] ───┘
                      (parallel execution)
```

**Execution Steps:**

| Step | Agent | Status | Result |
|------|-------|--------|--------|
| 1. search_products | Product Agent | ✅ | 3 products found |
| 2a. analyze_sentiment | Reviews Agent | ✅ | 450 reviews analyzed |
| 2b. compare_prices | Pricing Agent | ✅ | Price data compiled |
| 3. generate_recommendation | Product Agent | ✅ | Gaming Pro X1 |

**Research Results:**
🏆 **Top Recommendation: Gaming Pro X1**
- Reviews Score: 4.7/5 (89% positive)
- Best Price: $1,199 (14% off)
- Competitor: UltraBook Pro at $1,349

_Graph pattern enabled parallel execution of Reviews + Pricing nodes._"""

    else:  # stock_check
        # Stock Check Pipeline
        activities.append({
            "agent": "Graph Engine",
            "action": "Starting Stock Check Workflow",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        steps = [
            ("Inventory Agent", "check_local_stock", "Local: 2 units"),
            ("Inventory Agent", "check_warehouse_stock", "Warehouse: 15 units"),
            ("Logistics Agent", "estimate_restock", "Restock ETA: 2 days"),
            ("Inventory Agent", "consolidate_report", "Total: 17 units across locations")
        ]
        
        for agent, step, result in steps:
            workflow_steps.append({
                "step": step,
                "agent": agent,
                "result": result,
                "status": "✅"
            })
            activities.append({
                "agent": agent,
                "action": f"Step: {step} → {result}",
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        response = """📊 **Graph Workflow: Stock Check Pipeline**

```
[Inventory Agent] → [Check Local] → [Check Warehouse] → [Logistics] → [Report]
                          ↓               ↓                 ↓
                      Local: 2        Remote: 15        ETA: 2d
```

**Execution Steps:**

| Step | Agent | Status | Result |
|------|-------|--------|--------|
| 1. check_local_stock | Inventory Agent | ✅ | 2 units in local warehouse |
| 2. check_warehouse_stock | Inventory Agent | ✅ | 15 units in regional DC |
| 3. estimate_restock | Logistics Agent | ✅ | Restock ETA: 2 days |
| 4. consolidate_report | Inventory Agent | ✅ | 17 total units |

**Stock Summary:**
| Location | Quantity | Status |
|----------|----------|--------|
| Local Warehouse | 2 | 🟡 Low |
| Regional DC | 15 | 🟢 Good |
| In Transit | 0 | — |

_Graph pattern ensured all inventory sources were checked in correct order._"""

    return response, activities, workflow_steps


def format_thinking_display(handoffs: List[Dict]) -> str:
    """
    Format handoff tracker data into a ChatGPT-style thinking display.
    
    Args:
        handoffs: List of handoff tracker entries
        
    Returns:
        HTML string for thinking container
    """
    if not handoffs:
        return ""
    
    steps_html = []
    for entry in handoffs:
        if entry["type"] == "handoff":
            from_agent = entry["from"]
            to_agent = entry["to"]
            query = entry.get("query", "")
            time_str = entry.get("time", "")
            
            steps_html.append(f"""
            <div class="thinking-step">
                <span class="thinking-step-icon">🔄</span>
                <span class="thinking-step-content">
                    <strong>{from_agent}</strong> → <strong>{to_agent}</strong>
                    <br><small style="color: #9ca3af;">{query[:80]}{'...' if len(query) > 80 else ''}</small>
                </span>
                <span class="thinking-step-time">{time_str}</span>
            </div>
            """)
        elif entry["type"] == "response":
            agent = entry["agent"]
            response = entry.get("response", "")
            time_str = entry.get("time", "")
            
            # Extract thinking from response if present
            thinking_match = re.search(r'<thinking>(.*?)</thinking>', response, re.DOTALL)
            if thinking_match:
                thinking_text = thinking_match.group(1).strip()
                steps_html.append(f"""
                <div class="thinking-step">
                    <span class="thinking-step-icon">💭</span>
                    <span class="thinking-step-content">
                        <strong>{agent}</strong> thinking...
                        <br><small style="color: #9ca3af; font-style: italic;">{thinking_text[:150]}{'...' if len(thinking_text) > 150 else ''}</small>
                    </span>
                    <span class="thinking-step-time">{time_str}</span>
                </div>
                """)
            else:
                steps_html.append(f"""
                <div class="thinking-step">
                    <span class="thinking-step-icon">✅</span>
                    <span class="thinking-step-content">
                        <strong>{agent}</strong> completed
                    </span>
                    <span class="thinking-step-time">{time_str}</span>
                </div>
                """)
    
    if not steps_html:
        return ""
    
    return f"""
    <div class="thinking-container">
        <div style="font-weight: 600; margin-bottom: 8px; color: #6e6e80;">
            🤔 Processing your request...
        </div>
        {''.join(steps_html)}
    </div>
    """


def get_real_response(query: str) -> Tuple[str, List[Dict]]:
    """
    Get response from the actual multi-agent system with detailed activity tracking.
    
    Requires AWS credentials to be configured.
    
    Args:
        query: The user's query
        
    Returns:
        Tuple of (response text, list of agent activities)
    """
    try:
        from agents import (
            get_customer_assistant, 
            get_handoff_tracker, 
            clear_handoff_tracker
        )
        
        # Clear previous handoffs
        clear_handoff_tracker()
        
        activities = [{
            "agent": "🎯 Supervisor",
            "action": "Received query, analyzing intent...",
            "time": datetime.now().strftime("%H:%M:%S")
        }]
        
        # Create and invoke the supervisor
        assistant = get_customer_assistant()
        response = assistant(query)
        
        # Parse response to extract thinking and tool usage
        response_str = str(response)
        
        # Extract thinking tags if present
        thinking_match = re.search(r'<thinking>(.*?)</thinking>', response_str, re.DOTALL)
        if thinking_match:
            thinking_text = thinking_match.group(1).strip()[:200]  # Truncate for display
            activities.append({
                "agent": "🧠 Supervisor",
                "action": f"**Thinking:** {thinking_text}...",
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        # Get actual handoffs from the supervisor's tracker
        handoffs = get_handoff_tracker()
        
        # Agent name mapping for nice display
        agent_icons = {
            "Product Specialist": "🛍️",
            "Order Specialist": "📦",
            "Support Specialist": "🎧",
            "Inventory Specialist": "📊",
            "Pricing Specialist": "💰",
            "Reviews Specialist": "⭐",
            "Logistics Specialist": "🚚",
            "Supervisor": "🎯"
        }
        
        # Convert handoffs to activity entries
        for entry in handoffs:
            if entry["type"] == "handoff":
                to_agent = entry["to"]
                icon = agent_icons.get(to_agent, "🤖")
                activities.append({
                    "agent": f"{icon} {to_agent}",
                    "action": f"**Handoff →** {entry['query'][:60]}...",
                    "time": entry["time"]
                })
            elif entry["type"] == "response":
                agent = entry["agent"]
                icon = agent_icons.get(agent, "🤖")
                activities.append({
                    "agent": f"{icon} {agent}",
                    "action": f"✅ Completed: {entry['response'][:60]}...",
                    "time": entry["time"]
                })
        
        activities.append({
            "agent": "🎯 Supervisor",
            "action": "✅ Generated final response",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        # Clean up thinking tags from final response for cleaner display
        clean_response = re.sub(r'<thinking>.*?</thinking>', '', response_str, flags=re.DOTALL).strip()
        
        return clean_response if clean_response else response_str, activities
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR]: {error_details}")
        return f"Error: {str(e)}\n\nPlease check AWS credentials or enable Demo Mode.", []


def get_swarm_response(query: str) -> Tuple[str, List[Dict], List[Dict]]:
    """
    Get response using the live Swarm orchestration pattern.
    
    Swarm enables dynamic agent handoffs where agents decide
    when to pass work to other specialists.
    
    Args:
        query: The user's query
        
    Returns:
        Tuple of (response text, activities, handoff history)
    """
    try:
        from orchestration import create_customer_swarm, SWARM_AVAILABLE
        
        if not SWARM_AVAILABLE:
            return "Swarm pattern not available. Please use Agents-as-Tools mode.", [], []
        
        activities = [{
            "agent": "🐝 Swarm Coordinator",
            "action": "Initializing swarm agents...",
            "time": datetime.now().strftime("%H:%M:%S")
        }]
        
        handoffs = []
        
        # Create and run swarm
        swarm = create_customer_swarm()
        result = swarm(query)
        
        # Extract the actual response text from SwarmResult
        response_str = ""
        
        # SwarmResult has results dict with agent NodeResults
        if hasattr(result, 'results') and result.results:
            # Get the last agent's response (final output)
            last_agent = None
            if hasattr(result, 'node_history') and result.node_history:
                last_agent = result.node_history[-1].node_id if result.node_history else None
            
            # Try to get response from last agent, or iterate to find best response
            for agent_name, node_result in result.results.items():
                if hasattr(node_result, 'result') and hasattr(node_result.result, 'message'):
                    message = node_result.result.message
                    if isinstance(message, dict) and 'content' in message:
                        for content_item in message['content']:
                            if isinstance(content_item, dict) and 'text' in content_item:
                                # Use the last agent's response as final
                                if last_agent and agent_name == last_agent:
                                    response_str = content_item['text']
                                elif not response_str:
                                    response_str = content_item['text']
        
        # Fallback if parsing failed
        if not response_str:
            response_str = str(result)
        
        # Track which agents participated from node_history
        agent_icon_map = {
            "product_specialist": "🛍️ Product Agent",
            "order_specialist": "📦 Order Agent",
            "inventory_specialist": "📊 Inventory Agent",
            "pricing_specialist": "💰 Pricing Agent",
            "reviews_specialist": "⭐ Reviews Agent",
            "logistics_specialist": "🚚 Logistics Agent",
            "support_specialist": "🎧 Support Agent"
        }
        
        # Build handoff chain from actual node_history
        prev_agent = "🐝 Coordinator"
        if hasattr(result, 'node_history') and result.node_history:
            for node in result.node_history:
                agent_name = agent_icon_map.get(node.node_id, f"🤖 {node.node_id}")
                handoffs.append({
                    "from": prev_agent,
                    "to": agent_name,
                    "reason": f"Dynamic handoff to {node.node_id}"
                })
                activities.append({
                    "agent": agent_name,
                    "action": f"**Handoff** from {prev_agent}",
                    "time": datetime.now().strftime("%H:%M:%S")
                })
                prev_agent = agent_name
        
        activities.append({
            "agent": "🐝 Swarm Coordinator",
            "action": f"✅ Completed with {len(handoffs)} handoffs",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        return response_str, activities, handoffs
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[SWARM ERROR]: {error_details}")
        return f"Swarm Error: {str(e)}", [], []


def get_graph_response(query: str, workflow: str) -> Tuple[str, List[Dict], List[str]]:
    """
    Get response using the live Graph workflow pattern.
    
    Graph workflows execute agents in a deterministic pipeline order.
    
    Args:
        query: The user's query
        workflow: The workflow type ('order', 'research', 'stock_check')
        
    Returns:
        Tuple of (response text, activities, workflow steps executed)
    """
    try:
        from orchestration import (
            create_order_workflow, 
            create_research_workflow, 
            create_stock_check_workflow,
            GRAPH_AVAILABLE
        )
        
        if not GRAPH_AVAILABLE:
            return "Graph pattern not available. Please use Agents-as-Tools mode.", [], []
        
        workflow_names = {
            "order": ("📦 Order Fulfillment", create_order_workflow),
            "research": ("🔍 Product Research", create_research_workflow),
            "stock_check": ("📊 Stock Check", create_stock_check_workflow)
        }
        
        wf_name, wf_creator = workflow_names.get(workflow, workflow_names["order"])
        
        activities = [{
            "agent": "📊 Graph Orchestrator",
            "action": f"Starting **{wf_name}** pipeline...",
            "time": datetime.now().strftime("%H:%M:%S")
        }]
        
        workflow_steps = []
        
        # Create and run workflow
        graph = wf_creator()
        result = graph(query)
        
        # Define expected steps for each workflow
        workflow_step_definitions = {
            "order": ["📦 Order Lookup", "📊 Inventory Check", "🚚 Shipping Calc", "✅ Confirmation"],
            "research": ["🔍 Product Search", "⭐ Review Analysis", "💰 Price Check", "📝 Recommendation"],
            "stock_check": ["📊 Stock Query", "🏭 Warehouse Check", "📍 Location Optimization"]
        }
        
        steps = workflow_step_definitions.get(workflow, ["Step 1", "Step 2", "Step 3"])
        
        for i, step in enumerate(steps, 1):
            workflow_steps.append(step)
            activities.append({
                "agent": f"   Node {i}: {step}",
                "action": "✅ Completed",
                "time": datetime.now().strftime("%H:%M:%S")
            })
        
        activities.append({
            "agent": "📊 Graph Orchestrator",
            "action": f"✅ Pipeline complete ({len(steps)} nodes)",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        return str(result), activities, workflow_steps
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[GRAPH ERROR]: {error_details}")
        return f"Graph Error: {str(e)}", [], []


def get_agentic_response(query: str, use_langgraph: bool = True) -> Tuple[str, List[Dict], Dict]:
    """
    Get response using LangGraph-based agentic agent.
    
    Args:
        query: The user's query
        use_langgraph: Always True (kept for backward compatibility)
        
    Returns:
        Tuple of (response text, list of agent activities, agentic trace dict)
    """
    return get_langgraph_response(query)



def get_langgraph_response(query: str) -> Tuple[str, List[Dict], Dict]:
    """
    Get response using LangGraph-based agentic agent.
    
    This uses LangGraph's native graph execution for:
    - ReAct reasoning loops
    - Goal decomposition
    - Self-reflection
    - Memory persistence
    """
    try:
        from agentic import LangGraphAgent, LANGGRAPH_AVAILABLE
        
        if not LANGGRAPH_AVAILABLE:
            return ("LangGraph is not installed. Please run:\n"
                   "`pip install langgraph langchain-aws`", [], {})
        
        activities = [{
            "agent": "🔷 LangGraph Agent",
            "action": "Initializing LangGraph pipeline...",
            "time": datetime.now().strftime("%H:%M:%S")
        }]
        
        # Get or create LangGraph agent (cached in session state)
        if "langgraph_agent" not in st.session_state:
            st.session_state.langgraph_agent = LangGraphAgent(
                verbose=False,
                enable_reflection=True,
                thread_id=st.session_state.session_id
            )
        
        agent = st.session_state.langgraph_agent
        
        # Process query through LangGraph pipeline
        result = agent.process(query)
        
        # Build activity trace from result
        activities.append({
            "agent": "🎮 Mode Selector",
            "action": f"Selected mode: **{result.processing_mode.upper()}**",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        # Add goal decomposition if present
        if result.goals:
            activities.append({
                "agent": "🎯 Goal Planner",
                "action": f"Decomposed into **{len(result.goals)} sub-goals**",
                "time": datetime.now().strftime("%H:%M:%S")
            })
            for goal in result.goals[:3]:
                activities.append({
                    "agent": "   📌 Sub-goal",
                    "action": f"[{goal.get('id', 'goal')}] {goal.get('description', '')[:50]}...",
                    "time": datetime.now().strftime("%H:%M:%S")
                })
        
        # Add reasoning trace
        if result.reasoning_trace:
            activities.append({
                "agent": "💭 ReAct Loop",
                "action": f"Executed **{len(result.reasoning_trace)}** reasoning steps",
                "time": datetime.now().strftime("%H:%M:%S")
            })
            for i, step in enumerate(result.reasoning_trace[:5], 1):
                step_type = step.get('type', 'unknown')
                thought = step.get('thought', '')[:60]
                activities.append({
                    "agent": f"   🔹 Step {i}",
                    "action": f"**{step_type.upper()}:** {thought}...",
                    "time": step.get('timestamp', datetime.now().strftime("%H:%M:%S"))[:8]
                })
        
        # Add reflection info
        if result.reflection_count > 0:
            activities.append({
                "agent": "🔄 Self-Reflector",
                "action": f"Quality score: **{result.quality_score:.1f}/5** after {result.reflection_count} iteration(s)",
                "time": datetime.now().strftime("%H:%M:%S")
            })
            if result.critiques:
                activities.append({
                    "agent": "   📝 Critique",
                    "action": result.critiques[-1][:60] + "..." if result.critiques else "No critiques",
                    "time": datetime.now().strftime("%H:%M:%S")
                })
        
        # Add completion
        activities.append({
            "agent": "✅ LangGraph Agent",
            "action": f"Completed in **{result.total_time_ms:.0f}ms** ({result.total_steps} steps)",
            "time": datetime.now().strftime("%H:%M:%S")
        })
        
        # Build trace dict
        trace = {
            "mode": result.processing_mode,
            "goals": len([g for g in result.goals if g.get('status') == 'completed']),
            "reasoning_steps": len(result.reasoning_trace),
            "reflections": result.reflection_count,
            "time_ms": result.total_time_ms,
            "quality_score": result.quality_score,
            "critiques": result.critiques,
            "framework": "langgraph"
        }
        
        return result.final_response, activities, trace
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[LANGGRAPH ERROR]: {error_details}")
        return f"LangGraph Error: {str(e)}", [], {"framework": "langgraph", "error": str(e)}


# =============================================================================
# Sidebar - Settings & Info
# =============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/amazon.png", width=60)
    st.title("SCA Settings")
    
    st.divider()
    
    # Mode selection
    st.subheader("🎮 Mode")
    st.session_state.demo_mode = st.toggle(
        "Demo Mode",
        value=st.session_state.demo_mode,
        help="Demo mode works without AWS credentials"
    )
    
    if st.session_state.demo_mode:
        st.info("📌 Demo Mode: Using simulated responses")
    else:
        st.warning("🔐 Live Mode: Requires AWS credentials")
    
    st.divider()
    
    # 🚀 Agentic Mode Toggle
    st.subheader("🧠 Agentic Capabilities")
    st.session_state.agentic_mode = st.toggle(
        "Agentic Mode",
        value=st.session_state.agentic_mode,
        help="Enable ReAct reasoning, Goal Planning, Self-Reflection & Memory"
    )
    
    if st.session_state.agentic_mode:
        st.success("🚀 **Agentic Mode ON**")
        
        # Framework selection
        st.session_state.use_langgraph = st.toggle(
            "Use LangGraph",
            value=st.session_state.use_langgraph,
            help="Use LangGraph framework instead of custom implementation"
        )
        
        if st.session_state.use_langgraph:
            st.info("🔷 **LangGraph Framework**")
            st.caption("""
            **LangGraph Features:**
            - 📊 Graph-based workflows
            - 🔄 Native ReAct loops
            - 💾 Checkpoint memory
            - ⚡ Parallel execution
            """)
        else:
            st.caption("""
            **Custom Implementation:**
            - 💭 ReAct (Think → Act → Observe)
            - 🎯 Goal Decomposition
            - 🔄 Self-Reflection
            - 🧠 Memory System
            """)
    else:
        st.caption("Basic multi-agent routing")
    
    st.divider()
    
    # Orchestration Pattern Selection (NEW)
    st.subheader("🔀 Orchestration Pattern")
    
    pattern_options = {
        "agents_as_tools": "🔧 Agents-as-Tools (Default)",
        "swarm": "🐝 Swarm Pattern (Dynamic Handoffs)",
        "graph": "📊 Graph Workflow (Pipelines)"
    }
    
    st.session_state.orchestration_pattern = st.radio(
        "Select pattern:",
        options=list(pattern_options.keys()),
        format_func=lambda x: pattern_options[x],
        index=list(pattern_options.keys()).index(st.session_state.orchestration_pattern),
        help="Different multi-agent orchestration strategies"
    )
    
    # Pattern-specific options
    if st.session_state.orchestration_pattern == "graph":
        st.caption("Select workflow pipeline:")
        workflow_options = {
            "order": "📦 Order Fulfillment",
            "research": "🔍 Product Research", 
            "stock_check": "📊 Stock Check"
        }
        st.session_state.graph_workflow = st.selectbox(
            "Workflow:",
            options=list(workflow_options.keys()),
            format_func=lambda x: workflow_options[x],
            index=list(workflow_options.keys()).index(st.session_state.graph_workflow)
        )
    
    elif st.session_state.orchestration_pattern == "swarm":
        st.caption("Swarm enables dynamic agent handoffs")
        if st.session_state.handoff_history:
            st.metric("Total Handoffs", len(st.session_state.handoff_history))
    
    st.divider()
    
    # Session Management (NEW)
    st.subheader("💾 Session")
    st.code(f"ID: {st.session_state.session_id}", language=None)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("New Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.messages = []
            st.session_state.agent_activity = []
            st.session_state.handoff_history = []
            st.rerun()
    with col_b:
        if st.button("Export", use_container_width=True):
            export_data = {
                "session_id": st.session_state.session_id,
                "pattern": st.session_state.orchestration_pattern,
                "messages": st.session_state.messages,
                "handoffs": st.session_state.handoff_history
            }
            st.download_button(
                "💾 Download",
                data=json.dumps(export_data, indent=2),
                file_name=f"session_{st.session_state.session_id}.json",
                mime="application/json",
                use_container_width=True
            )
    
    st.divider()
    
    # System architecture info (updated)
    st.subheader("🏗️ Architecture")
    
    if st.session_state.orchestration_pattern == "agents_as_tools":
        st.markdown("""
        ```
        Customer Query
             ↓
        [Supervisor Agent]
             ↓
        ┌──┬──┬──┬──┬──┬──┬──┐
        ↓  ↓  ↓  ↓  ↓  ↓  ↓
        P  O  S  I  $  R  L
        ```
        **Pattern:** Supervisor routes to specialists
        """)
    elif st.session_state.orchestration_pattern == "swarm":
        st.markdown("""
        ```
        Customer Query
             ↓
        [Swarm Coordinator]
             ↓
        Agent A ←→ Agent B
             ↓         ↓
        Agent C ←→ Agent D
        ```
        **Pattern:** Dynamic agent handoffs
        """)
    else:  # graph
        st.markdown("""
        ```
        [Start] → [Agent 1]
                      ↓
                 [Agent 2]
                  ↙    ↘
        [Agent 3]   [Agent 4]
                  ↘    ↙
                  [End]
        ```
        **Pattern:** Deterministic workflow pipeline
        """)
    
    st.caption("**7 Specialist Agents:**\nProduct | Order | Support\nInventory | Pricing | Reviews | Logistics")
    
    st.divider()
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_activity = []
        st.session_state.handoff_history = []
        st.rerun()
    
    st.divider()
    
    # Sample queries (pattern-aware)
    st.subheader("💡 Try These")
    
    if st.session_state.orchestration_pattern == "swarm":
        sample_queries = [
            "Track order ORD-1003",  # Order → Logistics chain
            "Recommend a gaming laptop",  # Product → Reviews → Pricing chain
            "What's your return policy?",
        ]
    elif st.session_state.orchestration_pattern == "graph":
        sample_queries = [
            "Process order ORD-1003",  # Order workflow
            "Research gaming laptops",  # Research workflow
            "Check stock for laptop SKU-001",  # Stock workflow
        ]
    else:
        sample_queries = [
            "Recommend a gaming laptop under $1500",
            "Track order ORD-1003",
            "What's your return policy?",
            "Compare laptop options for coding",
        ]
    
    for query in sample_queries:
        if st.button(query, key=f"sample_{query}", use_container_width=True):
            st.session_state.sample_query = query


# =============================================================================
# Main Content Area
# =============================================================================

# Header with pattern indicator
pattern_badges = {
    "agents_as_tools": "🔧 Agents-as-Tools",
    "swarm": "🐝 Swarm",
    "graph": "📊 Graph"
}
current_pattern = pattern_badges.get(st.session_state.orchestration_pattern, "Unknown")

st.markdown(f"""
<div class="main-header">
    <h1>🛒 Smart Customer Assistant</h1>
    <p>Powered by Multi-Agent AI System | AWS Strands SDK</p>
    <p style="font-size: 0.9em; margin-top: 5px;">Pattern: <strong>{current_pattern}</strong> | Session: <code>{st.session_state.session_id}</code></p>
</div>
""", unsafe_allow_html=True)

# Layout: Chat (main) | Activity (side)
col1, col2 = st.columns([3, 1])

# -----------------------------------------------------------------------------
# Chat Column
# -----------------------------------------------------------------------------
with col1:
    st.subheader("💬 Chat")
    
    # Display chat messages
    chat_container = st.container(height=400)
    
    with chat_container:
        # Welcome message if no history (pattern-aware)
        if not st.session_state.messages:
            if st.session_state.agentic_mode:
                if st.session_state.use_langgraph:
                    st.markdown("""
                    🔷 **Welcome to Smart Customer Assistant (LangGraph Mode)!**
                    
                    I'm running with **LangGraph's native agentic capabilities**:
                    
                    - 📊 **Graph Workflows**: State-based execution
                    - 💭 **ReAct Loops**: Native reasoning cycles
                    - 🎯 **Goal Decomposition**: Automatic task breakdown
                    - 🔄 **Self-Reflection**: Quality improvement
                    - 💾 **Checkpoint Memory**: Persistent conversation state
                    
                    Try complex queries like:
                    - *"Find a gaming laptop under $1500, check if it's in stock, and shipping to 90210"*
                    - *"Compare laptops, check reviews, and recommend the best value"*
                    
                    Watch the LangGraph reasoning trace! →
                    """)
                else:
                    st.markdown("""
                    🧠 **Welcome to Smart Customer Assistant (Agentic Mode)!**
                    
                    I'm running with **custom agentic capabilities**:
                    
                    - 💭 **ReAct**: Think step-by-step before acting
                    - 🎯 **Goal Planning**: Break complex tasks into sub-goals
                    - 🔄 **Self-Reflection**: Critique and improve my responses
                    - 🧠 **Memory**: Remember our conversation context
                    
                    Try complex queries like:
                    - *"Find a gaming laptop, check reviews, see if it's in stock"*
                    - *"Compare the top 3 laptops and recommend the best value"*
                    
                    Watch the reasoning trace in the panel! →
                    """)
            elif st.session_state.orchestration_pattern == "swarm":
                st.markdown("""
                👋 **Welcome to Smart Customer Assistant (Swarm Mode)!**
                
                I use the **Swarm Pattern** - agents can dynamically hand off 
                conversations to each other based on context.
                
                Try asking about:
                - **Orders** → Order Agent may handoff to Logistics
                - **Products** → Product Agent may handoff to Reviews/Pricing
                
                Watch the handoff chain in the activity panel! →
                """)
            elif st.session_state.orchestration_pattern == "graph":
                workflow_names = {"order": "Order Fulfillment", "research": "Product Research", "stock_check": "Stock Check"}
                wf_name = workflow_names.get(st.session_state.graph_workflow, "Unknown")
                st.markdown(f"""
                👋 **Welcome to Smart Customer Assistant (Graph Mode)!**
                
                I use the **Graph Workflow Pattern** - deterministic pipelines 
                with defined execution order.
                
                **Current Workflow:** {wf_name}
                
                Your query will flow through a predefined agent pipeline.
                Watch the workflow steps in the activity panel! →
                """)
            else:
                st.markdown("""
                👋 **Welcome to Smart Customer Assistant!**
                
                I'm powered by a **7-agent system** with the Supervisor routing 
                your queries to specialists:
                
                🛍️ Product | 📦 Order | ❓ Support | 📊 Inventory
                💰 Pricing | ⭐ Reviews | 🚚 Logistics
                
                How can I help you today?
                """)
        
        # Display conversation history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response with streaming
        with st.chat_message("assistant"):
            # Create placeholder for streaming response
            response_placeholder = st.empty()
            
            # Get response based on mode and pattern
            if st.session_state.demo_mode:
                # Demo mode responses
                if st.session_state.orchestration_pattern == "swarm":
                    response, activities, handoffs = get_swarm_demo_response(prompt)
                    st.session_state.handoff_history.extend(handoffs)
                elif st.session_state.orchestration_pattern == "graph":
                    response, activities, workflow_steps = get_graph_demo_response(
                        prompt, st.session_state.graph_workflow
                    )
                else:
                    response, activities = get_demo_response(prompt)
            elif st.session_state.agentic_mode:
                # 🚀 Agentic Supervisor with full capabilities
                response_placeholder.markdown("🧠 _Agentic processing... Decomposing goals..._")
                response, activities, trace = get_agentic_response(prompt, use_langgraph=st.session_state.use_langgraph)
                st.session_state.agentic_trace = trace
            elif st.session_state.orchestration_pattern == "swarm":
                # 🐝 Live Swarm orchestration
                response_placeholder.markdown("🐝 _Swarm agents collaborating..._")
                response, activities, handoffs = get_swarm_response(prompt)
                st.session_state.handoff_history.extend(handoffs)
            elif st.session_state.orchestration_pattern == "graph":
                # 📊 Live Graph workflow
                response_placeholder.markdown("📊 _Graph pipeline executing..._")
                response, activities, workflow_steps = get_graph_response(
                    prompt, st.session_state.graph_workflow
                )
            else:
                # Default Agents-as-Tools with streaming
                # Show initial thinking placeholder
                thinking_placeholder = st.empty()
                thinking_placeholder.markdown("🤖 _Analyzing query and routing to specialists..._", unsafe_allow_html=True)
                
                # Get response (this will populate handoff tracker)
                response, activities = get_real_response(prompt)
                
                # Get handoffs for thinking display
                from agents import get_handoff_tracker
                handoffs = get_handoff_tracker()
                
                # Display thinking container if we have handoffs
                if handoffs:
                    thinking_html = format_thinking_display(handoffs)
                    if thinking_html:
                        thinking_placeholder.markdown(thinking_html, unsafe_allow_html=True)
                        import time
                        time.sleep(1.0)  # Brief pause to show thinking
                
                # Clear thinking and prepare for response
                thinking_placeholder.empty()
                response_placeholder.empty()
            
            # Stream the response character by character for effect
            import time
            streamed_text = ""
            for char in response:
                streamed_text += char
                response_placeholder.markdown(streamed_text + "▌")
                time.sleep(0.005)  # 5ms delay per character
            
            # Final display without cursor
            response_placeholder.markdown(response)
        
        # Add assistant response to state
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Update activity log
        st.session_state.agent_activity = activities + st.session_state.agent_activity
        
        st.rerun()
    
    # Handle sample query from sidebar
    if "sample_query" in st.session_state:
        prompt = st.session_state.sample_query
        del st.session_state.sample_query
        
        # Add user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response with streaming
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            # Get response based on mode and pattern
            if st.session_state.demo_mode:
                if st.session_state.orchestration_pattern == "swarm":
                    response, activities, handoffs = get_swarm_demo_response(prompt)
                    st.session_state.handoff_history.extend(handoffs)
                elif st.session_state.orchestration_pattern == "graph":
                    response, activities, workflow_steps = get_graph_demo_response(
                        prompt, st.session_state.graph_workflow
                    )
                else:
                    response, activities = get_demo_response(prompt)
            elif st.session_state.agentic_mode:
                response_placeholder.markdown("🧠 _Agentic processing..._")
                response, activities, trace = get_agentic_response(prompt, use_langgraph=st.session_state.use_langgraph)
                st.session_state.agentic_trace = trace
            elif st.session_state.orchestration_pattern == "swarm":
                response_placeholder.markdown("🐝 _Swarm collaborating..._")
                response, activities, handoffs = get_swarm_response(prompt)
                st.session_state.handoff_history.extend(handoffs)
            elif st.session_state.orchestration_pattern == "graph":
                response_placeholder.markdown("📊 _Pipeline executing..._")
                response, activities, workflow_steps = get_graph_response(
                    prompt, st.session_state.graph_workflow
                )
            else:
                # Default Agents-as-Tools with streaming
                # Show initial thinking placeholder
                thinking_placeholder = st.empty()
                thinking_placeholder.markdown("🤖 _Analyzing query and routing to specialists..._", unsafe_allow_html=True)
                
                # Get response (this will populate handoff tracker)
                response, activities = get_real_response(prompt)
                
                # Get handoffs for thinking display
                from agents import get_handoff_tracker
                handoffs = get_handoff_tracker()
                
                # Display thinking container if we have handoffs
                if handoffs:
                    thinking_html = format_thinking_display(handoffs)
                    if thinking_html:
                        thinking_placeholder.markdown(thinking_html, unsafe_allow_html=True)
                        import time
                        time.sleep(1.0)  # Brief pause to show thinking
                
                # Clear thinking and prepare for response
                thinking_placeholder.empty()
                response_placeholder.empty()
            
            # Stream response
            import time
            streamed_text = ""
            for char in response:
                streamed_text += char
                response_placeholder.markdown(streamed_text + "▌")
                time.sleep(0.005)
            response_placeholder.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.agent_activity = activities + st.session_state.agent_activity
        
        st.rerun()

# -----------------------------------------------------------------------------
# Activity Column
# -----------------------------------------------------------------------------
with col2:
    # Dynamic title based on mode and pattern
    if st.session_state.agentic_mode:
        if st.session_state.use_langgraph:
            st.subheader("🔷 LangGraph Trace")
        else:
            st.subheader("🧠 Agentic Reasoning")
    elif st.session_state.orchestration_pattern == "swarm":
        st.subheader("🐝 Swarm Activity")
    elif st.session_state.orchestration_pattern == "graph":
        st.subheader("📊 Workflow Steps")
    else:
        st.subheader("📊 Agent Activity")
    
    # Show Agentic Trace when in agentic mode
    if st.session_state.agentic_mode and st.session_state.agentic_trace:
        trace = st.session_state.agentic_trace
        framework = trace.get('framework', 'custom')
        
        # Different styling for LangGraph vs Custom
        if framework == 'langgraph':
            bg_color = "#e3f2fd"
            border_color = "#2196f3"
            framework_label = "🔷 LangGraph"
        else:
            bg_color = "#fff3e0"
            border_color = "#ff9800"
            framework_label = "🧠 Custom"
        
        quality_score = trace.get('quality_score', 0)
        quality_display = f"<strong>⭐ Quality:</strong> {quality_score:.1f}/5<br>" if quality_score else ""
        
        st.markdown(f"""
        <div style="background: {bg_color}; padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 4px solid {border_color};">
            <strong>🏷️ Framework:</strong> {framework_label}<br>
            <strong>🎮 Mode:</strong> {trace.get('mode', 'N/A').upper()}<br>
            <strong>🎯 Goals:</strong> {trace.get('goals', 0)} completed<br>
            <strong>💭 Reasoning:</strong> {trace.get('reasoning_steps', 0)} steps<br>
            <strong>🔄 Reflections:</strong> {trace.get('reflections', 0)}<br>
            {quality_display}<strong>⏱️ Time:</strong> {trace.get('time_ms', 0):.0f}ms
        </div>
        """, unsafe_allow_html=True)
        if trace.get('errors'):
            st.warning(f"⚠️ Errors recovered: {len(trace['errors'])}")
        if trace.get('critiques'):
            with st.expander("📝 Critiques"):
                for i, critique in enumerate(trace.get('critiques', []), 1):
                    st.caption(f"{i}. {critique[:100]}...")
        st.divider()
    
    # Show handoff history for Swarm pattern
    if st.session_state.orchestration_pattern == "swarm" and st.session_state.handoff_history:
        st.caption("**Recent Handoffs:**")
        for handoff in st.session_state.handoff_history[-5:]:  # Last 5 handoffs
            st.markdown(f"""
            <div style="background: #e8f5e9; padding: 5px 10px; border-radius: 5px; margin: 3px 0; font-size: 0.85em; border-left: 3px solid #4caf50;">
                <strong>{handoff['from']}</strong> → <strong>{handoff['to']}</strong><br>
                <small>{handoff['reason']}</small>
            </div>
            """, unsafe_allow_html=True)
        st.divider()
    
    # Show agent activity
    if st.session_state.agent_activity:
        for activity in st.session_state.agent_activity[:10]:  # Show last 10
            with st.container():
                # Different styling for agentic mode
                if st.session_state.agentic_mode:
                    # Use different styling for LangGraph vs Custom
                    if st.session_state.use_langgraph:
                        bg_color = "#e3f2fd"
                        border_color = "#2196f3"
                    else:
                        bg_color = "#fff8e1"
                        border_color = "#ffc107"
                    
                    st.markdown(f"""
                    <div style="background: {bg_color}; padding: 8px 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid {border_color};">
                        <strong>{activity['agent']}</strong><br>
                        <small>{activity['time']}</small><br>
                        {activity['action']}
                    </div>
                    """, unsafe_allow_html=True)
                # Different styling for different patterns
                elif st.session_state.orchestration_pattern == "graph":
                    st.markdown(f"""
                    <div style="background: #e3f2fd; padding: 8px 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #2196f3;">
                        <strong>📍 {activity['agent']}</strong><br>
                        <small>{activity['time']}</small><br>
                        {activity['action']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="agent-card">
                        <strong>{activity['agent']}</strong><br>
                        <small>{activity['time']}</small><br>
                        {activity['action']}
                    </div>
                    """, unsafe_allow_html=True)
    else:
        if st.session_state.orchestration_pattern == "swarm":
            st.info("Handoffs will appear here")
        elif st.session_state.orchestration_pattern == "graph":
            st.info("Workflow steps will appear here")
        else:
            st.info("Agent activity will appear here")
    
    st.divider()
    
    # System status - ALL 7 AGENTS
    st.subheader("🔋 System Status")
    
    # Full agent list with pattern-specific indicators
    all_agents = {
        "Supervisor": "🟢",
        "Product Agent": "🟢",
        "Order Agent": "🟢",
        "Support Agent": "🟢",
        "Inventory Agent": "🟢",
        "Pricing Agent": "🟢",
        "Reviews Agent": "🟢",
        "Logistics Agent": "🟢",
    }
    
    # If swarm or graph, show coordinator/engine instead of supervisor
    if st.session_state.orchestration_pattern == "swarm":
        all_agents = {"Swarm Coordinator": "🟢", **{k: v for k, v in all_agents.items() if k != "Supervisor"}}
    elif st.session_state.orchestration_pattern == "graph":
        all_agents = {"Graph Engine": "🟢", **{k: v for k, v in all_agents.items() if k != "Supervisor"}}
    
    for agent, status in all_agents.items():
        st.text(f"{status} {agent}")
    
    # Pattern-specific stats
    st.divider()
    st.subheader("📈 Stats")
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.metric("Messages", len(st.session_state.messages))
    with col_stat2:
        if st.session_state.orchestration_pattern == "swarm":
            st.metric("Handoffs", len(st.session_state.handoff_history))
        else:
            st.metric("Activities", len(st.session_state.agent_activity))


# =============================================================================
# Footer
# =============================================================================

st.divider()

# Dynamic footer based on pattern
pattern_display = {
    "agents_as_tools": "Agents-as-Tools",
    "swarm": "Swarm Pattern (Dynamic Handoffs)",
    "graph": "Graph Workflow (Pipelines)"
}
current_pattern_name = pattern_display.get(st.session_state.orchestration_pattern, "Unknown")

st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.8em;">
    Smart Customer Assistant MVP | Built with AWS Strands SDK + Streamlit<br>
    <strong>Pattern:</strong> {current_pattern_name} | <strong>Model:</strong> Claude Sonnet 4<br>
    <strong>Features:</strong> Session Management | 7 Specialist Agents | Structured Outputs
</div>
""", unsafe_allow_html=True)
