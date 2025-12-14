"""
==============================================================================
Pricing Agent - Deals, Discounts & Price Intelligence
==============================================================================
This agent handles all pricing-related queries including active deals,
coupon validation, price history, and discount calculations.
==============================================================================
"""

from strands import Agent
from strands.models import BedrockModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.pricing_tools import (
    get_active_deals,
    validate_coupon,
    get_price_history,
    get_lightning_deals,
    calculate_best_price
)
from utils.config import config


PRICING_AGENT_PROMPT = """
You are a Pricing Specialist AI for a large e-commerce platform. Your role
is to help customers find the best deals and maximize their savings.

## Your Capabilities:
1. **Active Deals**: Find current promotions and sales
2. **Coupon Validation**: Check if coupons are valid and applicable
3. **Price History**: Show historical prices and trends
4. **Lightning Deals**: Time-sensitive flash sales
5. **Best Price Calculation**: Stack discounts for maximum savings

## Guidelines:
- Always help customers save money
- Be transparent about deal terms and conditions
- Warn about expiring deals
- Explain minimum purchase requirements
- Calculate and show total savings

## Response Style:
- Highlight savings prominently 💰
- Use urgency for expiring deals ⏰
- Show original vs discounted prices
- Be enthusiastic about great deals!

## Tool Usage:
- Use `get_active_deals` to find current promotions
- Use `validate_coupon` to check coupon codes
- Use `get_price_history` for price trend analysis
- Use `get_lightning_deals` for time-limited offers
- Use `calculate_best_price` to find optimal discounts

## Important:
- Never promise discounts that don't exist
- Always mention if deals can be stacked
- Clarify eligibility requirements
"""


def create_pricing_agent(callback_handler=None) -> Agent:
    """
    Create and configure the Pricing Agent.
    
    Args:
        callback_handler: Optional callback for streaming
        
    Returns:
        Configured Agent for pricing operations
    """
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.5,
        max_tokens=1024,
    )
    
    agent = Agent(
        name="pricing_agent",
        system_prompt=PRICING_AGENT_PROMPT,
        model=model,
        tools=[
            get_active_deals,
            validate_coupon,
            get_price_history,
            get_lightning_deals,
            calculate_best_price
        ],
        callback_handler=callback_handler
    )
    
    return agent


if __name__ == "__main__":
    print("Pricing Agent - Test Mode")
    print("=" * 50)
    
    test_queries = [
        "What deals do you have on laptops?",
        "Is coupon WELCOME10 valid?",
        "What's the price history for PROD-001?"
    ]
    
    for query in test_queries:
        print(f"\n>>> {query}")
        print("[Requires AWS credentials]")
