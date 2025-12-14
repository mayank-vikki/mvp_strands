# 🏗️ Multi-Agent AI System Development Template

**A Complete Skeleton Guide for Building Production-Ready Multi-Agent AI Systems**

This document provides a chronological, step-by-step template for developing enterprise-grade multi-agent AI systems. Use this as your blueprint for creating intelligent agent systems for any domain or use case.

---

## 📋 Table of Contents

1. [Phase 1: Planning & Design](#phase-1-planning--design)
2. [Phase 2: Project Setup](#phase-2-project-setup)
3. [Phase 3: Data Layer](#phase-3-data-layer)
4. [Phase 4: Tools Development](#phase-4-tools-development)
5. [Phase 5: Agent Creation](#phase-5-agent-creation)
6. [Phase 6: Orchestration Patterns](#phase-6-orchestration-patterns)
7. [Phase 7: Agentic Capabilities](#phase-7-agentic-capabilities)
8. [Phase 8: Frontend Development](#phase-8-frontend-development)
9. [Phase 9: Testing & Validation](#phase-9-testing--validation)
10. [Phase 10: Deployment & Production](#phase-10-deployment--production)
11. [Real-World Examples](#real-world-examples)

---

## Phase 1: Planning & Design

### 1.1 Problem Analysis

**Questions to Answer:**
- What is the core problem you're solving?
- What are the main user personas and their needs?
- What are the key workflows/processes?
- What are the success metrics?

**Example (E-commerce Customer Service):**
```
Problem: Handle diverse customer queries across multiple domains
Personas: Shoppers, Order Managers, Support Seekers
Workflows: Product Discovery → Order Tracking → Support Resolution
Metrics: Response Accuracy, Resolution Time, Customer Satisfaction
```

### 1.2 Domain Decomposition

**Break down the problem into specialized domains:**

1. **List all possible query types**
2. **Group related queries into domains**
3. **Identify domain experts needed**
4. **Map domains to specialist agents**

**Template:**
```
Domain 1: [Domain Name]
  - Responsibilities: [What this domain handles]
  - Key Queries: [Example queries]
  - Required Tools: [What tools are needed]
  - Agent Name: [Specialist Agent Name]

Domain 2: [Domain Name]
  ...
```

**Example Output:**
```
Domain 1: Product Discovery
  - Responsibilities: Search, recommendations, comparisons, specifications
  - Key Queries: "Find laptops under $1500", "Compare gaming laptops"
  - Required Tools: search_products, get_recommendations, compare_products
  - Agent Name: Product Specialist

Domain 2: Order Management
  - Responsibilities: Order status, tracking, history, modifications
  - Key Queries: "Where is my order?", "Track ORD-1001"
  - Required Tools: lookup_order, track_shipment, estimate_delivery
  - Agent Name: Order Specialist
```

### 1.3 Architecture Decision

**Choose your orchestration pattern(s):**

| Pattern | Use Case | Complexity | When to Use |
|---------|----------|------------|-------------|
| **Agents-as-Tools** | Simple routing | Low | Single-domain queries, predictable routing |
| **Swarm** | Dynamic collaboration | Medium | Multi-domain queries, emergent workflows |
| **Graph Workflows** | Structured processes | Medium | Compliance, deterministic pipelines |
| **Agentic Supervisor** | Complex reasoning | High | Research, analysis, multi-step planning |

**Decision Matrix:**
```
IF query_type == "simple" AND single_domain:
    USE Agents-as-Tools
    
IF query_type == "complex" AND multi_domain:
    USE Swarm OR Agentic Supervisor
    
IF query_type == "structured_process":
    USE Graph Workflows
    
IF query_type == "research" OR "analysis":
    USE Agentic Supervisor
```

### 1.4 Tool Inventory

**For each domain, list required tools:**

**Template:**
```
Domain: [Domain Name]
Tools:
  1. tool_name_1
     - Purpose: [What it does]
     - Inputs: [Parameters]
     - Outputs: [Return format]
     - Data Source: [Where data comes from]
  
  2. tool_name_2
     ...
```

**Example:**
```
Domain: Product Discovery
Tools:
  1. search_products
     - Purpose: Find products matching search query
     - Inputs: query (str), category (optional), max_price (optional)
     - Outputs: JSON list of products with details
     - Data Source: products.json database
  
  2. get_recommendations
     - Purpose: AI-powered product recommendations
     - Inputs: query (str), num_recommendations (int)
     - Outputs: Ranked list with confidence scores
     - Data Source: ML model + products.json
```

---

## Phase 2: Project Setup

### 2.1 Project Structure

**Create the following directory structure:**

```
project_name/
│
├── 📄 README.md                    # Project documentation
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env                         # Environment variables (gitignored)
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 app/                         # Frontend Application
│   └── streamlit_app.py            # Main UI (or FastAPI, Flask, etc.)
│
├── 📁 src/                         # Source Code
│   │
│   ├── 📁 agents/                  # Specialist Agents
│   │   ├── __init__.py
│   │   ├── supervisor.py           # Main orchestrator
│   │   ├── [domain1]_agent.py      # Domain specialist 1
│   │   ├── [domain2]_agent.py      # Domain specialist 2
│   │   └── ...                     # More specialists
│   │
│   ├── 📁 tools/                   # Agent Tools
│   │   ├── __init__.py
│   │   ├── [domain1]_tools.py      # Tools for domain 1
│   │   ├── [domain2]_tools.py      # Tools for domain 2
│   │   └── ...                     # More tool modules
│   │
│   ├── 📁 orchestration/           # Multi-Agent Patterns
│   │   ├── __init__.py
│   │   ├── swarm_orchestrator.py   # Swarm pattern
│   │   └── graph_workflow.py       # Graph workflows
│   │
│   ├── 📁 agentic/                 # Agentic Capabilities (Optional)
│   │   ├── __init__.py
│   │   ├── react_agent.py          # ReAct reasoning
│   │   ├── goal_planner.py         # Goal decomposition
│   │   ├── reflection.py           # Self-reflection
│   │   └── memory.py               # Memory system
│   │
│   ├── 📁 models/                  # ML Models (Optional)
│   │   └── [model_name].py         # Custom models
│   │
│   ├── 📁 utils/                   # Utilities
│   │   ├── __init__.py
│   │   └── config.py              # Configuration
│   │
│   └── 📁 session/                 # Session Management (Optional)
│       ├── __init__.py
│       └── session_manager.py
│
├── 📁 data/                        # Data Files
│   ├── [domain1].json              # Domain 1 data
│   ├── [domain2].json              # Domain 2 data
│   └── ...                         # More data files
│
└── 📁 tests/                       # Test Suite
    ├── __init__.py
    ├── test_tools.py
    ├── test_agents.py
    └── test_orchestration.py
```

### 2.2 Dependencies Setup

**Create `requirements.txt`:**

```python
# Core Multi-Agent Framework
strands-agents>=1.19.0
strands-agents-tools>=0.1.0

# LLM Integration
boto3>=1.35.0                    # AWS Bedrock
# OR
openai>=1.0.0                    # OpenAI API
# OR
anthropic>=0.18.0                # Anthropic API

# Frontend
streamlit>=1.29.0                # Streamlit UI
# OR
fastapi>=0.104.0                 # FastAPI backend
# OR
flask>=3.0.0                     # Flask backend

# Utilities
python-dotenv>=1.0.0             # Environment variables
pydantic>=2.0.0                  # Data validation

# ML/AI (if needed)
torch>=2.0.0                     # PyTorch
numpy>=1.24.0                    # Numerical computing

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
```

### 2.3 Configuration Setup

**Create `src/utils/config.py`:**

```python
"""
Configuration management for the multi-agent system.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "bedrock")  # bedrock, openai, anthropic
    LLM_MODEL_ID: str = os.getenv("LLM_MODEL_ID", "amazon.nova-pro-v1:0")
    
    # AWS Configuration (if using Bedrock)
    AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # OpenAI Configuration (if using OpenAI)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Application Settings
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    MAX_AGENT_ITERATIONS: int = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))
    
    # Paths
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(PROJECT_ROOT, "data")
    
    @classmethod
    def get_model_kwargs(cls) -> dict:
        """Get model initialization parameters."""
        return {
            "model_id": cls.LLM_MODEL_ID,
            "temperature": 0.7,
            "max_tokens": 2048,
        }

config = Config()
```

**Create `.env` template:**

```env
# LLM Provider (bedrock, openai, anthropic)
LLM_PROVIDER=bedrock

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0

# OR OpenAI Configuration
# OPENAI_API_KEY=sk-...

# Application Settings
DEBUG_MODE=false
MAX_AGENT_ITERATIONS=10
```

---

## Phase 3: Data Layer

### 3.1 Data Schema Design

**For each domain, design JSON schema:**

**Template:**
```json
{
  "[domain_plural]": [
    {
      "id": "unique_id",
      "field1": "value1",
      "field2": "value2",
      "metadata": {
        "created_at": "timestamp",
        "updated_at": "timestamp"
      }
    }
  ]
}
```

**Example - Products:**
```json
{
  "products": [
    {
      "id": "P001",
      "name": "Product Name",
      "category": "Category",
      "price": 99.99,
      "description": "Product description",
      "features": ["feature1", "feature2"],
      "stock": 100,
      "rating": 4.5,
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

### 3.2 Data Generation

**Options:**
1. **Mock Data** (for development/testing)
2. **Real Database** (PostgreSQL, MongoDB, etc.)
3. **API Integration** (REST, GraphQL)
4. **File-based** (JSON, CSV, Parquet)

**For MVP, use JSON files:**
- Create sample data files in `data/` directory
- Ensure realistic data structure
- Include edge cases (empty results, missing fields, etc.)

---

## Phase 4: Tools Development

### 4.1 Tool Creation Pattern

**Standard tool template:**

```python
"""
[Domain] Tools - Agent Tool Functions
"""
import json
import os
from typing import Optional, List, Dict
from strands import tool

def _load_[domain]_data() -> List[Dict]:
    """Helper to load domain data."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    data_path = os.path.join(project_root, 'data', '[domain].json')
    
    with open(data_path, 'r') as f:
        data = json.load(f)
    return data.get('[domain_plural]', [])

@tool
def [tool_name](
    param1: str,
    param2: Optional[str] = None,
    param3: Optional[int] = None
) -> str:
    """
    [Clear description of what this tool does]
    
    Use this tool when [when to use it]
    
    Args:
        param1: Description of param1
        param2: Description of param2 (optional)
        param3: Description of param3 (optional)
        
    Returns:
        JSON string with results
        
    Example:
        >>> [tool_name]("example", param2="value")
        Returns [what it returns]
    """
    try:
        # Load data
        data = _load_[domain]_data()
        
        # Process query
        results = []
        for item in data:
            # Filtering/matching logic
            if [condition]:
                results.append(item)
        
        # Format response
        return json.dumps({
            "status": "success",
            "result_count": len(results),
            "results": results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error: {str(e)}"
        })
```

### 4.2 Tool Categories

**Organize tools by function:**

1. **Search/Query Tools**: Find, search, filter
2. **Retrieval Tools**: Get specific items by ID
3. **Analysis Tools**: Compare, analyze, summarize
4. **Action Tools**: Create, update, delete (if applicable)
5. **Validation Tools**: Check, verify, validate

### 4.3 Tool Best Practices

✅ **DO:**
- Use descriptive function names
- Include comprehensive docstrings
- Return structured JSON
- Handle errors gracefully
- Validate inputs

❌ **DON'T:**
- Return raw Python objects (always JSON string)
- Make tools too complex (decompose if needed)
- Hardcode business logic (make it configurable)
- Ignore edge cases

---

## Phase 5: Agent Creation

### 5.1 Specialist Agent Template

**Standard agent template:**

```python
"""
[Domain] Agent - Specialist for [Domain Responsibilities]
"""
from strands import Agent
from strands.models import BedrockModel  # or OpenAI, Anthropic

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.[domain]_tools import (
    tool1,
    tool2,
    tool3
)
from utils.config import config

# Agent System Prompt
[DOMAIN]_AGENT_PROMPT = """
You are a [Domain] Specialist AI assistant. Your role is to [primary responsibility].

## Your Capabilities:
1. **[Capability 1]**: [Description]
2. **[Capability 2]**: [Description]
3. **[Capability 3]**: [Description]

## Guidelines:
- [Guideline 1]
- [Guideline 2]
- [Guideline 3]

## Response Style:
- [Style guideline 1]
- [Style guideline 2]

## Tool Usage:
- Use `tool1` for [when to use]
- Use `tool2` for [when to use]
- Use `tool3` for [when to use]
"""

def create_[domain]_agent(callback_handler=None) -> Agent:
    """
    Create and configure the [Domain] Agent.
    
    Args:
        callback_handler: Optional callback for streaming responses
        
    Returns:
        Configured Agent instance
    """
    # Configure LLM model
    model = BedrockModel(  # or OpenAIModel, AnthropicModel
        model_id=config.LLM_MODEL_ID,
        temperature=0.7,  # Adjust based on domain (0.5-0.9)
        max_tokens=2048,
    )
    
    # Create agent with domain-specific tools
    agent = Agent(
        name="[domain]_agent",
        system_prompt=[DOMAIN]_AGENT_PROMPT,
        model=model,
        tools=[
            tool1,
            tool2,
            tool3
        ],
        callback_handler=callback_handler
    )
    
    return agent
```

### 5.2 Supervisor Agent

**Create the main orchestrator:**

```python
"""
Supervisor Agent - Multi-Agent Orchestrator
"""
from strands import Agent, tool
from strands.models import BedrockModel
from utils.config import config

# Lazy-load specialist agents
_specialist_agents = {}

def _get_[domain]_agent():
    """Lazy load [Domain] Agent."""
    if "[domain]" not in _specialist_agents:
        from agents.[domain]_agent import create_[domain]_agent
        _specialist_agents["[domain]"] = create_[domain]_agent()
    return _specialist_agents["[domain]"]

# Handoff tracker for UI
_handoff_tracker = []

def get_handoff_tracker():
    return _handoff_tracker

def clear_handoff_tracker():
    global _handoff_tracker
    _handoff_tracker = []

def _log_handoff(from_agent: str, to_agent: str, query: str):
    """Log handoffs for UI display."""
    from datetime import datetime
    _handoff_tracker.append({
        "type": "handoff",
        "from": from_agent,
        "to": to_agent,
        "query": query[:100],
        "time": datetime.now().strftime("%H:%M:%S")
    })

def _log_response(agent: str, response: str):
    """Log agent responses for UI display."""
    from datetime import datetime
    _handoff_tracker.append({
        "type": "response",
        "agent": agent,
        "response": response[:200],
        "time": datetime.now().strftime("%H:%M:%S")
    })

@tool
def ask_[domain]_specialist(query: str) -> str:
    """
    Delegate [domain]-related queries to the [Domain] Specialist.
    
    Use for: [List use cases]
    
    Args:
        query: The customer's [domain]-related question
        
    Returns:
        [Domain] specialist's response
    """
    _log_handoff("Supervisor", "[Domain] Specialist", query)
    agent = _get_[domain]_agent()
    response = agent(query)
    _log_response("[Domain] Specialist", str(response))
    return str(response)

# Repeat for each domain specialist...

SUPERVISOR_PROMPT = """
You are the [System Name] Supervisor - an intelligent AI orchestrator.

You have access to [N] specialist agents, each expert in their domain.
Your job is to analyze queries and call the APPROPRIATE specialists.

## Available Specialists:

### 1. [Domain] Specialist (`ask_[domain]_specialist`)
Expert in: [Expertise]
Use when: [When to use]
Keywords: [Keywords]

### 2. [Domain] Specialist (`ask_[domain]_specialist`)
...

## CRITICAL ROUTING RULES:

### Rule 1: ALWAYS call MULTIPLE specialists for multi-part queries
When a query contains multiple distinct needs, you MUST call ALL relevant specialists.

### Rule 2: Identify ALL parts of the query
Break down the query into its components and match each to a specialist.

### Rule 3: Call specialists in logical order
[Order guidance]

## Response Synthesis:
After calling all relevant specialists:
1. Combine their responses into ONE cohesive answer
2. Present information in a logical flow
3. Don't mention internal routing to the customer
4. Be conversational and helpful
"""

def get_customer_assistant(callback_handler=None) -> Agent:
    """Get the main assistant (supervisor)."""
    model = BedrockModel(
        model_id=config.LLM_MODEL_ID,
        temperature=0.7,
        max_tokens=2048,
    )
    
    supervisor = Agent(
        name="supervisor",
        system_prompt=SUPERVISOR_PROMPT,
        model=model,
        tools=[
            ask_[domain1]_specialist,
            ask_[domain2]_specialist,
            # ... all specialists
        ],
        callback_handler=callback_handler
    )
    
    return supervisor
```

### 5.3 Agent Prompt Engineering

**Key principles:**

1. **Clear Role Definition**: "You are a [Domain] Specialist..."
2. **Explicit Capabilities**: List what the agent can do
3. **Tool Usage Guidelines**: When to use each tool
4. **Response Style**: Tone, format, level of detail
5. **Error Handling**: What to do when tools fail
6. **Domain Knowledge**: Include relevant context

**Temperature Guidelines:**
- **0.3-0.5**: Factual, deterministic (order tracking, inventory)
- **0.6-0.7**: Balanced (product recommendations, support)
- **0.8-0.9**: Creative (content generation, brainstorming)

---

## Phase 6: Orchestration Patterns

### 6.1 Agents-as-Tools (Default)

**Already implemented in Phase 5.2** - This is the baseline pattern.

**When to use:**
- Simple, single-domain queries
- Predictable routing
- Production stability requirements

### 6.2 Swarm Orchestration

**Create `src/orchestration/swarm_orchestrator.py`:**

```python
"""
Swarm Multi-Agent Orchestration
"""
from strands import Agent
from strands.models import BedrockModel
from strands.multiagent import Swarm

def _create_swarm_[domain]_agent() -> Agent:
    """Create [Domain] Agent for Swarm with handoff awareness."""
    from tools.[domain]_tools import tool1, tool2
    
    model = BedrockModel(
        model_id=config.LLM_MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )
    
    return Agent(
        name="[domain]_specialist",
        system_prompt="""You are a [Domain] Specialist in a collaborative team.

Your expertise: [Expertise description]

When to hand off to other agents:
- Hand off to [OTHER_DOMAIN]_SPECIALIST if [condition]
- Hand off to [ANOTHER_DOMAIN]_SPECIALIST if [condition]

After completing your task, evaluate if another specialist
should continue helping. Use the handoff tool if needed.""",
        model=model,
        tools=[tool1, tool2]
    )

def create_[system]_swarm(entry_agent: str = "[domain]_specialist") -> Swarm:
    """Create collaborative Swarm of agents."""
    agents = [
        _create_swarm_[domain1]_agent(),
        _create_swarm_[domain2]_agent(),
        # ... all agents
    ]
    
    # Find entry point
    entry_point = next((a for a in agents if a.name == entry_agent), agents[0])
    
    return Swarm(
        agents,
        entry_point=entry_point,
        max_handoffs=10,
        max_iterations=15,
        execution_timeout=300.0
    )
```

### 6.3 Graph Workflows

**Create `src/orchestration/graph_workflow.py`:**

```python
"""
Graph Workflow Orchestration
"""
from strands.multiagent import GraphBuilder
from agents import create_[domain]_agent

def create_[workflow_name]_workflow() -> Graph:
    """
    Create [Workflow Name] workflow.
    
    Pipeline: [Step1] → [Step2] → [Step3] → [Step4]
    """
    # Create node agents
    step1_agent = _create_[step1]_node_agent()
    step2_agent = _create_[step2]_node_agent()
    step3_agent = _create_[step3]_node_agent()
    confirmation_agent = _create_confirmation_node_agent()
    
    # Build graph
    builder = GraphBuilder()
    
    # Add nodes
    builder.add_node(step1_agent, "step1")
    builder.add_node(step2_agent, "step2")
    builder.add_node(step3_agent, "step3")
    builder.add_node(confirmation_agent, "confirmation")
    
    # Add edges (execution order)
    builder.add_edge("step1", "step2")
    builder.add_edge("step2", "step3")
    builder.add_edge("step3", "confirmation")
    
    # Set entry point
    builder.set_entry_point("step1")
    
    return builder.build()
```

---

## Phase 7: Agentic Capabilities (Optional)

### 7.1 ReAct Agent

**Create `src/agentic/react_agent.py`:**

```python
"""
ReAct Pattern Implementation (Reasoning + Acting)
"""
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ThoughtAction:
    """Single ReAct step."""
    step_number: int
    thought: str
    action: str
    observation: str
    success: bool

class ReActAgent:
    """Agent with explicit reasoning."""
    
    def __init__(self, tools: List, max_steps: int = 8):
        self.tools = tools
        self.max_steps = max_steps
    
    def run(self, query: str) -> ReActResult:
        """Execute ReAct loop."""
        trace = []
        
        for step in range(self.max_steps):
            # THOUGHT: Reason about next action
            thought = self._think(query, trace)
            
            # ACTION: Execute action
            action, observation = self._act(thought)
            
            trace.append(ThoughtAction(
                step_number=step + 1,
                thought=thought,
                action=action,
                observation=observation,
                success=True
            ))
            
            # Check if done
            if self._is_complete(observation):
                break
        
        return ReActResult(query=query, trace=trace)
```

### 7.2 Goal Planner

**Create `src/agentic/goal_planner.py`:**

```python
"""
Goal Decomposition & Planning
"""
from dataclasses import dataclass
from typing import List

@dataclass
class SubGoal:
    """Single sub-goal."""
    id: str
    description: str
    agent: str
    dependencies: List[str]
    status: str

class GoalPlanner:
    """Decompose complex queries into sub-goals."""
    
    def decompose(self, query: str) -> ExecutionPlan:
        """Break down query into manageable goals."""
        # Use LLM to identify goals
        goals = self._identify_goals(query)
        
        # Determine dependencies
        goals = self._resolve_dependencies(goals)
        
        # Create execution plan
        return ExecutionPlan(goals=goals)
```

### 7.3 Self-Reflection

**Create `src/agentic/reflection.py`:**

```python
"""
Self-Reflection for Quality Improvement
"""
class SelfReflector:
    """Critique and improve responses."""
    
    def reflect_and_improve(self, query: str, response: str) -> ReflectionResult:
        """Analyze response and generate improvements."""
        # Critique response
        critique = self._critique(query, response)
        
        # Generate improved version
        improved = self._improve(response, critique)
        
        return ReflectionResult(
            initial_response=response,
            critique=critique,
            final_response=improved
        )
```

### 7.4 Memory System

**Create `src/agentic/memory.py`:**

```python
"""
Memory-Augmented Agent System
"""
class MemoryStore:
    """Multi-type memory system."""
    
    def __init__(self):
        self.short_term = []      # Recent conversation
        self.working = {}         # Current task state
        self.episodic = []        # Past interaction summaries
        self.long_term = []        # Persistent knowledge
    
    def add_turn(self, role: str, content: str):
        """Add conversation turn."""
        self.short_term.append({"role": role, "content": content})
    
    def assemble_context(self, query: str) -> Dict:
        """Assemble relevant context for query."""
        return {
            "recent": self.short_term[-10:],
            "working": self.working,
            "relevant_episodes": self._retrieve_episodes(query)
        }
```

---

## Phase 8: Frontend Development

### 8.1 Streamlit UI Template

**Create `app/streamlit_app.py`:**

```python
"""
[System Name] - Streamlit UI
"""
import streamlit as st
from agents import get_customer_assistant, get_handoff_tracker

st.set_page_config(
    page_title="[System Name]",
    page_icon="🤖",
    layout="wide"
)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("Settings")
    demo_mode = st.toggle("Demo Mode", value=True)
    orchestration_pattern = st.radio(
        "Pattern:",
        ["agents_as_tools", "swarm", "graph"]
    )

# Main chat
st.title("🤖 [System Name]")

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        if not demo_mode:
            assistant = get_customer_assistant()
            response = assistant(prompt)
            
            # Show thinking if available
            handoffs = get_handoff_tracker()
            if handoffs:
                st.markdown(format_thinking_display(handoffs), unsafe_allow_html=True)
            
            st.markdown(str(response))
        else:
            st.markdown("Demo response...")
    
    st.session_state.messages.append({"role": "assistant", "content": str(response)})
```

### 8.2 Thinking Display

**Add thinking visualization:**

```python
def format_thinking_display(handoffs: List[Dict]) -> str:
    """Format handoff tracker into thinking display."""
    steps = []
    for entry in handoffs:
        if entry["type"] == "handoff":
            steps.append(f"""
            <div style="background: #f7f7f8; padding: 8px; margin: 4px 0; border-radius: 4px;">
                🔄 <strong>{entry['from']}</strong> → <strong>{entry['to']}</strong>
                <br><small>{entry['query'][:60]}...</small>
            </div>
            """)
    return "".join(steps)
```

---

## Phase 9: Testing & Validation

### 9.1 Test Structure

**Create test files:**

```python
# tests/test_tools.py
def test_[tool_name]():
    """Test [tool_name] functionality."""
    result = [tool_name]("test_input")
    assert result["status"] == "success"
    assert len(result["results"]) > 0

# tests/test_agents.py
def test_[domain]_agent():
    """Test [Domain] Agent."""
    agent = create_[domain]_agent()
    response = agent("test query")
    assert response is not None
    assert len(str(response)) > 0

# tests/test_orchestration.py
def test_supervisor_routing():
    """Test supervisor routing logic."""
    assistant = get_customer_assistant()
    response = assistant("test query")
    assert response is not None
```

### 9.2 Validation Checklist

- [ ] All tools return valid JSON
- [ ] Agents handle edge cases (empty results, errors)
- [ ] Supervisor routes correctly to specialists
- [ ] Multi-part queries call multiple agents
- [ ] Error messages are user-friendly
- [ ] Response quality meets requirements
- [ ] Performance is acceptable (< 5s for simple queries)

---

## Phase 10: Deployment & Production

### 10.1 Environment Setup

**Production `.env`:**
```env
LLM_PROVIDER=bedrock
AWS_REGION=us-east-1
# Use IAM roles instead of keys in production
DEBUG_MODE=false
```

### 10.2 Monitoring

**Add logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### 10.3 Error Handling

**Implement graceful degradation:**
```python
try:
    response = agent(query)
except Exception as e:
    logger.error(f"Agent error: {e}")
    response = "I apologize, but I encountered an error. Please try again."
```

---

## Real-World Examples

### Example 1: Amazon Customer Service

**Domains:**
- Product Discovery
- Order Management
- Support & Returns
- Inventory Check
- Pricing & Deals
- Reviews & Ratings
- Logistics & Shipping

**Tools per Domain:**
- Product: search_products, get_recommendations, compare_products
- Order: lookup_order, track_shipment, estimate_delivery
- Support: search_faq, get_policy_info, check_return_eligibility
- Inventory: check_stock_availability, get_warehouse_info
- Pricing: get_active_deals, validate_coupon, get_price_history
- Reviews: get_product_reviews, get_rating_summary
- Logistics: get_shipping_options, calculate_shipping_cost

### Example 2: Amazon Seller Support

**Domains:**
- Listing Management
- Inventory Management
- Order Fulfillment
- Performance Analytics
- Payment & Billing
- Policy Compliance

**Tools per Domain:**
- Listing: create_listing, update_listing, get_listing_status
- Inventory: update_stock, get_inventory_levels, set_restock_alerts
- Fulfillment: process_order, generate_shipping_label, track_fulfillment
- Analytics: get_sales_report, get_performance_metrics
- Payment: get_payment_history, request_payout
- Compliance: check_policy_violations, get_compliance_status

### Example 3: Amazon Internal Operations

**Domains:**
- Warehouse Operations
- Supply Chain Management
- Quality Assurance
- Vendor Management
- Demand Forecasting

**Tools per Domain:**
- Warehouse: optimize_picking, track_inventory_movement, manage_returns
- Supply Chain: forecast_demand, optimize_routing, track_shipments
- QA: schedule_inspections, log_defects, generate_reports
- Vendor: manage_contracts, track_performance, process_invoices
- Forecasting: generate_forecasts, analyze_trends, adjust_inventory

---

## Quick Start Checklist

Use this checklist when starting a new multi-agent system:

### Planning
- [ ] Define problem and success metrics
- [ ] Decompose into domains
- [ ] List required tools per domain
- [ ] Choose orchestration pattern(s)

### Setup
- [ ] Create project structure
- [ ] Set up dependencies
- [ ] Configure environment variables
- [ ] Create data schemas

### Development
- [ ] Implement tools (one domain at a time)
- [ ] Create specialist agents
- [ ] Build supervisor orchestrator
- [ ] Add orchestration patterns (if needed)
- [ ] Implement agentic capabilities (if needed)

### Frontend
- [ ] Create UI (Streamlit/FastAPI/etc.)
- [ ] Add thinking/reasoning display
- [ ] Implement session management
- [ ] Add activity tracking

### Testing
- [ ] Write unit tests for tools
- [ ] Test agent responses
- [ ] Validate routing logic
- [ ] Test error handling

### Production
- [ ] Set up production environment
- [ ] Add monitoring/logging
- [ ] Implement error handling
- [ ] Performance optimization

---

## Best Practices

### 1. Start Simple
- Begin with Agents-as-Tools pattern
- Add complexity (Swarm, Graph, Agentic) only if needed
- One domain at a time

### 2. Tool Design
- Keep tools focused and single-purpose
- Return structured JSON
- Handle errors gracefully
- Document thoroughly

### 3. Agent Prompts
- Be explicit about capabilities
- Include examples
- Define response style
- Specify tool usage

### 4. Testing
- Test each component independently
- Use realistic test data
- Test edge cases
- Validate end-to-end flows

### 5. Iteration
- Start with MVP
- Gather user feedback
- Refine prompts based on results
- Add features incrementally

---

## Common Pitfalls & Solutions

### Pitfall 1: Over-complicated Routing
**Problem:** Supervisor calls too many agents unnecessarily

**Solution:** 
- Refine supervisor prompt with clearer routing rules
- Add examples of when NOT to call certain agents
- Use temperature 0.5-0.6 for more deterministic routing

### Pitfall 2: Tool Errors Not Handled
**Problem:** Tools crash and break the agent

**Solution:**
- Always wrap tool logic in try-except
- Return error status in JSON response
- Let agents handle errors gracefully

### Pitfall 3: Poor Response Quality
**Problem:** Agents give generic or unhelpful responses

**Solution:**
- Improve system prompts with domain knowledge
- Add examples of good responses
- Use reflection to improve quality
- Fine-tune temperature settings

### Pitfall 4: Slow Performance
**Problem:** System takes too long to respond

**Solution:**
- Cache agent instances
- Optimize tool queries
- Use parallel execution where possible
- Set appropriate timeouts

---

## Conclusion

This template provides a complete skeleton for building multi-agent AI systems. Follow the phases chronologically, adapt the templates to your specific domain, and iterate based on feedback.

**Remember:**
- Start simple, add complexity gradually
- Test thoroughly at each phase
- Document your decisions
- Keep user experience in mind
- Monitor and improve continuously

**Happy Building! 🚀**

