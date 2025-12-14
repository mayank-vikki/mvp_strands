"""
==============================================================================
Logistics Tools - Shipping, Carriers & Delivery Management
==============================================================================
Tools for calculating shipping costs, tracking packages, finding delivery
slots, and managing shipping options.
==============================================================================
"""

import json
import os
from strands import tool
from datetime import datetime, timedelta
from typing import Optional

# =============================================================================
# Data Loading
# =============================================================================

def _get_data_path(filename: str) -> str:
    """Get absolute path to data file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", "..", "data", filename)


def _load_shipping() -> dict:
    """Load shipping data."""
    with open(_get_data_path("shipping.json"), "r") as f:
        return json.load(f)


# =============================================================================
# Logistics Tools
# =============================================================================

@tool
def get_shipping_options(zip_code: str, weight_lbs: float = 2.0, is_prime: bool = False) -> str:
    """
    Get available shipping options with prices and delivery estimates.
    
    Args:
        zip_code: Destination ZIP code
        weight_lbs: Package weight in pounds (default 2.0)
        is_prime: Whether customer has Prime membership
        
    Returns:
        List of shipping options with prices and delivery times
    """
    data = _load_shipping()
    
    # Determine shipping zone based on ZIP (simplified)
    zip_prefix = zip_code[:3] if len(zip_code) >= 3 else "100"
    
    if zip_prefix.startswith(('0', '1', '2')):
        zone = next(z for z in data["shipping_zones"] if z["zone_id"] == "ZONE-1")
    elif zip_prefix.startswith(('9')):
        if zip_code.startswith(('995', '996', '997', '998', '999')):  # Alaska
            zone = next(z for z in data["shipping_zones"] if z["zone_id"] == "ZONE-4")
        else:
            zone = next(z for z in data["shipping_zones"] if z["zone_id"] == "ZONE-2")
    else:
        zone = next(z for z in data["shipping_zones"] if z["zone_id"] == "ZONE-3")
    
    today = datetime.now()
    output = f"""
**🚚 Shipping Options to {zip_code}**
📍 Zone: {zone['name']} ({zone['description']})

"""
    
    options = []
    for carrier in data["carriers"]:
        for service in carrier["services"]:
            # Skip Prime-only if not Prime
            if service.get("requires_prime") and not is_prime:
                continue
            
            # Calculate price
            price = service["base_price"] + (weight_lbs * service["per_lb_price"]) + zone["surcharge"]
            
            # Prime free shipping
            if service.get("requires_prime") and is_prime and service["base_price"] == 0:
                price = 0
            
            # Calculate delivery date
            min_days = service["delivery_days"]["min"] + (zone["ground_days"] if "Ground" in service["name"] else 0)
            max_days = service["delivery_days"]["max"] + (zone["ground_days"] if "Ground" in service["name"] else 0)
            
            delivery_min = today + timedelta(days=min_days)
            delivery_max = today + timedelta(days=max_days)
            
            options.append({
                "carrier": carrier["name"],
                "service": service["name"],
                "price": price,
                "delivery_min": delivery_min,
                "delivery_max": delivery_max,
                "is_prime": service.get("requires_prime", False)
            })
    
    # Sort by price
    options.sort(key=lambda x: x["price"])
    
    for opt in options:
        price_str = "**FREE**" if opt["price"] == 0 else f"${opt['price']:.2f}"
        prime_badge = " 🌟 Prime" if opt["is_prime"] else ""
        
        if opt["delivery_min"].date() == opt["delivery_max"].date():
            delivery_str = opt["delivery_min"].strftime("%a, %b %d")
        else:
            delivery_str = f"{opt['delivery_min'].strftime('%a, %b %d')} - {opt['delivery_max'].strftime('%a, %b %d')}"
        
        output += f"📦 **{opt['carrier']} - {opt['service']}**{prime_badge}\n"
        output += f"   💵 {price_str} | 📅 {delivery_str}\n\n"
    
    return output


@tool
def get_detailed_tracking(order_id: str) -> str:
    """
    Get detailed tracking information with full event history.
    
    Args:
        order_id: The order ID to track
        
    Returns:
        Detailed tracking timeline with all events
    """
    data = _load_shipping()
    
    events = data.get("tracking_events", {}).get(order_id)
    
    if not events:
        return f"No tracking information found for order {order_id}."
    
    output = f"""
**📦 Detailed Tracking: {order_id}**

**Tracking Timeline:**
"""
    
    for event in events:
        timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        formatted_time = timestamp.strftime("%b %d, %Y at %I:%M %p")
        
        status_emoji = {
            "label_created": "🏷️",
            "picked_up": "📤",
            "in_transit": "🚚",
            "out_for_delivery": "🚛",
            "delivered": "✅",
            "exception": "⚠️"
        }.get(event["status"], "📍")
        
        output += f"\n{status_emoji} **{event['description']}**\n"
        output += f"   📍 {event['location']}\n"
        output += f"   🕐 {formatted_time}\n"
    
    # Current status
    latest = events[-1]
    output += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
    output += f"📊 **Current Status:** {latest['status'].replace('_', ' ').title()}\n"
    output += f"📍 **Last Location:** {latest['location']}"
    
    return output


@tool
def get_delivery_slots(zip_code: str, date: str = None) -> str:
    """
    Get available delivery time slots for scheduled delivery.
    
    Args:
        zip_code: Destination ZIP code
        date: Preferred date (YYYY-MM-DD format) or None for next available
        
    Returns:
        Available delivery slots with times and costs
    """
    data = _load_shipping()
    slots = data.get("delivery_slots", [])
    
    if date:
        filtered_slots = [s for s in slots if s["date"] == date]
    else:
        filtered_slots = slots
    
    available_slots = [s for s in filtered_slots if s["available"]]
    
    if not available_slots:
        return f"No delivery slots available for {zip_code} on {date or 'the selected dates'}."
    
    output = f"**📅 Delivery Slots for {zip_code}:**\n\n"
    
    current_date = None
    for slot in available_slots:
        if slot["date"] != current_date:
            current_date = slot["date"]
            output += f"**{current_date}:**\n"
        
        premium_badge = " ⭐ Premium" if slot["premium"] else ""
        cost_str = f" (+${slot['extra_cost']:.2f})" if slot["extra_cost"] > 0 else " (Free)"
        
        output += f"  🕐 {slot['time_window']}{premium_badge}{cost_str}\n"
    
    output += "\n_Premium slots guarantee delivery in your preferred window._"
    
    return output


@tool
def calculate_shipping_cost(
    origin_zip: str,
    dest_zip: str,
    weight_lbs: float,
    dimensions: str = None,
    carrier: str = None
) -> str:
    """
    Calculate detailed shipping cost breakdown.
    
    Args:
        origin_zip: Origin ZIP code
        dest_zip: Destination ZIP code
        weight_lbs: Package weight in pounds
        dimensions: Package dimensions "LxWxH" in inches (optional)
        carrier: Preferred carrier or None for all options
        
    Returns:
        Detailed cost breakdown by carrier and service
    """
    data = _load_shipping()
    
    # Calculate dimensional weight if dimensions provided
    dim_weight = None
    if dimensions:
        try:
            l, w, h = map(float, dimensions.lower().replace(" ", "").split("x"))
            dim_weight = (l * w * h) / 139  # Standard DIM factor
        except:
            pass
    
    billable_weight = max(weight_lbs, dim_weight or 0)
    
    # Simplified zone calculation
    zone_surcharge = 2.99  # Default national
    
    # Format dimensional weight display
    dim_weight_display = f"{dim_weight:.1f}" if dim_weight else "N/A"
    
    output = f"""
**💰 Shipping Cost Calculator**

📦 **Package Details:**
  • Actual Weight: {weight_lbs} lbs
  • Dimensional Weight: {dim_weight_display} lbs
  • Billable Weight: {billable_weight:.1f} lbs
  • Route: {origin_zip} → {dest_zip}

**Carrier Options:**
"""
    
    carriers_to_show = data["carriers"]
    if carrier:
        carriers_to_show = [c for c in carriers_to_show if c["name"].lower() == carrier.lower()]
    
    for carr in carriers_to_show:
        output += f"\n**{carr['name']}:**\n"
        
        for service in carr["services"]:
            if service.get("requires_prime"):
                continue  # Skip Prime-only for general calc
            
            base = service["base_price"]
            weight_cost = billable_weight * service["per_lb_price"]
            total = base + weight_cost + zone_surcharge
            
            output += f"  • {service['name']}: ${total:.2f}\n"
            output += f"    (Base ${base:.2f} + Weight ${weight_cost:.2f} + Zone ${zone_surcharge:.2f})\n"
    
    return output


@tool
def get_carrier_info(carrier_code: str = None) -> str:
    """
    Get information about shipping carriers and their services.
    
    Args:
        carrier_code: Carrier code (ups, fedex, usps, amzl) or None for all
        
    Returns:
        Carrier details including services and tracking URL format
    """
    data = _load_shipping()
    
    carriers = data["carriers"]
    if carrier_code:
        carriers = [c for c in carriers if c["code"].lower() == carrier_code.lower()]
    
    if not carriers:
        return f"Carrier '{carrier_code}' not found. Available: ups, fedex, usps, amzl"
    
    output = "**🚚 Carrier Information:**\n\n"
    
    for carrier in carriers:
        output += f"**{carrier['name']}** ({carrier['code'].upper()})\n"
        output += f"🔗 Tracking: {carrier['tracking_url_template'].replace('{tracking_number}', 'XXXXX')}\n\n"
        
        output += "Services:\n"
        for service in carrier["services"]:
            days = service["delivery_days"]
            day_str = f"{days['min']}-{days['max']} days" if days['min'] != days['max'] else f"{days['min']} day"
            prime = " (Prime)" if service.get("requires_prime") else ""
            
            output += f"  • **{service['name']}**{prime}\n"
            output += f"    📅 {day_str} | 💵 ${service['base_price']:.2f}+\n"
        
        output += "\n"
    
    return output
