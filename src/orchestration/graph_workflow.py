"""
==============================================================================
Graph Workflow Orchestration
==============================================================================
Implements deterministic workflow pipelines using the Strands Graph pattern.
Graphs define explicit execution order with nodes (agents) and edges 
(dependencies), enabling structured multi-step processes.

Example Workflows:
    - Order Processing: Order → Inventory → Logistics → Confirmation
    - Product Research: Product → Reviews → Pricing → Recommendation
    - Support Escalation: Support → Order → Logistics → Resolution

Key Features:
    - Deterministic execution order
    - Parallel execution for independent tasks
    - Conditional edges for dynamic workflows
    - Feedback loops for iterative refinement
    - Custom nodes for business logic

Usage:
    from orchestration import create_order_workflow, create_research_workflow
    
    workflow = create_order_workflow()
    result = workflow("Process order ORD-1001 for shipping")
==============================================================================
"""

import logging
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass

from strands import Agent
from strands.models import BedrockModel

# Try to import Graph components from strands
try:
    from strands.multiagent import GraphBuilder
    from strands.multiagent.graph import Graph
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False
    GraphBuilder = None
    Graph = None

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config

# Enable logging for debugging
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)


# =============================================================================
# Graph Node Agents
# =============================================================================

def _create_order_node_agent() -> Agent:
    """Create Order Agent optimized for graph workflows."""
    from tools.order_tools import lookup_order, track_shipment, get_order_history
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.5,  # More deterministic for workflows
        max_tokens=1024
    )
    
    return Agent(
        name="order_processor",
        system_prompt="""You are an Order Processor in a workflow pipeline.

Your task: Extract and validate order information for the next step.

Output format: Provide a clear summary including:
- Order ID
- Order status
- Items in order (product IDs)
- Customer shipping address (zip code)
- Any special instructions

Be concise and structured - your output feeds into the next workflow step.""",
        model=model,
        tools=[lookup_order, track_shipment, get_order_history]
    )


def _create_inventory_node_agent() -> Agent:
    """Create Inventory Agent optimized for graph workflows."""
    from tools.inventory_tools import check_stock_availability, get_warehouse_info, find_nearest_warehouse
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.5,
        max_tokens=1024
    )
    
    return Agent(
        name="inventory_checker",
        system_prompt="""You are an Inventory Checker in a workflow pipeline.

Your task: Verify stock availability for order items.

Based on the order information provided, check:
- Stock availability for each product
- Which warehouse has the items
- Any low stock alerts

Output format: Provide clear status for each item:
- Product ID: [Available/Out of Stock] at [Warehouse]
- Recommended fulfillment warehouse
- Any concerns or alternatives needed

Be concise - your output feeds into logistics planning.""",
        model=model,
        tools=[check_stock_availability, get_warehouse_info, find_nearest_warehouse]
    )


def _create_logistics_node_agent() -> Agent:
    """Create Logistics Agent optimized for graph workflows."""
    from tools.logistics_tools import (
        get_shipping_options, calculate_shipping_cost,
        get_delivery_slots, get_carrier_info
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.5,
        max_tokens=1024
    )
    
    return Agent(
        name="logistics_planner",
        system_prompt="""You are a Logistics Planner in a workflow pipeline.

Your task: Plan optimal shipping based on inventory and order info.

Based on inventory availability and shipping address, determine:
- Best shipping method
- Estimated delivery date
- Shipping cost
- Recommended carrier

Output format: Provide shipping plan:
- Carrier: [Name]
- Method: [Standard/Express/etc]
- Estimated delivery: [Date]
- Cost: [$X.XX]
- Ships from: [Warehouse]

Be concise and actionable.""",
        model=model,
        tools=[get_shipping_options, calculate_shipping_cost,
               get_delivery_slots, get_carrier_info]
    )


def _create_pricing_node_agent() -> Agent:
    """Create Pricing Agent optimized for graph workflows."""
    from tools.pricing_tools import (
        get_active_deals, calculate_best_price,
        validate_coupon, get_lightning_deals
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.5,
        max_tokens=1024
    )
    
    return Agent(
        name="pricing_optimizer",
        system_prompt="""You are a Pricing Optimizer in a workflow pipeline.

Your task: Find the best price and applicable discounts.

For the products identified, check:
- Active deals and promotions
- Applicable coupons
- Lightning deals
- Calculate final best price

Output format: Provide pricing summary:
- Original price: $X.XX
- Discounts applied: [List]
- Final price: $X.XX
- Savings: $X.XX (X%)

Be concise and value-focused.""",
        model=model,
        tools=[get_active_deals, calculate_best_price,
               validate_coupon, get_lightning_deals]
    )


def _create_reviews_node_agent() -> Agent:
    """Create Reviews Agent optimized for graph workflows."""
    from tools.reviews_tools import (
        get_product_reviews, get_rating_summary,
        get_review_highlights
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.5,
        max_tokens=1024
    )
    
    return Agent(
        name="review_analyzer",
        system_prompt="""You are a Review Analyzer in a workflow pipeline.

Your task: Summarize customer sentiment for products.

For the products identified, provide:
- Overall rating
- Key positive points
- Key concerns
- Purchase recommendation

Output format: Brief review summary:
- Rating: X.X/5 (N reviews)
- Pros: [Top 3 points]
- Cons: [Top concerns if any]
- Verdict: [Recommended/Consider alternatives]

Be concise and balanced.""",
        model=model,
        tools=[get_product_reviews, get_rating_summary, get_review_highlights]
    )


def _create_product_node_agent() -> Agent:
    """Create Product Agent optimized for graph workflows."""
    from tools.product_tools import (
        search_products, get_product_details,
        get_recommendations
    )
    
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.5,
        max_tokens=1024
    )
    
    return Agent(
        name="product_finder",
        system_prompt="""You are a Product Finder in a workflow pipeline.

Your task: Find and detail relevant products.

Based on the query, provide:
- Product ID(s) found
- Key specifications
- Price range
- Category

Output format: Product summary:
- Product: [Name] (ID: [PROD-XXX])
- Category: [Category]
- Price: $X.XX
- Key specs: [Brief list]

Be concise - your output feeds into review/pricing analysis.""",
        model=model,
        tools=[search_products, get_product_details, get_recommendations]
    )


def _create_confirmation_node_agent() -> Agent:
    """Create Confirmation Agent for final workflow step."""
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=1024
    )
    
    return Agent(
        name="confirmation_generator",
        system_prompt="""You are a Confirmation Generator in a workflow pipeline.

Your task: Create a clear, customer-friendly summary of the completed workflow.

Synthesize all previous information into a cohesive response:
- Summarize what was processed
- Confirm key details
- Provide next steps if applicable
- Be warm and professional

Format your response as a customer communication.""",
        model=model,
        tools=[]  # No tools - just synthesis
    )


# =============================================================================
# Workflow Factories
# =============================================================================

def create_order_workflow(
    execution_timeout: float = 300.0,
    node_timeout: float = 60.0
) -> Optional[Any]:
    """
    Create Order Processing Workflow.
    
    Pipeline: Order → Inventory → Logistics → Confirmation
    
    This workflow handles end-to-end order processing:
    1. Order: Look up and validate order details
    2. Inventory: Check stock availability
    3. Logistics: Plan shipping
    4. Confirmation: Generate customer summary
    
    Args:
        execution_timeout: Total workflow timeout (seconds)
        node_timeout: Per-node timeout (seconds)
        
    Returns:
        Graph workflow instance
    """
    if not GRAPH_AVAILABLE:
        print("Warning: Strands Graph not available. Install strands-agents>=1.19")
        return FallbackWorkflow("order")
    
    # Create node agents
    order_agent = _create_order_node_agent()
    inventory_agent = _create_inventory_node_agent()
    logistics_agent = _create_logistics_node_agent()
    confirmation_agent = _create_confirmation_node_agent()
    
    # Build the graph
    builder = GraphBuilder()
    
    # Add nodes
    builder.add_node(order_agent, "order")
    builder.add_node(inventory_agent, "inventory")
    builder.add_node(logistics_agent, "logistics")
    builder.add_node(confirmation_agent, "confirmation")
    
    # Add edges (sequential pipeline)
    builder.add_edge("order", "inventory")
    builder.add_edge("inventory", "logistics")
    builder.add_edge("logistics", "confirmation")
    
    # Set entry point
    builder.set_entry_point("order")
    
    # Configure timeouts
    builder.set_execution_timeout(execution_timeout)
    builder.set_node_timeout(node_timeout)
    
    # Build and return
    return builder.build()


def create_research_workflow(
    execution_timeout: float = 300.0,
    node_timeout: float = 60.0
) -> Optional[Any]:
    """
    Create Product Research Workflow.
    
    Pipeline: Product → [Reviews | Pricing] (parallel) → Confirmation
    
    This workflow helps customers research products:
    1. Product: Find and detail the product
    2. Reviews: Analyze customer feedback (parallel)
    3. Pricing: Find best deals (parallel)
    4. Confirmation: Synthesize recommendation
    
    Args:
        execution_timeout: Total workflow timeout (seconds)
        node_timeout: Per-node timeout (seconds)
        
    Returns:
        Graph workflow instance
    """
    if not GRAPH_AVAILABLE:
        print("Warning: Strands Graph not available. Install strands-agents>=1.19")
        return FallbackWorkflow("research")
    
    # Create node agents
    product_agent = _create_product_node_agent()
    reviews_agent = _create_reviews_node_agent()
    pricing_agent = _create_pricing_node_agent()
    confirmation_agent = _create_confirmation_node_agent()
    
    # Build the graph
    builder = GraphBuilder()
    
    # Add nodes
    builder.add_node(product_agent, "product")
    builder.add_node(reviews_agent, "reviews")
    builder.add_node(pricing_agent, "pricing")
    builder.add_node(confirmation_agent, "recommendation")
    
    # Add edges (parallel for reviews and pricing)
    builder.add_edge("product", "reviews")
    builder.add_edge("product", "pricing")
    builder.add_edge("reviews", "recommendation")
    builder.add_edge("pricing", "recommendation")
    
    # Set entry point
    builder.set_entry_point("product")
    
    # Configure timeouts
    builder.set_execution_timeout(execution_timeout)
    builder.set_node_timeout(node_timeout)
    
    # Build and return
    return builder.build()


def create_stock_check_workflow(
    execution_timeout: float = 180.0,
    node_timeout: float = 45.0
) -> Optional[Any]:
    """
    Create Stock Check Workflow.
    
    Pipeline: Product → Inventory → Logistics
    
    Quick workflow to check availability and shipping:
    1. Product: Identify the product
    2. Inventory: Check stock levels
    3. Logistics: Show shipping options
    
    Args:
        execution_timeout: Total workflow timeout (seconds)
        node_timeout: Per-node timeout (seconds)
        
    Returns:
        Graph workflow instance
    """
    if not GRAPH_AVAILABLE:
        print("Warning: Strands Graph not available.")
        return FallbackWorkflow("stock_check")
    
    # Create node agents
    product_agent = _create_product_node_agent()
    inventory_agent = _create_inventory_node_agent()
    logistics_agent = _create_logistics_node_agent()
    
    # Build the graph
    builder = GraphBuilder()
    
    # Add nodes
    builder.add_node(product_agent, "product")
    builder.add_node(inventory_agent, "inventory")
    builder.add_node(logistics_agent, "logistics")
    
    # Add edges
    builder.add_edge("product", "inventory")
    builder.add_edge("inventory", "logistics")
    
    # Set entry point
    builder.set_entry_point("product")
    
    # Configure timeouts
    builder.set_execution_timeout(execution_timeout)
    builder.set_node_timeout(node_timeout)
    
    return builder.build()


# =============================================================================
# Conditional Edge Functions
# =============================================================================

def needs_inventory_check(state) -> bool:
    """Check if inventory verification is needed based on order status."""
    order_result = state.results.get("order")
    if not order_result:
        return False
    result_text = str(order_result.result).lower()
    return "pending" in result_text or "processing" in result_text


def is_in_stock(state) -> bool:
    """Check if items are in stock based on inventory check."""
    inventory_result = state.results.get("inventory")
    if not inventory_result:
        return False
    result_text = str(inventory_result.result).lower()
    return "available" in result_text and "out of stock" not in result_text


def needs_alternative(state) -> bool:
    """Check if alternative products should be suggested."""
    inventory_result = state.results.get("inventory")
    if not inventory_result:
        return False
    result_text = str(inventory_result.result).lower()
    return "out of stock" in result_text or "unavailable" in result_text


# =============================================================================
# Graph Result Handler
# =============================================================================

@dataclass
class WorkflowResult:
    """Structured result from workflow execution."""
    status: str
    final_response: str
    execution_order: List[str]
    node_results: Dict[str, str]
    execution_time_ms: float
    total_nodes: int
    completed_nodes: int


def process_graph_result(result) -> WorkflowResult:
    """
    Process Graph execution result into structured format.
    
    Args:
        result: GraphResult from Graph execution
        
    Returns:
        WorkflowResult with processed data
    """
    # Extract node results
    node_results = {}
    for node_id, node_result in getattr(result, 'results', {}).items():
        if hasattr(node_result, 'result'):
            node_results[node_id] = str(node_result.result)
    
    return WorkflowResult(
        status=str(getattr(result, 'status', 'unknown')),
        final_response=str(result) if result else "No response",
        execution_order=[
            node.node_id for node in getattr(result, 'execution_order', [])
        ],
        node_results=node_results,
        execution_time_ms=getattr(result, 'execution_time', 0),
        total_nodes=getattr(result, 'total_nodes', 0),
        completed_nodes=getattr(result, 'completed_nodes', 0)
    )


# =============================================================================
# Fallback Workflow (Demo Mode)
# =============================================================================

class FallbackWorkflow:
    """
    Fallback workflow for when Strands Graph is not available.
    Executes agents sequentially to simulate workflow.
    """
    
    WORKFLOW_CONFIGS = {
        "order": ["order", "inventory", "logistics", "confirmation"],
        "research": ["product", "reviews", "pricing", "confirmation"],
        "stock_check": ["product", "inventory", "logistics"]
    }
    
    def __init__(self, workflow_type: str):
        """Initialize fallback workflow."""
        self.workflow_type = workflow_type
        self.steps = self.WORKFLOW_CONFIGS.get(workflow_type, ["confirmation"])
        self.agents = {}
    
    def _get_agent(self, step: str) -> Agent:
        """Lazy load agent for step."""
        if step not in self.agents:
            agent_creators = {
                "order": _create_order_node_agent,
                "inventory": _create_inventory_node_agent,
                "logistics": _create_logistics_node_agent,
                "pricing": _create_pricing_node_agent,
                "reviews": _create_reviews_node_agent,
                "product": _create_product_node_agent,
                "confirmation": _create_confirmation_node_agent
            }
            if step in agent_creators:
                self.agents[step] = agent_creators[step]()
        return self.agents.get(step)
    
    def __call__(self, task: str) -> str:
        """Execute workflow sequentially."""
        context = task
        results = {}
        
        for step in self.steps:
            agent = self._get_agent(step)
            if agent:
                # Build context from previous steps
                if results:
                    prev_context = "\n\n".join([
                        f"[{s}]: {r}" for s, r in results.items()
                    ])
                    full_prompt = f"Previous workflow steps:\n{prev_context}\n\nOriginal task: {task}"
                else:
                    full_prompt = task
                
                response = agent(full_prompt)
                results[step] = str(response)
                context = str(response)
        
        return context


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Graph Workflow Pattern - Deterministic Pipelines")
    print("=" * 70)
    
    print("\nGraph Available:", GRAPH_AVAILABLE)
    
    print("\n" + "-" * 70)
    print("Available Workflows:")
    print("-" * 70)
    
    workflows = [
        ("Order Processing", "Order → Inventory → Logistics → Confirmation"),
        ("Product Research", "Product → [Reviews | Pricing] → Recommendation"),
        ("Stock Check", "Product → Inventory → Logistics")
    ]
    
    for name, pipeline in workflows:
        print(f"\n{name}:")
        print(f"  Pipeline: {pipeline}")
    
    print("\n" + "-" * 70)
    print("Example Usage:")
    print("-" * 70)
    print("""
    # Create and run order workflow
    workflow = create_order_workflow()
    result = workflow("Process order ORD-1001 for shipping")
    
    # Create and run research workflow  
    workflow = create_research_workflow()
    result = workflow("Research gaming laptops under $1500")
    """)
