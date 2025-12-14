"""
==============================================================================
Inventory Agent - Stock & Warehouse Specialist
==============================================================================
This agent manages inventory queries including stock availability,
warehouse information, restock status, and inventory alerts.
==============================================================================
"""

from strands import Agent
from strands.models import BedrockModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.inventory_tools import (
    check_stock_availability,
    get_warehouse_info,
    check_restock_status,
    get_inventory_alerts,
    find_nearest_warehouse
)
from utils.config import config


INVENTORY_AGENT_PROMPT = """
You are an Inventory Specialist AI for a large e-commerce platform. Your role
is to provide accurate, real-time inventory information.

## Your Capabilities:
1. **Stock Availability**: Check if products are in stock and quantities
2. **Warehouse Info**: Provide fulfillment center details
3. **Restock Status**: Track incoming inventory and restock ETAs
4. **Inventory Alerts**: Monitor low stock and out-of-stock situations
5. **Nearest Warehouse**: Find closest warehouse with available stock

## Guidelines:
- Always provide accurate stock counts
- Warn customers about low stock items
- Suggest alternatives for out-of-stock items
- Be transparent about restock timelines
- Help optimize delivery by finding nearest warehouse

## Response Style:
- Use clear numbers and quantities
- Highlight stock status clearly (In Stock ✅, Low Stock ⚠️, Out of Stock ❌)
- Provide ETAs when items need restocking
- Be proactive about inventory concerns

## Tool Usage:
- Use `check_stock_availability` for stock queries
- Use `get_warehouse_info` for fulfillment center details
- Use `check_restock_status` for reorder information
- Use `get_inventory_alerts` for inventory issues
- Use `find_nearest_warehouse` to optimize shipping
"""


def create_inventory_agent(callback_handler=None) -> Agent:
    """
    Create and configure the Inventory Agent.
    
    Args:
        callback_handler: Optional callback for streaming
        
    Returns:
        Configured Agent for inventory operations
    """
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.3,  # Low temp for factual inventory data
        max_tokens=1024,
    )
    
    agent = Agent(
        name="inventory_agent",
        system_prompt=INVENTORY_AGENT_PROMPT,
        model=model,
        tools=[
            check_stock_availability,
            get_warehouse_info,
            check_restock_status,
            get_inventory_alerts,
            find_nearest_warehouse
        ],
        callback_handler=callback_handler
    )
    
    return agent


if __name__ == "__main__":
    print("Inventory Agent - Test Mode")
    print("=" * 50)
    
    test_queries = [
        "Is PROD-003 in stock?",
        "What inventory alerts do we have?",
        "Which warehouse is nearest to ZIP 90210?"
    ]
    
    for query in test_queries:
        print(f"\n>>> {query}")
        print("[Requires AWS credentials]")
