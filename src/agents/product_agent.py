"""
==============================================================================
Product Agent - Specialist for Product Discovery & Recommendations
==============================================================================
This agent handles all product-related queries using the PyTorch
recommendation model and product search tools.

Capabilities:
    - Search products by keywords
    - Provide AI-powered recommendations
    - Compare products
    - Get detailed product information
==============================================================================
"""

from strands import Agent
from strands.models import BedrockModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.product_tools import (
    search_products,
    get_recommendations,
    compare_products,
    get_product_details
)
from utils.config import config

# =============================================================================
# Agent System Prompt
# =============================================================================

PRODUCT_AGENT_PROMPT = """
You are a Product Discovery Specialist AI assistant. Your role is to help 
customers find the perfect products for their needs.

## Your Capabilities:
1. **Search Products**: Find products matching customer descriptions
2. **AI Recommendations**: Use the PyTorch model to suggest relevant products
3. **Compare Products**: Help customers compare multiple options
4. **Product Details**: Provide comprehensive product information

## Guidelines:
- Always understand what the customer is looking for before recommending
- Consider budget constraints when mentioned
- Highlight key features relevant to customer needs
- If asked about gaming, focus on performance specs
- If asked about work/productivity, focus on reliability and features
- Suggest alternatives in different price ranges when appropriate

## Response Style:
- Be helpful and enthusiastic about products
- Present information in a clear, organized manner
- Always mention price and availability
- Offer to compare products if customer seems undecided

## Tool Usage:
- Use `search_products` for keyword-based searches
- Use `get_recommendations` for AI-powered suggestions (uses PyTorch model)
- Use `compare_products` when customer wants to compare options
- Use `get_product_details` for in-depth product information
"""


def create_product_agent(callback_handler=None) -> Agent:
    """
    Create and configure the Product Agent.
    
    The Product Agent specializes in helping customers discover products
    using AI-powered recommendations and search capabilities.
    
    Args:
        callback_handler: Optional callback for streaming responses
        
    Returns:
        Configured Agent instance for product operations
        
    Example:
        >>> agent = create_product_agent()
        >>> response = agent("I need a laptop for video editing")
    """
    # Configure Bedrock model
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.7,
        max_tokens=2048,
    )
    
    # Create agent with product-specific tools
    agent = Agent(
        name="product_agent",
        system_prompt=PRODUCT_AGENT_PROMPT,
        model=model,
        tools=[
            search_products,
            get_recommendations,
            compare_products,
            get_product_details
        ],
        callback_handler=callback_handler
    )
    
    return agent


# =============================================================================
# Standalone testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Product Agent Test")
    print("=" * 60)
    
    # Note: Requires AWS credentials to be configured
    try:
        agent = create_product_agent()
        
        # Test query
        test_queries = [
            "I need a laptop for gaming under $2000",
            "What headphones do you recommend?",
            "Compare gaming laptops"
        ]
        
        for query in test_queries:
            print(f"\n>>> Query: {query}")
            print("-" * 40)
            # Uncomment to test (requires AWS credentials):
            # response = agent(query)
            # print(response)
            print("[Requires AWS credentials to run]")
            
    except Exception as e:
        print(f"Error: {e}")
