"""
==============================================================================
LangGraph Agentic Agent - Full Autonomous Capabilities
==============================================================================
Implements ReAct, Goal Planning, Self-Reflection, and Memory using LangGraph.

LangGraph provides:
    - Graph-based agent workflows with cycles
    - Built-in state management
    - ReAct pattern support
    - Conditional routing
    - Human-in-the-loop patterns

This replaces the custom agentic implementation with LangGraph's native
capabilities while maintaining the same interface.

Usage:
    from agentic import LangGraphAgent
    
    agent = LangGraphAgent()
    result = agent.process("Find me a gaming laptop, check reviews, verify stock")
    
    print(result.final_response)
    print(result.reasoning_trace)
==============================================================================
"""

import json
import time
import operator
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Annotated, TypedDict, Sequence, Literal
from datetime import datetime
from enum import Enum

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.prebuilt import ToolNode, tools_condition
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None
    START = None

# LangChain imports
try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.tools import tool as langchain_tool
    from langchain_core.output_parsers import StrOutputParser
    from langchain_aws import ChatBedrock
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatBedrock = None

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config


# =============================================================================
# State Definitions
# =============================================================================

class AgentState(TypedDict):
    """State maintained throughout the agent execution."""
    # Core conversation
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Current query being processed
    current_query: str
    
    # Goal planning state
    goals: List[Dict[str, Any]]
    current_goal_index: int
    goal_results: Dict[str, str]
    
    # ReAct reasoning trace
    reasoning_trace: List[Dict[str, Any]]
    current_thought: str
    
    # Reflection state
    draft_response: str
    reflection_count: int
    quality_score: float
    critiques: List[str]
    
    # Memory
    conversation_history: List[Dict[str, str]]
    working_memory: Dict[str, Any]
    
    # Control flow
    processing_mode: str  # "simple", "standard", "complex"
    should_continue: bool
    final_response: str
    
    # Metrics
    total_steps: int
    start_time: float


# =============================================================================
# Tool Definitions (Convert existing tools to LangChain format)
# =============================================================================

def create_langchain_tools():
    """Create LangChain-compatible tools from existing tools."""
    tools = []
    
    # Import existing tools
    try:
        from tools.product_tools import search_products, get_recommendations, compare_products, get_product_details
        from tools.order_tools import lookup_order, track_shipment, estimate_delivery, get_order_history
        from tools.support_tools import search_faq, get_policy_info, check_return_eligibility
        from tools.inventory_tools import check_stock_availability, get_warehouse_info, find_nearest_warehouse
        from tools.pricing_tools import get_active_deals, validate_coupon, get_price_history, calculate_best_price
        from tools.reviews_tools import get_product_reviews, get_rating_summary, get_review_highlights
        from tools.logistics_tools import get_shipping_options, calculate_shipping_cost, get_delivery_slots
        
        # Wrap each tool for LangChain
        @langchain_tool
        def lc_search_products(query: str, category: str = None, max_price: float = None) -> str:
            """Search for products based on a text query with optional filters.
            
            Args:
                query: The search query describing what the customer wants
                category: Optional category filter (e.g., "Laptops", "Audio")
                max_price: Optional maximum price filter in dollars
            """
            return search_products(query, category, max_price)
        
        @langchain_tool
        def lc_get_recommendations(query: str, num_recommendations: int = 3) -> str:
            """Get AI-powered product recommendations using the PyTorch model.
            
            Args:
                query: Description of what the customer is looking for
                num_recommendations: Number of products to recommend (default: 3)
            """
            return get_recommendations(query, num_recommendations)
        
        @langchain_tool
        def lc_compare_products(product_ids: List[str]) -> str:
            """Compare multiple products side-by-side.
            
            Args:
                product_ids: List of product IDs to compare (e.g., ["P001", "P002"])
            """
            return compare_products(product_ids)
        
        @langchain_tool
        def lc_get_product_details(product_id: str) -> str:
            """Get detailed information about a specific product.
            
            Args:
                product_id: The unique product ID (e.g., "P001")
            """
            return get_product_details(product_id)
        
        @langchain_tool
        def lc_lookup_order(order_id: str) -> str:
            """Look up an order by its order ID.
            
            Args:
                order_id: The order ID to look up (format: ORD-XXXX)
            """
            return lookup_order(order_id)
        
        @langchain_tool
        def lc_track_shipment(order_id: str) -> str:
            """Get detailed tracking information for an order's shipment.
            
            Args:
                order_id: The order ID to track
            """
            return track_shipment(order_id)
        
        @langchain_tool
        def lc_check_stock_availability(product_id: str) -> str:
            """Check if a product is in stock and get availability details.
            
            Args:
                product_id: The product ID to check stock for
            """
            return check_stock_availability(product_id)
        
        @langchain_tool
        def lc_get_warehouse_info(warehouse_id: str = None) -> str:
            """Get information about warehouses and their stock levels.
            
            Args:
                warehouse_id: Optional specific warehouse ID
            """
            return get_warehouse_info(warehouse_id)
        
        @langchain_tool
        def lc_get_active_deals(category: str = None, product_id: str = None) -> str:
            """Get currently active deals and promotions.
            
            Args:
                category: Optional category filter
                product_id: Optional specific product ID
            """
            return get_active_deals(category, product_id)
        
        @langchain_tool
        def lc_validate_coupon(coupon_code: str) -> str:
            """Validate a coupon code and get its details.
            
            Args:
                coupon_code: The coupon code to validate
            """
            return validate_coupon(coupon_code)
        
        @langchain_tool
        def lc_get_product_reviews(product_id: str, limit: int = 5) -> str:
            """Get customer reviews for a product.
            
            Args:
                product_id: The product ID to get reviews for
                limit: Maximum number of reviews to return
            """
            return get_product_reviews(product_id, limit)
        
        @langchain_tool
        def lc_get_rating_summary(product_id: str) -> str:
            """Get rating summary and statistics for a product.
            
            Args:
                product_id: The product ID to get ratings for
            """
            return get_rating_summary(product_id)
        
        @langchain_tool
        def lc_get_shipping_options(zip_code: str, product_id: str = None) -> str:
            """Get available shipping options for a destination.
            
            Args:
                zip_code: Destination ZIP code
                product_id: Optional product ID for specific shipping info
            """
            return get_shipping_options(zip_code, product_id)
        
        @langchain_tool
        def lc_calculate_shipping_cost(zip_code: str, product_id: str, shipping_method: str = "standard") -> str:
            """Calculate shipping cost for a product to a destination.
            
            Args:
                zip_code: Destination ZIP code
                product_id: Product ID to ship
                shipping_method: Shipping method (standard, express, overnight)
            """
            return calculate_shipping_cost(zip_code, product_id, shipping_method)
        
        @langchain_tool
        def lc_search_faq(query: str) -> str:
            """Search the FAQ database for answers.
            
            Args:
                query: The question or topic to search for
            """
            return search_faq(query)
        
        @langchain_tool
        def lc_get_policy_info(policy_type: str) -> str:
            """Get information about store policies.
            
            Args:
                policy_type: Type of policy (return, shipping, warranty, etc.)
            """
            return get_policy_info(policy_type)
        
        tools = [
            lc_search_products,
            lc_get_recommendations,
            lc_compare_products,
            lc_get_product_details,
            lc_lookup_order,
            lc_track_shipment,
            lc_check_stock_availability,
            lc_get_warehouse_info,
            lc_get_active_deals,
            lc_validate_coupon,
            lc_get_product_reviews,
            lc_get_rating_summary,
            lc_get_shipping_options,
            lc_calculate_shipping_cost,
            lc_search_faq,
            lc_get_policy_info,
        ]
        
    except ImportError as e:
        print(f"Warning: Could not import tools: {e}")
    
    return tools


# =============================================================================
# Graph Nodes
# =============================================================================

def create_llm():
    """Create the LangChain LLM instance."""
    return ChatBedrock(
        model_id=config.BEDROCK_MODEL_ID,
        model_kwargs={
            "temperature": 0.7,
            "max_tokens": 2048,
        },
        region_name=config.AWS_REGION,
    )


def create_llm_with_tools():
    """Create LLM with tools bound for tool calling."""
    llm = create_llm()
    tools = create_langchain_tools()
    return llm.bind_tools(tools), tools


def query_analyzer(state: AgentState) -> AgentState:
    """Analyze the query to determine processing mode and decompose into goals."""
    query = state["current_query"]
    query_lower = query.lower()
    
    # Determine processing mode
    simple_indicators = ["hi", "hello", "thanks", "you're welcome", "bye", "goodbye"]
    complex_indicators = ["and", "also", "plus", "compare", "best", "recommend", "check", "verify", ","]
    
    # Check if it's a simple greeting/polite query
    is_simple = any(query_lower.strip().startswith(ind) or query_lower.strip() == ind for ind in simple_indicators)
    
    if is_simple:
        mode = "simple"
        goals = []
    else:
        # Check for multi-part queries (contains "and" or multiple commas)
        complex_count = sum(1 for ind in complex_indicators if ind in query_lower)
        has_multiple_parts = query_lower.count(",") >= 1 or query_lower.count(" and ") >= 1
        
        if complex_count >= 1 or has_multiple_parts:
            mode = "complex"
            # Decompose into goals
            goals = decompose_query_to_goals(query)
        else:
            mode = "standard"
            goals = [{"id": "goal_1", "description": query, "status": "pending"}]
    
    # Add reasoning trace
    reasoning_trace = state.get("reasoning_trace", [])
    reasoning_trace.append({
        "step": len(reasoning_trace) + 1,
        "type": "analysis",
        "thought": f"Query analyzed. Mode: {mode}. Goals identified: {len(goals)}",
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        **state,
        "processing_mode": mode,
        "goals": goals,
        "current_goal_index": 0,
        "reasoning_trace": reasoning_trace,
        "total_steps": state.get("total_steps", 0) + 1
    }


def decompose_query_to_goals(query: str) -> List[Dict[str, Any]]:
    """Decompose a complex query into sub-goals."""
    goals = []
    query_lower = query.lower()
    
    # Product-related goals
    if any(word in query_lower for word in ["laptop", "product", "find", "search", "recommend"]):
        goals.append({
            "id": "goal_product",
            "description": "Find and recommend products matching the query",
            "agent": "product",
            "status": "pending",
            "dependencies": []
        })
    
    # Stock/Inventory goals
    if any(word in query_lower for word in ["stock", "available", "in stock", "availability"]):
        goals.append({
            "id": "goal_inventory",
            "description": "Check stock availability for recommended products",
            "agent": "inventory",
            "status": "pending",
            "dependencies": ["goal_product"] if any(g["id"] == "goal_product" for g in goals) else []
        })
    
    # Review goals
    if any(word in query_lower for word in ["review", "rating", "feedback"]):
        goals.append({
            "id": "goal_reviews",
            "description": "Get customer reviews and ratings",
            "agent": "reviews",
            "status": "pending",
            "dependencies": ["goal_product"] if any(g["id"] == "goal_product" for g in goals) else []
        })
    
    # Pricing goals
    if any(word in query_lower for word in ["deal", "discount", "price", "coupon"]):
        goals.append({
            "id": "goal_pricing",
            "description": "Check for deals and best prices",
            "agent": "pricing",
            "status": "pending",
            "dependencies": ["goal_product"] if any(g["id"] == "goal_product" for g in goals) else []
        })
    
    # Shipping goals
    if any(word in query_lower for word in ["shipping", "delivery", "ship to"]):
        # Extract zip code if present
        import re
        zip_match = re.search(r'\b(\d{5})\b', query)
        zip_code = zip_match.group(1) if zip_match else None
        
        goals.append({
            "id": "goal_shipping",
            "description": f"Get shipping options{' to ' + zip_code if zip_code else ''}",
            "agent": "logistics",
            "status": "pending",
            "dependencies": [],
            "parameters": {"zip_code": zip_code}
        })
    
    # Order goals
    if any(word in query_lower for word in ["order", "track", "ord-"]):
        import re
        order_match = re.search(r'ORD-\d+', query, re.IGNORECASE)
        order_id = order_match.group(0).upper() if order_match else None
        
        goals.append({
            "id": "goal_order",
            "description": f"Look up order {order_id}" if order_id else "Look up order information",
            "agent": "order",
            "status": "pending",
            "dependencies": [],
            "parameters": {"order_id": order_id}
        })
    
    # If no specific goals identified, create a general goal
    if not goals:
        goals.append({
            "id": "goal_general",
            "description": query,
            "agent": "general",
            "status": "pending",
            "dependencies": []
        })
    
    return goals


def simple_responder(state: AgentState) -> AgentState:
    """Handle simple queries with direct responses."""
    query = state["current_query"].lower().strip()
    
    # Only respond with greeting if it's a pure greeting
    if query in ["hi", "hello", "hey", "hello!", "hi there", "hey there"]:
        response = "Hello! I'm your Smart Customer Assistant. What can I help you with?"
    elif "thank" in query:
        response = "You're welcome! Is there anything else I can help you with?"
    elif query in ["ok", "okay", "yes", "no"]:
        response = "I understand. How can I assist you further?"
    else:
        # For any other simple query, treat it as standard mode
        return {
            **state,
            "processing_mode": "standard",
            "should_continue": True
        }
    
    reasoning_trace = state.get("reasoning_trace", [])
    reasoning_trace.append({
        "step": len(reasoning_trace) + 1,
        "type": "response",
        "thought": "Simple query - providing direct response",
        "action": "respond",
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        **state,
        "final_response": response,
        "should_continue": False,
        "reasoning_trace": reasoning_trace,
        "total_steps": state.get("total_steps", 0) + 1
    }


def react_reasoner(state: AgentState) -> AgentState:
    """ReAct reasoning node - Think about what to do next."""
    goals = state.get("goals", [])
    goal_results = state.get("goal_results", {})
    current_goal_index = state.get("current_goal_index", 0)
    
    if current_goal_index >= len(goals):
        # All goals completed
        return {
            **state,
            "should_continue": False,
            "current_thought": "All goals completed. Ready to synthesize response."
        }
    
    current_goal = goals[current_goal_index]
    
    # Check dependencies
    dependencies = current_goal.get("dependencies", [])
    deps_satisfied = all(dep in goal_results for dep in dependencies)
    
    if not deps_satisfied:
        # Skip to next goal or wait
        return {
            **state,
            "current_goal_index": current_goal_index + 1,
            "current_thought": f"Dependencies not met for {current_goal['id']}. Moving to next goal."
        }
    
    reasoning_trace = state.get("reasoning_trace", [])
    reasoning_trace.append({
        "step": len(reasoning_trace) + 1,
        "type": "thought",
        "goal": current_goal["id"],
        "thought": f"Processing goal: {current_goal['description']}",
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        **state,
        "current_thought": f"Working on: {current_goal['description']}",
        "reasoning_trace": reasoning_trace,
        "total_steps": state.get("total_steps", 0) + 1
    }


def tool_executor(state: AgentState) -> AgentState:
    """Execute tools based on current goal - uses direct tool calls instead of LLM tool binding."""
    goals = state.get("goals", [])
    current_goal_index = state.get("current_goal_index", 0)
    goal_results = state.get("goal_results", {})
    
    if current_goal_index >= len(goals):
        return state
    
    current_goal = goals[current_goal_index]
    goal_id = current_goal.get("id", "unknown")
    query = state["current_query"]
    
    # Import tools directly and execute based on goal type
    tool_results = []
    
    try:
        if goal_id == "goal_product" or "product" in current_goal.get("agent", ""):
            # Execute product search
            from tools.product_tools import search_products, get_recommendations
            
            # Extract price from query if present
            import re
            price_match = re.search(r'\$?(\d+(?:,\d{3})*)', query)
            max_price = float(price_match.group(1).replace(',', '')) if price_match else None
            
            result = search_products(query, max_price=max_price)
            tool_results.append({"tool": "search_products", "result": result})
            
        elif goal_id == "goal_inventory" or "inventory" in current_goal.get("agent", ""):
            # Execute inventory check
            from tools.inventory_tools import check_stock_availability
            
            # Get product ID from previous results or use default
            prev_results = goal_results.get("goal_product", "{}")
            try:
                prev_data = json.loads(prev_results) if isinstance(prev_results, str) else prev_results
                # Try to extract product ID
                if isinstance(prev_data, list) and len(prev_data) > 0:
                    product_id = prev_data[0].get("result", {}).get("products", [{}])[0].get("id", "PROD-001")
                elif isinstance(prev_data, dict):
                    product_id = prev_data.get("products", [{}])[0].get("id", "PROD-001")
                else:
                    product_id = "PROD-001"
            except:
                product_id = "PROD-001"
            
            result = check_stock_availability(product_id)
            tool_results.append({"tool": "check_stock_availability", "result": result, "product_id": product_id})
            
        elif goal_id == "goal_shipping" or "logistics" in current_goal.get("agent", ""):
            # Execute shipping options lookup
            from tools.logistics_tools import get_shipping_options
            
            # Extract zip code from parameters or query
            zip_code = current_goal.get("parameters", {}).get("zip_code")
            if not zip_code:
                import re
                zip_match = re.search(r'\b(\d{5})\b', query)
                zip_code = zip_match.group(1) if zip_match else "90210"
            
            result = get_shipping_options(zip_code)
            tool_results.append({"tool": "get_shipping_options", "result": result, "zip_code": zip_code})
            
        elif goal_id == "goal_reviews" or "reviews" in current_goal.get("agent", ""):
            # Execute reviews lookup
            from tools.reviews_tools import get_product_reviews, get_rating_summary
            
            # Get product ID from previous results
            prev_results = goal_results.get("goal_product", "{}")
            try:
                prev_data = json.loads(prev_results) if isinstance(prev_results, str) else prev_results
                if isinstance(prev_data, list) and len(prev_data) > 0:
                    product_id = prev_data[0].get("result", {}).get("products", [{}])[0].get("id", "PROD-001")
                else:
                    product_id = "PROD-001"
            except:
                product_id = "PROD-001"
            
            result = get_rating_summary(product_id)
            tool_results.append({"tool": "get_rating_summary", "result": result})
            
        elif goal_id == "goal_pricing" or "pricing" in current_goal.get("agent", ""):
            # Execute pricing lookup
            from tools.pricing_tools import get_active_deals
            
            result = get_active_deals()
            tool_results.append({"tool": "get_active_deals", "result": result})
            
        elif goal_id == "goal_order" or "order" in current_goal.get("agent", ""):
            # Execute order lookup
            from tools.order_tools import lookup_order, track_shipment
            
            order_id = current_goal.get("parameters", {}).get("order_id")
            if not order_id:
                import re
                order_match = re.search(r'ORD-\d+', query, re.IGNORECASE)
                order_id = order_match.group(0).upper() if order_match else "ORD-1001"
            
            result = lookup_order(order_id)
            tool_results.append({"tool": "lookup_order", "result": result, "order_id": order_id})
            
        else:
            # General goal - try product search as default
            from tools.product_tools import search_products
            result = search_products(query)
            tool_results.append({"tool": "search_products", "result": result})
            
    except Exception as e:
        tool_results.append({"error": str(e), "goal": goal_id})
    
    # Update goal results
    if tool_results:
        goal_results[goal_id] = json.dumps(tool_results, indent=2)
    
    # Mark goal as completed and move to next
    goals[current_goal_index]["status"] = "completed"
    
    reasoning_trace = state.get("reasoning_trace", [])
    reasoning_trace.append({
        "step": len(reasoning_trace) + 1,
        "type": "action",
        "goal": goal_id,
        "tools_used": [tr.get("tool", "unknown") for tr in tool_results if "tool" in tr],
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        **state,
        "goals": goals,
        "goal_results": goal_results,
        "current_goal_index": current_goal_index + 1,
        "reasoning_trace": reasoning_trace,
        "total_steps": state.get("total_steps", 0) + 1
    }


def response_synthesizer(state: AgentState) -> AgentState:
    """Synthesize final response from all goal results."""
    llm = create_llm()
    goal_results = state.get("goal_results", {})
    
    if not goal_results:
        return {
            **state,
            "draft_response": "I wasn't able to gather the information you requested. Please try again.",
            "should_continue": False
        }
    
    synthesis_prompt = f"""Based on the following information gathered, synthesize a helpful, comprehensive response for the customer.

ORIGINAL QUERY: {state["current_query"]}

INFORMATION GATHERED:
{json.dumps(goal_results, indent=2)}

Provide a well-structured, customer-friendly response that:
1. Directly addresses the customer's question
2. Includes all relevant details from the gathered information
3. Is organized and easy to read
4. Offers additional helpful suggestions if appropriate

Do NOT mention internal processes, tools, or agents. Respond as if you naturally know this information.
"""
    
    messages = [
        SystemMessage(content="You are a helpful customer assistant providing a final response."),
        HumanMessage(content=synthesis_prompt)
    ]
    
    response = llm.invoke(messages)
    
    reasoning_trace = state.get("reasoning_trace", [])
    reasoning_trace.append({
        "step": len(reasoning_trace) + 1,
        "type": "synthesis",
        "thought": "Synthesizing final response from gathered information",
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        **state,
        "draft_response": response.content,
        "reasoning_trace": reasoning_trace,
        "total_steps": state.get("total_steps", 0) + 1
    }


def self_reflector(state: AgentState) -> AgentState:
    """Self-reflection node - Critique and improve the response."""
    llm = create_llm()
    draft_response = state.get("draft_response", "")
    reflection_count = state.get("reflection_count", 0)
    
    # Limit reflections to prevent infinite loops
    if reflection_count >= 2:
        return {
            **state,
            "final_response": draft_response,
            "should_continue": False
        }
    
    reflection_prompt = f"""Critique the following response and suggest improvements if needed.

ORIGINAL QUERY: {state["current_query"]}

DRAFT RESPONSE:
{draft_response}

Evaluate the response on these criteria (score 1-5 each):
1. Completeness - Does it fully answer the question?
2. Accuracy - Is the information correct?
3. Clarity - Is it easy to understand?
4. Helpfulness - Does it provide actionable information?
5. Tone - Is it professional and friendly?

If the average score is 4 or higher, respond with:
APPROVED: [The response is good]

If improvements are needed, respond with:
CRITIQUE: [Specific issues]
IMPROVED_RESPONSE: [The improved response]
"""
    
    messages = [
        SystemMessage(content="You are a quality reviewer improving customer responses."),
        HumanMessage(content=reflection_prompt)
    ]
    
    response = llm.invoke(messages)
    response_text = response.content
    
    reasoning_trace = state.get("reasoning_trace", [])
    critiques = state.get("critiques", [])
    
    if "APPROVED" in response_text:
        # Response is good
        reasoning_trace.append({
            "step": len(reasoning_trace) + 1,
            "type": "reflection",
            "thought": "Response approved after reflection",
            "iteration": reflection_count + 1,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            **state,
            "final_response": draft_response,
            "should_continue": False,
            "quality_score": 4.5,
            "reasoning_trace": reasoning_trace,
            "reflection_count": reflection_count + 1
        }
    else:
        # Extract improved response
        if "IMPROVED_RESPONSE:" in response_text:
            improved = response_text.split("IMPROVED_RESPONSE:")[-1].strip()
        else:
            improved = draft_response
        
        if "CRITIQUE:" in response_text:
            critique = response_text.split("CRITIQUE:")[-1].split("IMPROVED_RESPONSE:")[0].strip()
            critiques.append(critique)
        
        reasoning_trace.append({
            "step": len(reasoning_trace) + 1,
            "type": "reflection",
            "thought": f"Response improved in iteration {reflection_count + 1}",
            "critique": critiques[-1] if critiques else None,
            "timestamp": datetime.now().isoformat()
        })
        
        # After improvement, set both draft and final response
        # Also set should_continue to False to exit reflection loop
        return {
            **state,
            "draft_response": improved,
            "final_response": improved,  # Set final response to improved version
            "critiques": critiques,
            "reasoning_trace": reasoning_trace,
            "reflection_count": reflection_count + 1,
            "should_continue": False,  # Exit reflection loop after improvement
            "total_steps": state.get("total_steps", 0) + 1
        }


def memory_updater(state: AgentState) -> AgentState:
    """Update memory with the conversation."""
    conversation_history = state.get("conversation_history", [])
    
    # Add current exchange to history
    conversation_history.append({
        "role": "user",
        "content": state["current_query"],
        "timestamp": datetime.now().isoformat()
    })
    
    conversation_history.append({
        "role": "assistant",
        "content": state.get("final_response", state.get("draft_response", "")),
        "timestamp": datetime.now().isoformat()
    })
    
    # Update working memory with extracted entities
    working_memory = state.get("working_memory", {})
    
    # Extract entities from goal results
    goal_results = state.get("goal_results", {})
    for goal_id, result in goal_results.items():
        if "product" in goal_id.lower():
            working_memory["last_products_discussed"] = result
        elif "order" in goal_id.lower():
            working_memory["last_order_discussed"] = result
    
    return {
        **state,
        "conversation_history": conversation_history[-20:],  # Keep last 20 turns
        "working_memory": working_memory
    }


# =============================================================================
# Routing Functions
# =============================================================================

def route_by_mode(state: AgentState) -> str:
    """Route based on processing mode."""
    mode = state.get("processing_mode", "standard")
    
    if mode == "simple":
        return "simple_response"
    else:
        return "react_reason"


def should_continue_react(state: AgentState) -> str:
    """Determine if ReAct loop should continue."""
    goals = state.get("goals", [])
    current_goal_index = state.get("current_goal_index", 0)
    
    if current_goal_index < len(goals):
        return "execute_tools"
    else:
        return "synthesize"


def should_continue_reflection(state: AgentState) -> str:
    """Determine if reflection should continue."""
    if state.get("should_continue", True) and state.get("reflection_count", 0) < 2:
        return "reflect"
    else:
        return "update_memory"


# =============================================================================
# Graph Construction
# =============================================================================

def create_langgraph_agent():
    """Create the LangGraph agent workflow."""
    if not LANGGRAPH_AVAILABLE:
        raise ImportError("LangGraph is not available. Install with: pip install langgraph")
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze_query", query_analyzer)
    workflow.add_node("simple_response", simple_responder)
    workflow.add_node("react_reason", react_reasoner)
    workflow.add_node("execute_tools", tool_executor)
    workflow.add_node("synthesize", response_synthesizer)
    workflow.add_node("reflect", self_reflector)
    workflow.add_node("update_memory", memory_updater)
    
    # Add edges
    workflow.add_edge(START, "analyze_query")
    
    # Conditional routing based on query complexity
    workflow.add_conditional_edges(
        "analyze_query",
        route_by_mode,
        {
            "simple_response": "simple_response",
            "react_reason": "react_reason"
        }
    )
    
    # Simple response goes straight to memory update
    workflow.add_edge("simple_response", "update_memory")
    
    # ReAct loop
    workflow.add_conditional_edges(
        "react_reason",
        should_continue_react,
        {
            "execute_tools": "execute_tools",
            "synthesize": "synthesize"
        }
    )
    
    # Tool execution loops back to reasoning
    workflow.add_edge("execute_tools", "react_reason")
    
    # Synthesis goes to reflection
    workflow.add_edge("synthesize", "reflect")
    
    # Reflection loop
    workflow.add_conditional_edges(
        "reflect",
        should_continue_reflection,
        {
            "reflect": "reflect",
            "update_memory": "update_memory"
        }
    )
    
    # Memory update ends the graph
    workflow.add_edge("update_memory", END)
    
    # Compile with memory saver for conversation persistence
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)


# =============================================================================
# Result Classes
# =============================================================================

@dataclass
class LangGraphResult:
    """Result from LangGraph agent execution."""
    query: str
    final_response: str
    processing_mode: str
    reasoning_trace: List[Dict[str, Any]]
    goals: List[Dict[str, Any]]
    goal_results: Dict[str, str]
    critiques: List[str]
    total_steps: int
    total_time_ms: float
    reflection_count: int
    quality_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "final_response": self.final_response,
            "processing_mode": self.processing_mode,
            "reasoning_trace": self.reasoning_trace,
            "goals": self.goals,
            "goal_results": self.goal_results,
            "critiques": self.critiques,
            "metrics": {
                "total_steps": self.total_steps,
                "total_time_ms": self.total_time_ms,
                "reflection_count": self.reflection_count,
                "quality_score": self.quality_score
            }
        }
    
    def format_summary(self) -> str:
        lines = [
            "=" * 60,
            "LANGGRAPH AGENT SUMMARY",
            "=" * 60,
            f"Query: {self.query}",
            f"Mode: {self.processing_mode}",
            f"Time: {self.total_time_ms:.0f}ms",
            "",
            "📊 Metrics:",
            f"   • Total steps: {self.total_steps}",
            f"   • Goals completed: {len([g for g in self.goals if g.get('status') == 'completed'])}",
            f"   • Reflections: {self.reflection_count}",
            f"   • Quality score: {self.quality_score:.1f}/5",
        ]
        
        if self.critiques:
            lines.append(f"   • Critiques addressed: {len(self.critiques)}")
        
        lines.append("")
        lines.append("💭 Reasoning Trace:")
        for step in self.reasoning_trace[:5]:  # Show first 5 steps
            lines.append(f"   {step.get('step', '?')}. [{step.get('type', 'unknown')}] {step.get('thought', '')[:60]}...")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("RESPONSE:")
        lines.append(self.final_response)
        lines.append("=" * 60)
        
        return "\n".join(lines)


# =============================================================================
# Main Agent Class
# =============================================================================

class LangGraphAgent:
    """
    LangGraph-based agentic agent with ReAct, Goal Planning, Reflection, and Memory.
    
    This provides the same interface as the custom AgenticSupervisor but uses
    LangGraph's native graph execution capabilities.
    """
    
    def __init__(
        self,
        verbose: bool = True,
        enable_reflection: bool = True,
        thread_id: str = "default"
    ):
        self.verbose = verbose
        self.enable_reflection = enable_reflection
        self.thread_id = thread_id
        
        # Create the graph
        self.graph = create_langgraph_agent()
        
        # Conversation memory (persisted via LangGraph checkpointer)
        self.conversation_history = []
        self.working_memory = {}
    
    def process(self, query: str) -> LangGraphResult:
        """Process a user query through the LangGraph pipeline."""
        start_time = time.time()
        
        if self.verbose:
            print("\n" + "=" * 60)
            print("🔷 LANGGRAPH AGENT")
            print("=" * 60)
            print(f"📝 Query: {query}")
        
        # Initialize state
        initial_state = {
            "messages": [],
            "current_query": query,
            "goals": [],
            "current_goal_index": 0,
            "goal_results": {},
            "reasoning_trace": [],
            "current_thought": "",
            "draft_response": "",
            "reflection_count": 0,
            "quality_score": 0.0,
            "critiques": [],
            "conversation_history": self.conversation_history,
            "working_memory": self.working_memory,
            "processing_mode": "standard",
            "should_continue": True,
            "final_response": "",
            "total_steps": 0,
            "start_time": start_time
        }
        
        # Run the graph
        config = {"configurable": {"thread_id": self.thread_id}}
        
        try:
            final_state = self.graph.invoke(initial_state, config)
        except Exception as e:
            if self.verbose:
                print(f"Error in LangGraph execution: {e}")
            # Fallback response
            final_state = {
                **initial_state,
                "final_response": f"I encountered an error processing your request. Please try again.",
                "reasoning_trace": [{"step": 1, "type": "error", "thought": str(e)}]
            }
        
        # Update persistent memory
        self.conversation_history = final_state.get("conversation_history", [])
        self.working_memory = final_state.get("working_memory", {})
        
        total_time_ms = (time.time() - start_time) * 1000
        
        result = LangGraphResult(
            query=query,
            final_response=final_state.get("final_response", final_state.get("draft_response", "")),
            processing_mode=final_state.get("processing_mode", "standard"),
            reasoning_trace=final_state.get("reasoning_trace", []),
            goals=final_state.get("goals", []),
            goal_results=final_state.get("goal_results", {}),
            critiques=final_state.get("critiques", []),
            total_steps=final_state.get("total_steps", 0),
            total_time_ms=total_time_ms,
            reflection_count=final_state.get("reflection_count", 0),
            quality_score=final_state.get("quality_score", 0.0)
        )
        
        if self.verbose:
            print(result.format_summary())
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "framework": "LangGraph",
            "memory_stats": {
                "conversation_turns": len(self.conversation_history),
                "working_memory_keys": list(self.working_memory.keys())
            },
            "thread_id": self.thread_id
        }
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.conversation_history = []
        self.working_memory = {}


# =============================================================================
# Convenience Functions
# =============================================================================

def create_langgraph_supervisor(
    verbose: bool = True,
    enable_reflection: bool = True,
    thread_id: str = "default"
) -> LangGraphAgent:
    """Create a LangGraph agent with default configuration."""
    return LangGraphAgent(
        verbose=verbose,
        enable_reflection=enable_reflection,
        thread_id=thread_id
    )


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LangGraph Agent Demo")
    print("=" * 60)
    
    if not LANGGRAPH_AVAILABLE:
        print("LangGraph not installed. Run: pip install langgraph langchain-aws")
        exit(1)
    
    agent = LangGraphAgent(verbose=True)
    
    # Test queries
    queries = [
        "Hello!",
        "Find me a gaming laptop under $1500",
        "I want a laptop under $1500, check if it's in stock, and shipping options to 90210",
    ]
    
    for query in queries:
        print("\n" + "=" * 60)
        result = agent.process(query)
        print("\n")



