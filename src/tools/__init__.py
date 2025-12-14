"""
==============================================================================
Tools Package - Smart Customer Assistant MVP
==============================================================================
Agent tools for product search, order management, customer support,
inventory management, pricing/deals, reviews, and logistics.
==============================================================================
"""

from .product_tools import (
    search_products,
    get_recommendations,
    compare_products,
    get_product_details
)

from .order_tools import (
    lookup_order,
    track_shipment,
    estimate_delivery,
    get_order_history
)

from .support_tools import (
    search_faq,
    get_policy_info,
    check_return_eligibility,
    escalate_to_human
)

from .inventory_tools import (
    check_stock_availability,
    get_warehouse_info,
    check_restock_status,
    get_inventory_alerts,
    find_nearest_warehouse
)

from .pricing_tools import (
    get_active_deals,
    validate_coupon,
    get_price_history,
    get_lightning_deals,
    calculate_best_price
)

from .reviews_tools import (
    get_product_reviews,
    get_rating_summary,
    search_reviews,
    get_review_highlights,
    compare_product_ratings
)

from .logistics_tools import (
    get_shipping_options,
    get_detailed_tracking,
    get_delivery_slots,
    calculate_shipping_cost,
    get_carrier_info
)

# All available tools grouped by domain
PRODUCT_TOOLS = [search_products, get_recommendations, compare_products, get_product_details]
ORDER_TOOLS = [lookup_order, track_shipment, estimate_delivery, get_order_history]
SUPPORT_TOOLS = [search_faq, get_policy_info, check_return_eligibility, escalate_to_human]
INVENTORY_TOOLS = [check_stock_availability, get_warehouse_info, check_restock_status, get_inventory_alerts, find_nearest_warehouse]
PRICING_TOOLS = [get_active_deals, validate_coupon, get_price_history, get_lightning_deals, calculate_best_price]
REVIEWS_TOOLS = [get_product_reviews, get_rating_summary, search_reviews, get_review_highlights, compare_product_ratings]
LOGISTICS_TOOLS = [get_shipping_options, get_detailed_tracking, get_delivery_slots, calculate_shipping_cost, get_carrier_info]

# All tools combined
ALL_TOOLS = PRODUCT_TOOLS + ORDER_TOOLS + SUPPORT_TOOLS + INVENTORY_TOOLS + PRICING_TOOLS + REVIEWS_TOOLS + LOGISTICS_TOOLS

__all__ = [
    # Product tools
    "search_products",
    "get_recommendations",
    "compare_products",
    "get_product_details",
    # Order tools
    "lookup_order",
    "track_shipment",
    "estimate_delivery",
    "get_order_history",
    # Support tools
    "search_faq",
    "get_policy_info",
    "check_return_eligibility",
    "escalate_to_human",
    # Inventory tools
    "check_stock_availability",
    "get_warehouse_info",
    "check_restock_status",
    "get_inventory_alerts",
    "find_nearest_warehouse",
    # Pricing tools
    "get_active_deals",
    "validate_coupon",
    "get_price_history",
    "get_lightning_deals",
    "calculate_best_price",
    # Reviews tools
    "get_product_reviews",
    "get_rating_summary",
    "search_reviews",
    "get_review_highlights",
    "compare_product_ratings",
    # Logistics tools
    "get_shipping_options",
    "get_detailed_tracking",
    "get_delivery_slots",
    "calculate_shipping_cost",
    "get_carrier_info",
    # Tool groups
    "PRODUCT_TOOLS",
    "ORDER_TOOLS",
    "SUPPORT_TOOLS",
    "INVENTORY_TOOLS",
    "PRICING_TOOLS",
    "REVIEWS_TOOLS",
    "LOGISTICS_TOOLS",
    "ALL_TOOLS"
]
