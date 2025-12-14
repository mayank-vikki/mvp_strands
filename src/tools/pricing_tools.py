"""
==============================================================================
Pricing Tools - Deals, Discounts, Coupons & Price History
==============================================================================
Tools for finding deals, applying coupons, checking price history,
and calculating discounts.
==============================================================================
"""

import json
import os
from strands import tool
from datetime import datetime
from typing import Optional

# =============================================================================
# Data Loading
# =============================================================================

def _get_data_path(filename: str) -> str:
    """Get absolute path to data file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", "..", "data", filename)


def _load_deals() -> dict:
    """Load deals and pricing data."""
    with open(_get_data_path("deals.json"), "r") as f:
        return json.load(f)


def _load_products() -> list:
    """Load products data."""
    with open(_get_data_path("products.json"), "r") as f:
        data = json.load(f)
        return data.get("products", [])


# =============================================================================
# Pricing Tools
# =============================================================================

@tool
def get_active_deals(category: Optional[str] = None) -> str:
    """
    Get all currently active deals and promotions.
    
    Args:
        category: Optional category to filter (e.g., "Laptops", "Audio")
        
    Returns:
        List of active deals with discount details
    """
    data = _load_deals()
    today = datetime.now().strftime("%Y-%m-%d")
    
    active = []
    for deal in data["active_deals"]:
        if deal["status"] == "active":
            if deal["start_date"] <= today <= deal["end_date"]:
                if category is None or deal.get("category", "").lower() == category.lower():
                    active.append(deal)
    
    if not active:
        return f"No active deals found{' for ' + category if category else ''}."
    
    output = f"**🎉 Active Deals{' - ' + category if category else ''}:**\n\n"
    
    for deal in active:
        # Calculate discount display
        if deal["type"] == "percentage":
            discount_text = f"{deal['discount_value']}% OFF"
        elif deal["type"] == "fixed":
            discount_text = f"${deal['discount_value']} OFF"
        elif deal["type"] == "buy_one_get_one":
            discount_text = f"BOGO {deal['discount_value']}% OFF"
        else:
            discount_text = "Special Offer"
        
        remaining = deal["usage_limit"] - deal["used_count"]
        
        output += f"🏷️ **{deal['name']}**\n"
        output += f"   💰 {discount_text}\n"
        output += f"   📅 Ends: {deal['end_date']}\n"
        output += f"   🎫 Remaining: {remaining} uses left\n"
        if deal.get("min_purchase"):
            output += f"   💵 Min Purchase: ${deal['min_purchase']}\n"
        output += "\n"
    
    return output


@tool
def validate_coupon(coupon_code: str, cart_total: float = 0, category: str = None) -> str:
    """
    Validate a coupon code and show potential savings.
    
    Args:
        coupon_code: The coupon code to validate
        cart_total: Current cart total to calculate savings
        category: Product category in cart
        
    Returns:
        Coupon validity status and discount details
    """
    data = _load_deals()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Find coupon
    coupon = None
    for c in data["coupons"]:
        if c["coupon_code"].upper() == coupon_code.upper():
            coupon = c
            break
    
    if not coupon:
        return f"❌ Coupon code '{coupon_code}' not found. Please check the code and try again."
    
    # Check if expired
    if coupon["status"] == "expired" or coupon["valid_until"] < today:
        return f"❌ Coupon '{coupon_code}' has expired on {coupon['valid_until']}."
    
    # Check if not yet valid
    if coupon["valid_from"] > today:
        return f"⏳ Coupon '{coupon_code}' is not yet valid. It starts on {coupon['valid_from']}."
    
    # Check minimum purchase
    if coupon.get("min_purchase") and cart_total < coupon["min_purchase"]:
        return f"⚠️ Coupon '{coupon_code}' requires minimum purchase of ${coupon['min_purchase']}. Your cart: ${cart_total:.2f}"
    
    # Check category
    applicable_cats = coupon.get("applicable_categories", ["all"])
    if "all" not in applicable_cats and category and category not in applicable_cats:
        return f"⚠️ Coupon '{coupon_code}' is not valid for {category}. Valid for: {', '.join(applicable_cats)}"
    
    # Calculate savings
    if coupon["type"] == "percentage":
        savings = cart_total * (coupon["discount_value"] / 100)
        if coupon.get("max_discount") and savings > coupon["max_discount"]:
            savings = coupon["max_discount"]
        savings_text = f"Save ${savings:.2f} ({coupon['discount_value']}% off)"
    elif coupon["type"] == "fixed":
        savings = coupon["discount_value"]
        savings_text = f"Save ${savings:.2f}"
    elif coupon["type"] == "free_shipping":
        savings_text = "FREE SHIPPING"
    else:
        savings_text = "Special discount applied"
    
    output = f"""
✅ **Coupon Valid: {coupon_code}**

📋 **{coupon['description']}**
💰 **{savings_text}**
📅 Valid until: {coupon['valid_until']}
"""
    
    if coupon.get("usage_limit_per_user"):
        output += f"🔄 Uses per customer: {coupon['usage_limit_per_user']}\n"
    
    if coupon.get("requires_loyalty"):
        output += "⭐ Requires loyalty membership\n"
    
    return output


@tool
def get_price_history(product_id: str) -> str:
    """
    Get historical pricing data for a product.
    
    Shows price trends, lowest price ever, and price predictions.
    
    Args:
        product_id: The product ID to check
        
    Returns:
        Price history with trends and insights
    """
    data = _load_deals()
    products = _load_products()
    
    # Get product name and current price
    product = None
    for p in products:
        if p["id"] == product_id:
            product = p
            break
    
    if not product:
        return f"Product {product_id} not found."
    
    # Find price history
    history = None
    for ph in data.get("price_history", []):
        if ph["product_id"] == product_id:
            history = ph
            break
    
    if not history:
        return f"No price history available for {product['name']}."
    
    current_price = product["price"]
    
    output = f"""
**📈 Price History: {product['name']}**

💵 **Current Price:** ${current_price:,.2f}
📉 **Lowest Ever:** ${history['lowest_price']:,.2f} ({history['lowest_date']})
📊 **Average Price:** ${history['average_price']:,.2f}

**Price Trend:**
"""
    
    for entry in history["history"][-5:]:  # Last 5 entries
        price = entry["price"]
        event = entry.get("event", "")
        event_badge = f" 🏷️ {event}" if event else ""
        
        if price < current_price:
            trend = "🟢"
        elif price > current_price:
            trend = "🔴"
        else:
            trend = "⚪"
        
        output += f"  {trend} {entry['date']}: ${price:,.2f}{event_badge}\n"
    
    # Price insight
    if current_price <= history['lowest_price'] * 1.1:
        output += "\n💡 **Insight:** Current price is near all-time low! Great time to buy."
    elif current_price >= history['average_price'] * 1.1:
        output += "\n💡 **Insight:** Price is above average. Consider waiting for a sale."
    else:
        output += "\n💡 **Insight:** Price is at normal levels."
    
    return output


@tool
def get_lightning_deals() -> str:
    """
    Get active lightning deals (time-limited flash sales).
    
    Returns:
        Current lightning deals with remaining time and quantity
    """
    data = _load_deals()
    products = _load_products()
    product_lookup = {p["id"]: p for p in products}
    
    lightning = data.get("lightning_deals", [])
    active_deals = [d for d in lightning if d["status"] == "active"]
    
    if not active_deals:
        return "⚡ No active lightning deals at the moment. Check back soon!"
    
    output = "**⚡ Lightning Deals - Limited Time!**\n\n"
    
    for deal in active_deals:
        product = product_lookup.get(deal["product_id"], {})
        remaining_qty = deal["quantity_available"] - deal["quantity_claimed"]
        claimed_pct = int((deal["quantity_claimed"] / deal["quantity_available"]) * 100)
        
        output += f"🔥 **{product.get('name', deal['product_id'])}**\n"
        output += f"   ~~${deal['original_price']:.2f}~~ → **${deal['deal_price']:.2f}** ({deal['discount_percentage']}% off)\n"
        output += f"   ⏰ Ends: {deal['end_time']}\n"
        output += f"   📊 {claimed_pct}% claimed ({remaining_qty} left)\n\n"
    
    return output


@tool
def calculate_best_price(product_id: str, coupon_code: str = None) -> str:
    """
    Calculate the best possible price for a product with all applicable discounts.
    
    Args:
        product_id: The product ID
        coupon_code: Optional coupon code to apply
        
    Returns:
        Breakdown of all applicable discounts and final price
    """
    data = _load_deals()
    products = _load_products()
    
    # Get product
    product = None
    for p in products:
        if p["id"] == product_id:
            product = p
            break
    
    if not product:
        return f"Product {product_id} not found."
    
    original_price = product["price"]
    final_price = original_price
    discounts_applied = []
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check for active deals
    for deal in data["active_deals"]:
        if deal["status"] == "active" and product_id in deal.get("product_ids", []):
            if deal["start_date"] <= today <= deal["end_date"]:
                if deal["type"] == "percentage":
                    discount = final_price * (deal["discount_value"] / 100)
                    if deal.get("max_discount"):
                        discount = min(discount, deal["max_discount"])
                    final_price -= discount
                    discounts_applied.append(f"🏷️ {deal['name']}: -${discount:.2f}")
                elif deal["type"] == "fixed":
                    final_price -= deal["discount_value"]
                    discounts_applied.append(f"🏷️ {deal['name']}: -${deal['discount_value']:.2f}")
    
    # Check lightning deals
    for ld in data.get("lightning_deals", []):
        if ld["product_id"] == product_id and ld["status"] == "active":
            lightning_price = ld["deal_price"]
            if lightning_price < final_price:
                savings = final_price - lightning_price
                final_price = lightning_price
                discounts_applied.append(f"⚡ Lightning Deal: -${savings:.2f}")
    
    # Apply coupon if provided
    if coupon_code:
        for coupon in data["coupons"]:
            if coupon["coupon_code"].upper() == coupon_code.upper() and coupon["status"] == "active":
                if coupon["type"] == "percentage":
                    discount = final_price * (coupon["discount_value"] / 100)
                    if coupon.get("max_discount"):
                        discount = min(discount, coupon["max_discount"])
                    final_price -= discount
                    discounts_applied.append(f"🎟️ Coupon {coupon_code}: -${discount:.2f}")
                elif coupon["type"] == "fixed":
                    final_price -= coupon["discount_value"]
                    discounts_applied.append(f"🎟️ Coupon {coupon_code}: -${coupon['discount_value']:.2f}")
    
    total_savings = original_price - final_price
    
    output = f"""
**💰 Best Price Calculation: {product['name']}**

📋 Original Price: ${original_price:,.2f}

**Discounts Applied:**
"""
    
    if discounts_applied:
        for d in discounts_applied:
            output += f"  {d}\n"
    else:
        output += "  (No discounts currently available)\n"
    
    output += f"""
━━━━━━━━━━━━━━━━━━━━━━
✅ **Final Price: ${final_price:,.2f}**
💵 **Total Savings: ${total_savings:,.2f}** ({int((total_savings/original_price)*100)}% off)
"""
    
    return output
