"""
==============================================================================
Logistics Agent - Shipping & Delivery Specialist
==============================================================================
This agent handles shipping options, carrier information, tracking,
delivery scheduling, and cost calculations.
==============================================================================
"""

from strands import Agent
from strands.models import BedrockModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.logistics_tools import (
    get_shipping_options,
    get_detailed_tracking,
    get_delivery_slots,
    calculate_shipping_cost,
    get_carrier_info
)
from utils.config import config


LOGISTICS_AGENT_PROMPT = """
You are a Logistics Specialist AI for a large e-commerce platform. Your role
is to help customers with shipping, delivery, and carrier-related questions.

## Your Capabilities:
1. **Shipping Options**: Show available shipping methods with prices
2. **Package Tracking**: Provide detailed tracking information
3. **Delivery Slots**: Help schedule deliveries
4. **Shipping Calculator**: Calculate shipping costs
5. **Carrier Information**: Explain carrier services

## Guidelines:
- Always show multiple shipping options when available
- Highlight Prime benefits for eligible customers
- Provide accurate delivery estimates
- Explain tracking statuses clearly
- Help customers choose cost-effective options

## Response Style:
- Show delivery dates prominently 📅
- Display prices clearly 💵
- Use carrier logos/names 🚚
- Highlight free shipping options
- Explain any delays proactively

## Tool Usage:
- Use `get_shipping_options` for available methods
- Use `get_detailed_tracking` for package status
- Use `get_delivery_slots` for scheduled delivery
- Use `calculate_shipping_cost` for cost breakdown
- Use `get_carrier_info` for carrier details

## Important:
- Be accurate with delivery estimates
- Explain carrier differences honestly
- Warn about potential delays
- Help with lost package situations
"""


def create_logistics_agent(callback_handler=None) -> Agent:
    """
    Create and configure the Logistics Agent.
    
    Args:
        callback_handler: Optional callback for streaming
        
    Returns:
        Configured Agent for logistics operations
    """
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.4,
        max_tokens=1024,
    )
    
    agent = Agent(
        name="logistics_agent",
        system_prompt=LOGISTICS_AGENT_PROMPT,
        model=model,
        tools=[
            get_shipping_options,
            get_detailed_tracking,
            get_delivery_slots,
            calculate_shipping_cost,
            get_carrier_info
        ],
        callback_handler=callback_handler
    )
    
    return agent


if __name__ == "__main__":
    print("Logistics Agent - Test Mode")
    print("=" * 50)
    
    test_queries = [
        "What shipping options are available to 90210?",
        "Track my order ORD-1003",
        "What delivery slots are available?"
    ]
    
    for query in test_queries:
        print(f"\n>>> {query}")
        print("[Requires AWS credentials]")
