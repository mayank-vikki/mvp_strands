"""
==============================================================================
Inventory Tools - Stock & Warehouse Management
==============================================================================
Tools for checking inventory levels, stock availability, warehouse info,
and restock status.
==============================================================================
"""

import json
import os
from strands import tool
from typing import Optional

# =============================================================================
# Data Loading
# =============================================================================

def _get_data_path(filename: str) -> str:
    """Get absolute path to data file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", "..", "data", filename)


def _load_inventory() -> dict:
    """Load inventory data from JSON file."""
    with open(_get_data_path("inventory.json"), "r") as f:
        return json.load(f)


def _load_products() -> list:
    """Load products data."""
    with open(_get_data_path("products.json"), "r") as f:
        data = json.load(f)
        return data.get("products", [])


# =============================================================================
# Inventory Tools
# =============================================================================

@tool
def check_stock_availability(product_id: str) -> str:
    """
    Check real-time stock availability for a product.
    
    Returns stock status, available quantity, and warehouse distribution.
    
    Args:
        product_id: The product ID (e.g., "PROD-001")
        
    Returns:
        Detailed stock information including availability and locations
    """
    data = _load_inventory()
    products = _load_products()
    
    # Find product name
    product_name = None
    for p in products:
        if p["id"] == product_id:
            product_name = p["name"]
            break
    
    # Find inventory record
    for inv in data["inventory"]:
        if inv["product_id"] == product_id:
            status_emoji = {
                "in_stock": "✅",
                "low_stock": "⚠️",
                "out_of_stock": "❌"
            }.get(inv["status"], "❓")
            
            output = f"""
**Stock Status for {product_name or product_id}**

{status_emoji} **Status:** {inv['status'].replace('_', ' ').title()}
📦 **Total Stock:** {inv['total_stock']} units
🔒 **Reserved:** {inv['reserved']} units
✅ **Available:** {inv['available']} units

**Warehouse Distribution:**
"""
            for wh_id, qty in inv["warehouse_distribution"].items():
                wh_name = next((w["location"] for w in data["warehouses"] if w["warehouse_id"] == wh_id), wh_id)
                output += f"  • {wh_name}: {qty} units\n"
            
            if inv.get("next_restock_eta"):
                output += f"\n📅 **Next Restock:** {inv['next_restock_eta']}"
            
            if inv.get("backorder_count"):
                output += f"\n⏳ **Backorders Pending:** {inv['backorder_count']}"
            
            return output
    
    return f"❌ No inventory record found for product {product_id}"


@tool
def get_warehouse_info(warehouse_id: Optional[str] = None) -> str:
    """
    Get information about fulfillment centers/warehouses.
    
    Args:
        warehouse_id: Optional specific warehouse ID. If not provided, returns all.
        
    Returns:
        Warehouse details including location and capacity
    """
    data = _load_inventory()
    
    if warehouse_id:
        for wh in data["warehouses"]:
            if wh["warehouse_id"] == warehouse_id:
                utilization_pct = int(wh["current_utilization"] * 100)
                return f"""
**{wh['name']}**
📍 Location: {wh['location']}
🌎 Region: {wh['region'].title()}
📦 Capacity: {wh['capacity']:,} units
📊 Utilization: {utilization_pct}%
"""
        return f"Warehouse {warehouse_id} not found."
    
    # Return all warehouses
    output = "**Fulfillment Centers:**\n\n"
    for wh in data["warehouses"]:
        utilization_pct = int(wh["current_utilization"] * 100)
        output += f"• **{wh['name']}** ({wh['location']})\n"
        output += f"  Capacity: {wh['capacity']:,} | Utilization: {utilization_pct}%\n\n"
    
    return output


@tool
def check_restock_status(product_id: str) -> str:
    """
    Check restock/replenishment status for a product.
    
    Args:
        product_id: The product ID to check
        
    Returns:
        Restock information including ETA if applicable
    """
    data = _load_inventory()
    products = _load_products()
    
    product_name = None
    for p in products:
        if p["id"] == product_id:
            product_name = p["name"]
            break
    
    for inv in data["inventory"]:
        if inv["product_id"] == product_id:
            output = f"""
**Restock Status for {product_name or product_id}**

📊 **Current Stock:** {inv['available']} available
🎯 **Reorder Point:** {inv['reorder_point']} units
📦 **Reorder Quantity:** {inv['reorder_quantity']} units
📅 **Last Restock:** {inv['last_restock']}
"""
            
            if inv['available'] <= inv['reorder_point']:
                output += "\n⚠️ **Alert:** Stock at or below reorder point!"
                if inv.get("next_restock_eta"):
                    output += f"\n📅 **Next Restock ETA:** {inv['next_restock_eta']}"
                else:
                    output += "\n📋 Reorder has been automatically triggered."
            else:
                output += "\n✅ Stock levels healthy - no restock needed."
            
            return output
    
    return f"No inventory record found for {product_id}"


@tool
def get_inventory_alerts() -> str:
    """
    Get current inventory alerts (low stock, out of stock, etc.).
    
    Returns:
        List of active inventory alerts sorted by priority
    """
    data = _load_inventory()
    products = _load_products()
    
    # Create product lookup
    product_lookup = {p["id"]: p["name"] for p in products}
    
    if not data.get("alerts"):
        return "✅ No active inventory alerts."
    
    output = "**🚨 Active Inventory Alerts:**\n\n"
    
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    sorted_alerts = sorted(data["alerts"], key=lambda x: priority_order.get(x["priority"], 99))
    
    for alert in sorted_alerts:
        priority_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }.get(alert["priority"], "⚪")
        
        product_name = product_lookup.get(alert["product_id"], alert["product_id"])
        
        output += f"{priority_emoji} **{alert['type'].replace('_', ' ').title()}**\n"
        output += f"   Product: {product_name}\n"
        output += f"   {alert['message']}\n\n"
    
    return output


@tool
def find_nearest_warehouse(zip_code: str, product_id: str) -> str:
    """
    Find the nearest warehouse with stock for a product.
    
    Args:
        zip_code: Customer's ZIP code
        product_id: Product to check availability for
        
    Returns:
        Nearest warehouse with available stock and estimated shipping
    """
    data = _load_inventory()
    
    # Mock ZIP to region mapping (simplified)
    zip_prefix = zip_code[:3] if len(zip_code) >= 3 else zip_code
    
    # Simplified region detection
    if zip_prefix.startswith(('0', '1', '2')):
        preferred_region = "east"
    elif zip_prefix.startswith(('9', '8')):
        preferred_region = "west"
    elif zip_prefix.startswith(('7', '6')):
        preferred_region = "central"
    else:
        preferred_region = "southeast"
    
    # Find inventory
    inv_record = None
    for inv in data["inventory"]:
        if inv["product_id"] == product_id:
            inv_record = inv
            break
    
    if not inv_record:
        return f"Product {product_id} not found in inventory."
    
    if inv_record["available"] <= 0:
        return f"❌ Product {product_id} is currently out of stock at all warehouses."
    
    # Find best warehouse
    best_warehouse = None
    best_stock = 0
    
    # First try preferred region
    for wh in data["warehouses"]:
        if wh["region"] == preferred_region:
            stock = inv_record["warehouse_distribution"].get(wh["warehouse_id"], 0)
            if stock > best_stock:
                best_warehouse = wh
                best_stock = stock
    
    # If no stock in preferred region, find any with stock
    if not best_warehouse or best_stock == 0:
        for wh in data["warehouses"]:
            stock = inv_record["warehouse_distribution"].get(wh["warehouse_id"], 0)
            if stock > best_stock:
                best_warehouse = wh
                best_stock = stock
    
    if best_warehouse and best_stock > 0:
        est_days = 2 if best_warehouse["region"] == preferred_region else 4
        return f"""
**Nearest Fulfillment Center with Stock:**

🏭 **{best_warehouse['name']}**
📍 Location: {best_warehouse['location']}
📦 Available: {best_stock} units
🚚 Estimated Delivery: {est_days}-{est_days + 2} business days

Ships from {best_warehouse['region'].title()} region to ZIP {zip_code}.
"""
    
    return "Unable to find warehouse with available stock."
