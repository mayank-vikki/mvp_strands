# 🤖 Multi-Agent AI Customer Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange.svg)
![Strands](https://img.shields.io/badge/Strands-SDK-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red.svg)

**An enterprise-grade Multi-Agent AI System built with AWS Strands SDK, featuring 7 specialist agents, 32 tools, and 4 orchestration patterns for intelligent customer service automation.**

[Features](#-features) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Orchestration Modes](#-orchestration-modes)

</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Orchestration Modes](#-orchestration-modes)
  - [Mode 1: Agents-as-Tools (Default)](#mode-1-agents-as-tools-default)
  - [Mode 2: Swarm Orchestration](#mode-2-swarm-orchestration)
  - [Mode 3: Graph Workflows](#mode-3-graph-workflows)
  - [Mode 4: Agentic Supervisor](#mode-4-agentic-supervisor-full-autonomous)
- [Components Deep Dive](#-components-deep-dive)
- [Data Flow](#-data-flow)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)

---

## 🎯 Project Overview

This project demonstrates a **production-ready Multi-Agent AI System** designed for e-commerce customer service. It showcases advanced concepts in:

- **Multi-Agent Orchestration** - Multiple AI agents collaborating to solve complex queries
- **Tool-Augmented LLMs** - Agents equipped with specialized tools for real-world tasks
- **Agentic AI Patterns** - ReAct reasoning, goal decomposition, self-reflection, and memory
- **AWS Bedrock Integration** - Powered by Amazon Nova Pro foundation model

### Why Multi-Agent Systems?

| Single Agent | Multi-Agent System |
|--------------|-------------------|
| One model handles everything | Specialized experts for each domain |
| Limited context window | Distributed knowledge |
| Generic responses | Domain-specific expertise |
| No collaboration | Agents can consult each other |
| Single point of failure | Fault-tolerant architecture |

---

## ✨ Features

### 🤖 7 Specialist Agents
| Agent | Expertise | Tools |
|-------|-----------|-------|
| 🛍️ **Product Agent** | Search, recommendations, comparisons | 4 tools |
| 📦 **Order Agent** | Order status, tracking, history | 4 tools |
| 🎧 **Support Agent** | FAQ, policies, returns, escalation | 4 tools |
| 📊 **Inventory Agent** | Stock levels, warehouses, availability | 5 tools |
| 💰 **Pricing Agent** | Deals, coupons, price history | 5 tools |
| ⭐ **Reviews Agent** | Ratings, reviews, sentiment analysis | 5 tools |
| 🚚 **Logistics Agent** | Shipping, carriers, delivery slots | 5 tools |

### 🛠️ 32 Specialized Tools
Tools are functions that agents can invoke to perform actions:

```
Product Tools     → search_products, get_recommendations, compare_products, get_product_details
Order Tools       → lookup_order, track_shipment, estimate_delivery, get_order_history
Support Tools     → search_faq, get_policy_info, check_return_eligibility, escalate_to_human
Inventory Tools   → check_stock_availability, get_warehouse_info, check_restock_status, get_inventory_alerts, find_nearest_warehouse
Pricing Tools     → get_active_deals, validate_coupon, get_price_history, get_lightning_deals, calculate_best_price
Reviews Tools     → get_product_reviews, get_rating_summary, search_reviews, get_review_highlights, compare_product_ratings
Logistics Tools   → get_shipping_options, get_detailed_tracking, get_delivery_slots, calculate_shipping_cost, get_carrier_info
```

### 🧠 4 Orchestration Patterns
1. **Agents-as-Tools** - Supervisor routes queries to specialists
2. **Swarm** - Agents self-organize with dynamic handoffs
3. **Graph Workflows** - Deterministic pipelines for complex processes
4. **Agentic Supervisor** - Full autonomous reasoning with ReAct, planning, and reflection

---

## 🏗️ Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              STREAMLIT UI                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Chat UI   │  │   Mode      │  │  Activity   │  │   Trace     │        │
│  │             │  │  Selector   │  │   Panel     │  │   Viewer    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER                                  │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │ Agents-as-    │  │    Swarm      │  │    Graph      │  │   Agentic    │ │
│  │    Tools      │  │ Orchestrator  │  │  Workflows    │  │  Supervisor  │ │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘  └──────┬───────┘ │
└──────────┼──────────────────┼──────────────────┼─────────────────┼──────────┘
           │                  │                  │                 │
           ▼                  ▼                  ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SPECIALIST AGENTS                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Product │ │  Order  │ │ Support │ │Inventory│ │ Pricing │ │ Reviews │   │
│  │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │ │  Agent  │   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   │
│       │          │          │          │          │          │             │
│  ┌─────────┐                                                               │
│  │Logistics│                                                               │
│  │  Agent  │                                                               │
│  └────┬────┘                                                               │
└───────┼─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              TOOLS LAYER                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  32 Specialized Tools: Search, Tracking, Stock Check, Pricing, etc.  │   │
│  └───────────────────────────────────┬──────────────────────────────────┘   │
└──────────────────────────────────────┼──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │products │  │ orders  │  │inventory│  │ reviews │  │  deals  │           │
│  │  .json  │  │  .json  │  │  .json  │  │  .json  │  │  .json  │           │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS BEDROCK                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │              Amazon Nova Pro (amazon.nova-pro-v1:0)                   │   │
│  │                      Foundation Model                                 │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
mvp_project/
│
├── 📄 README.md                    # This file
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env                         # Environment variables (AWS credentials)
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 app/                         # Frontend Application
│   └── streamlit_app.py            # Streamlit UI (1700+ lines)
│
├── 📁 src/                         # Source Code
│   │
│   ├── 📁 agents/                  # 7 Specialist Agents + Supervisor
│   │   ├── __init__.py
│   │   ├── supervisor.py           # Main orchestrator (Agents-as-Tools)
│   │   ├── product_agent.py        # 🛍️ Product search & recommendations
│   │   ├── order_agent.py          # 📦 Order tracking & history
│   │   ├── support_agent.py        # 🎧 FAQ & policy support
│   │   ├── inventory_agent.py      # 📊 Stock & warehouse management
│   │   ├── pricing_agent.py        # 💰 Deals & pricing
│   │   ├── reviews_agent.py        # ⭐ Reviews & ratings
│   │   └── logistics_agent.py      # 🚚 Shipping & delivery
│   │
│   ├── 📁 tools/                   # 32 Specialized Tools
│   │   ├── __init__.py
│   │   ├── product_tools.py        # 4 product tools
│   │   ├── order_tools.py          # 4 order tools
│   │   ├── support_tools.py        # 4 support tools
│   │   ├── inventory_tools.py      # 5 inventory tools
│   │   ├── pricing_tools.py        # 5 pricing tools
│   │   ├── reviews_tools.py        # 5 review tools
│   │   └── logistics_tools.py      # 5 logistics tools
│   │
│   ├── 📁 agentic/                 # Agentic Capabilities Module
│   │   ├── __init__.py
│   │   ├── agentic_supervisor.py   # 🧠 Full autonomous supervisor
│   │   ├── react_agent.py          # ReAct pattern implementation
│   │   ├── goal_planner.py         # Goal decomposition engine
│   │   ├── reflection.py           # Self-reflection & critique
│   │   └── memory.py               # Multi-type memory system
│   │
│   ├── 📁 orchestration/           # Multi-Agent Orchestration Patterns
│   │   ├── __init__.py
│   │   ├── swarm_orchestrator.py   # 🐝 Swarm pattern
│   │   └── graph_workflow.py       # 📊 Graph workflows
│   │
│   ├── 📁 models/                  # ML Models
│   │   └── recommender.py          # PyTorch recommendation model
│   │
│   └── 📁 utils/                   # Utilities
│       ├── __init__.py
│       └── config.py               # Configuration management
│
├── 📁 data/                        # Mock Data (JSON)
│   ├── products.json               # Product catalog
│   ├── orders.json                 # Order database
│   ├── inventory.json              # Stock levels
│   ├── reviews.json                # Customer reviews
│   ├── deals.json                  # Active promotions
│   ├── faq.json                    # FAQ database
│   └── shipping.json               # Shipping options
│
└── 📁 tests/                       # Test Suite
    └── ...
```

---

## 🔧 Installation

### Prerequisites

- Python 3.10+
- AWS Account with Bedrock access
- Amazon Nova Pro model enabled in Bedrock

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/mvp_project.git
cd mvp_project
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure AWS Credentials

Create a `.env` file in the project root:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# Bedrock Model Configuration
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
```

### Step 5: Run the Application

```bash
streamlit run app/streamlit_app.py
```

Open your browser at `http://localhost:8501`

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Key | Required |
| `AWS_DEFAULT_REGION` | AWS Region | `us-east-1` |
| `BEDROCK_MODEL_ID` | Bedrock Model ID | `amazon.nova-pro-v1:0` |

### Supported Models

- `amazon.nova-pro-v1:0` (Recommended)
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`

---

## 🔄 Orchestration Modes

This system supports **4 distinct orchestration patterns**, each with different characteristics:

---

### Mode 1: Agents-as-Tools (Default)

**Pattern**: Centralized routing with supervisor as the single point of control.

```
┌──────────────────────────────────────────────────────────────┐
│                      USER QUERY                               │
│            "What's the status of order ORD-1001?"            │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    🎯 SUPERVISOR AGENT                        │
│                                                               │
│  1. Analyzes query intent                                     │
│  2. Identifies required specialist (Order Agent)              │
│  3. Calls specialist as a "tool"                              │
│  4. Receives specialist response                              │
│  5. Formats and returns final response                        │
│                                                               │
│  Tools Available:                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ask_product_specialist()  │ ask_order_specialist()      │ │
│  │ ask_support_specialist()  │ ask_inventory_specialist()  │ │
│  │ ask_pricing_specialist()  │ ask_reviews_specialist()    │ │
│  │ ask_logistics_specialist()                              │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    📦 ORDER AGENT                             │
│                                                               │
│  Tools: lookup_order, track_shipment, estimate_delivery      │
│                                                               │
│  1. Receives delegated query                                  │
│  2. Uses lookup_order("ORD-1001")                            │
│  3. Retrieves order data from orders.json                    │
│  4. Returns structured response to Supervisor                 │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                      FINAL RESPONSE                           │
│  "Order ORD-1001 is currently 'shipped' and expected to      │
│   arrive on December 18, 2024. Tracking: TRK-876543"         │
└──────────────────────────────────────────────────────────────┘
```

**Characteristics:**
- ✅ Predictable routing
- ✅ Easy to debug
- ✅ Low latency for simple queries
- ❌ Limited cross-domain collaboration

**When to Use:**
- Simple, single-domain queries
- When you need predictable routing
- Production environments requiring stability

**Code Flow:**
```python
# src/agents/supervisor.py

@tool
def ask_order_specialist(query: str) -> str:
    """Route order-related queries to the Order Agent."""
    _log_handoff("Supervisor", "Order Agent", query)
    order_agent = _get_order_agent()
    response = order_agent(query)
    _log_response("Order Agent", response)
    return str(response)

def get_customer_assistant():
    """Create the main supervisor with all specialists as tools."""
    return Agent(
        name="customer_assistant",
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
        ]
    )
```

---

### Mode 2: Swarm Orchestration

**Pattern**: Decentralized, self-organizing agents with dynamic handoffs.

```
┌──────────────────────────────────────────────────────────────┐
│                      USER QUERY                               │
│  "I need a laptop, check if it's in stock, and what's the   │
│   return policy?"                                            │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    🐝 SWARM COORDINATOR                       │
│        Initializes swarm with all specialist agents          │
└───────────────────────────┬──────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  🛍️ Product │     │ 📊 Inventory │     │ 🎧 Support  │
│   Agent     │     │    Agent    │     │   Agent    │
│             │     │             │     │            │
│ "I'll find  │     │ "Waiting    │     │ "Waiting   │
│  laptops"   │     │  for product│     │  for my    │
│             │     │  info"      │     │  turn"     │
└──────┬──────┘     └─────────────┘     └────────────┘
       │
       │  🔄 DYNAMIC HANDOFF
       │  "Found laptops, now checking stock..."
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                    📊 INVENTORY AGENT                        │
│                                                              │
│  Receives: Product IDs from Product Agent                    │
│  Action: check_stock_availability("PROD-001")               │
│  Result: "Gaming Pro X1 - 45 units in stock"                │
│                                                              │
│  🔄 HANDOFF: "Stock checked, user also asked about policy"  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    🎧 SUPPORT AGENT                          │
│                                                              │
│  Receives: Context from previous agents                      │
│  Action: get_policy_info("return")                          │
│  Result: "30-day return policy details..."                   │
│                                                              │
│  ✅ COMPLETE: All parts of query addressed                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FINAL RESPONSE                          │
│  Aggregated response from all three agents with:            │
│  - Laptop recommendations                                    │
│  - Stock availability                                        │
│  - Return policy details                                     │
└─────────────────────────────────────────────────────────────┘
```

**Handoff Mechanism:**
```
AGENT A                           AGENT B
   │                                 │
   │   handoff_to_agent(            │
   │     agent_name="inventory",    │
   │     message="Check stock for   │
   │              PROD-001"         │
   │   )                            │
   │ ─────────────────────────────► │
   │                                 │
   │                           (Executes task)
   │                                 │
   │ ◄───────────────────────────── │
   │        Result + Context        │
```

**Characteristics:**
- ✅ Handles complex, multi-domain queries
- ✅ Emergent collaboration
- ✅ Flexible and adaptive
- ❌ Less predictable execution path

**When to Use:**
- Complex, multi-domain queries
- When query scope is unpredictable
- Research and exploration tasks

**Code Flow:**
```python
# src/orchestration/swarm_orchestrator.py

def create_customer_swarm():
    """Create a swarm of collaborative agents."""
    agents = [
        _create_swarm_product_agent(),
        _create_swarm_order_agent(),
        _create_swarm_support_agent(),
        _create_swarm_inventory_agent(),
        _create_swarm_pricing_agent(),
        _create_swarm_reviews_agent(),
        _create_swarm_logistics_agent()
    ]
    
    return Swarm(
        agents=agents,
        initial_agent="product_specialist"  # Entry point
    )
```

---

### Mode 3: Graph Workflows

**Pattern**: Deterministic pipelines with predefined execution order.

```
┌──────────────────────────────────────────────────────────────┐
│                      USER QUERY                               │
│            "Process order ORD-1001 for shipping"             │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              📊 ORDER FULFILLMENT WORKFLOW                    │
│                                                               │
│   Predefined Pipeline: Order → Inventory → Logistics → Done  │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────┐
│                           │                                   │
│    ┌──────────────────────┴───────────────────────────┐      │
│    │                                                   │      │
│    ▼                                                   │      │
│  ┌─────────────────────┐                              │      │
│  │  STEP 1: ORDER      │                              │      │
│  │  ──────────────     │                              │      │
│  │  📦 Order Agent     │                              │      │
│  │                     │                              │      │
│  │  Input: Query       │                              │      │
│  │  Action: lookup_order("ORD-1001")                 │      │
│  │  Output:            │                              │      │
│  │   - Order ID        │                              │      │
│  │   - Product IDs     │                              │      │
│  │   - Ship Address    │                              │      │
│  └──────────┬──────────┘                              │      │
│             │                                          │      │
│             │  (Pass context to next node)            │      │
│             ▼                                          │      │
│  ┌─────────────────────┐                              │      │
│  │  STEP 2: INVENTORY  │                              │      │
│  │  ──────────────     │                              │      │
│  │  📊 Inventory Agent │                              │      │
│  │                     │                              │      │
│  │  Input: Product IDs │                              │      │
│  │  Action: check_stock_availability()               │      │
│  │  Output:            │                              │      │
│  │   - Stock status    │                              │      │
│  │   - Warehouse ID    │                              │      │
│  └──────────┬──────────┘                              │      │
│             │                                          │      │
│             │  (Pass context to next node)            │      │
│             ▼                                          │      │
│  ┌─────────────────────┐                              │      │
│  │  STEP 3: LOGISTICS  │                              │      │
│  │  ──────────────     │                              │      │
│  │  🚚 Logistics Agent │                              │      │
│  │                     │                              │      │
│  │  Input: Address +   │                              │      │
│  │         Warehouse   │                              │      │
│  │  Action:            │                              │      │
│  │   - get_shipping_options()                        │      │
│  │   - calculate_shipping_cost()                     │      │
│  │  Output:            │                              │      │
│  │   - Shipping plan   │                              │      │
│  │   - Carrier info    │                              │      │
│  │   - ETA             │                              │      │
│  └──────────┬──────────┘                              │      │
│             │                                          │      │
│             │  (Pass to confirmation)                 │      │
│             ▼                                          │      │
│  ┌─────────────────────┐                              │      │
│  │  STEP 4: CONFIRM    │                              │      │
│  │  ──────────────     │                              │      │
│  │  ✅ Confirmation    │                              │      │
│  │                     │                              │      │
│  │  Synthesize all     │                              │      │
│  │  previous outputs   │                              │      │
│  │  into final         │                              │      │
│  │  customer response  │                              │      │
│  └──────────┬──────────┘                              │      │
│             │                                          │      │
└─────────────┼──────────────────────────────────────────┘      │
              │                                                  │
              ▼                                                  │
┌──────────────────────────────────────────────────────────────┐
│                      FINAL RESPONSE                          │
│  "Order ORD-1001 processed:                                  │
│   - Items: Gaming Pro X1 (verified in stock at WH-WEST)     │
│   - Shipping: FedEx Express, $12.99                         │
│   - Estimated Delivery: December 18, 2024                   │
│   - Tracking will be sent to customer@email.com"            │
└──────────────────────────────────────────────────────────────┘
```

**Available Workflows:**

| Workflow | Pipeline | Use Case |
|----------|----------|----------|
| **Order Fulfillment** | Order → Inventory → Logistics → Confirm | Process shipments |
| **Product Research** | Product → Reviews → Pricing → Recommend | Shopping assistance |
| **Stock Check** | Inventory → Logistics → Confirm | Availability queries |

**Characteristics:**
- ✅ Predictable execution order
- ✅ Great for compliance workflows
- ✅ Easy to audit and debug
- ❌ Less flexible than Swarm

**When to Use:**
- Structured business processes
- Compliance-requiring workflows
- When execution order matters

**Code Flow:**
```python
# src/orchestration/graph_workflow.py

def create_order_workflow():
    """Create order fulfillment workflow graph."""
    builder = GraphBuilder()
    
    # Define nodes (agents)
    builder.add_node("order", _create_order_node_agent())
    builder.add_node("inventory", _create_inventory_node_agent())
    builder.add_node("logistics", _create_logistics_node_agent())
    builder.add_node("confirmation", _create_confirmation_node_agent())
    
    # Define edges (execution order)
    builder.add_edge("order", "inventory")
    builder.add_edge("inventory", "logistics")
    builder.add_edge("logistics", "confirmation")
    
    # Set entry point
    builder.set_entry_point("order")
    
    return builder.build()
```

---

### Mode 4: Agentic Supervisor (Full Autonomous)

**Pattern**: Complete autonomous reasoning with ReAct, goal decomposition, self-reflection, and memory.

This is the most advanced mode, integrating all agentic capabilities:

```
┌──────────────────────────────────────────────────────────────┐
│                      USER QUERY                               │
│  "Help me buy a laptop: find options, check reviews, verify │
│   stock, compare prices, and suggest the best one"          │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              🧠 AGENTIC SUPERVISOR                            │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  PHASE 1: MEMORY ASSEMBLY                              │  │
│  │  ────────────────────────────────────────────────────  │  │
│  │  • Check short-term memory for recent context          │  │
│  │  • Query long-term memory for user preferences         │  │
│  │  • Load episodic memory for similar past queries       │  │
│  │  • Assemble working memory for current task            │  │
│  └────────────────────────────────────────────────────────┘  │
│                            │                                  │
│                            ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  PHASE 2: GOAL DECOMPOSITION                           │  │
│  │  ────────────────────────────────────────────────────  │  │
│  │                                                         │  │
│  │  Complex Query Decomposed Into:                         │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ Goal 1: Find laptop options [INDEPENDENT]       │   │  │
│  │  │   → Agent: Product Agent                        │   │  │
│  │  │   → Priority: HIGH                              │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  │            │                                            │  │
│  │            ▼ (Dependency)                               │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ Goal 2: Check reviews [DEPENDS: Goal 1]         │   │  │
│  │  │   → Agent: Reviews Agent                        │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ Goal 3: Verify stock [DEPENDS: Goal 1]          │   │  │
│  │  │   → Agent: Inventory Agent                      │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ Goal 4: Compare prices [DEPENDS: Goal 1]        │   │  │
│  │  │   → Agent: Pricing Agent                        │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  │            │                                            │  │
│  │            ▼ (All dependencies)                         │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │ Goal 5: Generate recommendation                 │   │  │
│  │  │   [DEPENDS: Goals 2, 3, 4]                      │   │  │
│  │  └─────────────────────────────────────────────────┘   │  │
│  │                                                         │  │
│  └────────────────────────────────────────────────────────┘  │
│                            │                                  │
│                            ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  PHASE 3: ReAct EXECUTION LOOP                         │  │
│  │  ────────────────────────────────────────────────────  │  │
│  │                                                         │  │
│  │  For each goal in execution_order:                      │  │
│  │                                                         │  │
│  │    THOUGHT → ACTION → OBSERVATION → THOUGHT → ...      │  │
│  │                                                         │  │
│  │    ┌─────────────────────────────────────────────┐     │  │
│  │    │  THOUGHT: "I need to find laptop options     │     │  │
│  │    │           first. Let me search for laptops." │     │  │
│  │    └──────────────────┬──────────────────────────┘     │  │
│  │                       ▼                                 │  │
│  │    ┌─────────────────────────────────────────────┐     │  │
│  │    │  ACTION: search_products("gaming laptop")    │     │  │
│  │    └──────────────────┬──────────────────────────┘     │  │
│  │                       ▼                                 │  │
│  │    ┌─────────────────────────────────────────────┐     │  │
│  │    │  OBSERVATION: "Found 3 laptops..."           │     │  │
│  │    └──────────────────┬──────────────────────────┘     │  │
│  │                       ▼                                 │  │
│  │    ┌─────────────────────────────────────────────┐     │  │
│  │    │  THOUGHT: "Good, now check reviews..."       │     │  │
│  │    └─────────────────────────────────────────────┘     │  │
│  │                                                         │  │
│  └────────────────────────────────────────────────────────┘  │
│                            │                                  │
│                            ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  PHASE 4: SELF-REFLECTION                              │  │
│  │  ────────────────────────────────────────────────────  │  │
│  │                                                         │  │
│  │  Critiques:                                             │  │
│  │  • Completeness: 4/5 - "Missing warranty info"         │  │
│  │  • Helpfulness: 5/5 - "Clear recommendation"           │  │
│  │                                                         │  │
│  │  Refinement: Added warranty comparison section          │  │
│  │                                                         │  │
│  │  Overall Quality: 4.5/5 → Threshold met                │  │
│  │                                                         │  │
│  └────────────────────────────────────────────────────────┘  │
│                            │                                  │
│                            ▼                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  PHASE 5: MEMORY UPDATE                                │  │
│  │  ────────────────────────────────────────────────────  │  │
│  │  • Store interaction in short-term memory              │  │
│  │  • Update user preference (interested in laptops)      │  │
│  │  • Create episodic summary for future reference        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    FINAL RESPONSE                             │
│                                                               │
│  "Based on my analysis, here's my recommendation:            │
│                                                               │
│   🏆 Best Overall: Gaming Pro X1 ($1,299)                    │
│      ⭐ Reviews: 4.5/5 (89 reviews)                          │
│      📊 Stock: 45 units available                            │
│      💰 Price: Currently $100 off                            │
│                                                               │
│   Why this choice:                                            │
│   • Best review scores for gaming                             │
│   • In stock and ships immediately                            │
│   • Best value with current discount"                        │
└──────────────────────────────────────────────────────────────┘
```

**Agentic Components:**

| Component | Purpose | File |
|-----------|---------|------|
| **ReAct Agent** | Explicit reasoning before actions | `agentic/react_agent.py` |
| **Goal Planner** | Decompose complex queries | `agentic/goal_planner.py` |
| **Self-Reflector** | Critique and improve responses | `agentic/reflection.py` |
| **Memory System** | Maintain context across turns | `agentic/memory.py` |
| **Agentic Supervisor** | Orchestrate all components | `agentic/agentic_supervisor.py` |

**Characteristics:**
- ✅ Handles most complex queries
- ✅ Transparent reasoning (explainable AI)
- ✅ Self-improving responses
- ✅ Context-aware across sessions
- ❌ Higher latency
- ❌ Higher token usage

**When to Use:**
- Complex, multi-step tasks
- When quality matters more than speed
- Research and analysis queries
- When you need explainable AI decisions

---

## 🔍 Components Deep Dive

### How Agents Are Created

Each specialist agent follows this pattern:

```python
from strands import Agent
from strands.models import BedrockModel

def create_product_agent(callback_handler=None) -> Agent:
    """Create the Product Specialist Agent."""
    
    # Configure the LLM
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,  # Higher for creative recommendations
        max_tokens=2048
    )
    
    # Create the agent with specialized prompt and tools
    return Agent(
        name="product_agent",
        system_prompt=PRODUCT_AGENT_PROMPT,  # Domain expertise
        model=model,
        tools=[
            search_products,      # Tool function
            get_recommendations,  # Tool function
            compare_products,     # Tool function
            get_product_details   # Tool function
        ],
        callback_handler=callback_handler
    )
```

### How Tools Are Defined

Tools are Python functions decorated with `@tool`:

```python
from strands import tool

@tool
def search_products(
    query: str, 
    category: str = None, 
    max_results: int = 5
) -> str:
    """
    Search for products matching the query.
    
    Args:
        query: Search terms (e.g., "gaming laptop")
        category: Optional category filter
        max_results: Maximum number of results
    
    Returns:
        JSON string with matching products
    """
    products = _load_products()
    results = []
    
    for product in products:
        if query.lower() in product["name"].lower():
            results.append(product)
            if len(results) >= max_results:
                break
    
    return json.dumps(results, indent=2)
```

### Memory System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY SYSTEM                             │
├─────────────────────────────────────────────────────────────┤
│  SHORT-TERM MEMORY (Recent conversation - last 10 turns)    │
├─────────────────────────────────────────────────────────────┤
│  WORKING MEMORY (Current task state and intermediate data)  │
├─────────────────────────────────────────────────────────────┤
│  EPISODIC MEMORY (Past interaction summaries)               │
├─────────────────────────────────────────────────────────────┤
│  LONG-TERM MEMORY (Persistent knowledge via vector store)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

```
User Input
    │
    ▼
┌─────────────────┐
│  Streamlit UI   │
│  (Chat Input)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     
│  Mode Selection │──► Demo Mode? ──► Mock Responses
└────────┬────────┘     
         │ NO
         ▼
┌─────────────────────────────────────────┐
│           Orchestration Layer            │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌──────────┐  │
│  │A-a-T│ │Swarm│ │Graph│ │ Agentic  │  │
│  └──┬──┘ └──┬──┘ └──┬──┘ └────┬─────┘  │
└─────┼───────┼───────┼─────────┼────────┘
      └───────┴───────┴─────────┘
              │
              ▼
      ┌───────────────────────┐
      │   Specialist Agents   │
      │  (7 Domain Experts)   │
      └───────────┬───────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │    Tools Layer        │
      │   (32 Functions)      │
      └───────────┬───────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │    Data Layer         │
      │   (JSON Files)        │
      └───────────┬───────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │    AWS Bedrock        │
      │   (Nova Pro LLM)      │
      └───────────────────────┘
```

---

## 🚀 Usage

### Running the Application

```bash
streamlit run app/streamlit_app.py
```

### Switching Modes

1. **Toggle Demo Mode** - OFF for live AWS Bedrock calls
2. **Select Orchestration Pattern** - Agents-as-Tools, Swarm, or Graph
3. **Enable Agentic Mode** - Toggle for full autonomous reasoning

### Sample Queries by Mode

| Mode | Example Query |
|------|---------------|
| **Default** | "What's the status of order ORD-1001?" |
| **Swarm** | "I want a laptop under $1000, check stock, and shipping to 90210" |
| **Graph** | "Process order ORD-1001 for shipping" |
| **Agentic** | "Compare laptops, analyze reviews, check availability, recommend best value" |

---

## 📚 API Reference

### Creating Agents

```python
from agents import get_customer_assistant

assistant = get_customer_assistant()
response = assistant("Your query here")
```

### Using Swarm

```python
from orchestration import create_customer_swarm

swarm = create_customer_swarm()
result = swarm("Multi-domain query")
```

### Using Graph Workflows

```python
from orchestration import create_order_workflow

workflow = create_order_workflow()
result = workflow("Order processing query")
```

### Using Agentic Supervisor

```python
from agentic import AgenticSupervisor

supervisor = AgenticSupervisor(
    enable_react=True,
    enable_goals=True,
    enable_reflection=True,
    enable_memory=True
)
result = supervisor.process("Complex query")
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **AWS Strands SDK** - Multi-agent framework
- **Amazon Bedrock** - Foundation model hosting
- **Streamlit** - Frontend framework
- **ReAct Paper** - Reasoning paradigm
- **MemGPT** - Memory-augmented agents

---

<div align="center">

**Built with ❤️ for demonstrating Multi-Agent AI expertise**

*Showcasing: AWS Bedrock • Strands SDK • Agentic Patterns • Multi-Agent Orchestration*

</div>
