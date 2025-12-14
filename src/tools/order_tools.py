"""
==============================================================================
Order Tools - Agent Tool Functions for Order Management
==============================================================================
These tools are designed to be used by the Order Agent to look up orders,
track shipments, and provide delivery estimates.

Tools defined here:
    - lookup_order: Find order by ID
    - track_shipment: Get current shipping status
    - estimate_delivery: Calculate delivery ETA
    - get_order_history: Get customer's order history
==============================================================================
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional
from strands import tool


def _load_orders() -> list:
    """
    Helper function to load orders from JSON file.
    
    Returns:
        List of order dictionaries
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    orders_path = os.path.join(project_root, 'data', 'orders.json')
    
    with open(orders_path, 'r') as f:
        data = json.load(f)
    return data.get('orders', [])


def _get_status_description(status: str) -> str:
    """
    Get human-readable description for order status.
    
    Args:
        status: Order status code
        
    Returns:
        Friendly status description
    """
    status_map = {
        "processing": "Your order is being prepared for shipment",
        "shipped": "Your order has been shipped and is on its way",
        "out_for_delivery": "Your order is out for delivery today!",
        "delivered": "Your order has been delivered",
        "delayed": "Your order is experiencing a delay",
        "cancelled": "This order has been cancelled"
    }
    return status_map.get(status, f"Status: {status}")


@tool
def lookup_order(order_id: str) -> str:
    """
    Look up an order by its order ID.
    
    Use this tool when a customer asks about a specific order
    using their order ID (e.g., "ORD-1001").
    
    Args:
        order_id: The order ID to look up (format: ORD-XXXX)
        
    Returns:
        JSON string with order details including status, items, and shipping info
        
    Example:
        >>> lookup_order("ORD-1001")
        Returns complete order information for order ORD-1001
    """
    try:
        orders = _load_orders()
        
        # Find the order
        for order in orders:
            if order.get("id") == order_id:
                # Build response
                response = {
                    "status": "found",
                    "order": {
                        "order_id": order.get("id"),
                        "customer_name": order.get("customer_name"),
                        "product_name": order.get("product_name"),
                        "quantity": order.get("quantity"),
                        "total_price": order.get("total_price"),
                        "order_status": order.get("status"),
                        "status_description": _get_status_description(order.get("status")),
                        "ordered_date": order.get("ordered_date"),
                        "shipping_address": order.get("shipping_address")
                    }
                }
                
                # Add shipping info if available
                if order.get("tracking_number"):
                    response["order"]["tracking_number"] = order.get("tracking_number")
                if order.get("shipped_date"):
                    response["order"]["shipped_date"] = order.get("shipped_date")
                if order.get("delivered_date"):
                    response["order"]["delivered_date"] = order.get("delivered_date")
                if order.get("estimated_delivery"):
                    response["order"]["estimated_delivery"] = order.get("estimated_delivery")
                    
                # Add delay info if delayed
                if order.get("status") == "delayed":
                    response["order"]["delay_reason"] = order.get("delay_reason", "Unknown")
                    response["order"]["original_delivery"] = order.get("original_delivery")
                    
                # Add cancellation info if cancelled
                if order.get("status") == "cancelled":
                    response["order"]["cancelled_date"] = order.get("cancelled_date")
                    response["order"]["cancellation_reason"] = order.get("cancellation_reason")
                    response["order"]["refund_status"] = order.get("refund_status")
                    
                return json.dumps(response, indent=2)
        
        # Order not found
        return json.dumps({
            "status": "not_found",
            "message": f"Order '{order_id}' was not found in our system",
            "suggestions": [
                "Please check the order ID and try again",
                "Order IDs are in format ORD-XXXX",
                "Contact support if you need help finding your order"
            ]
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error looking up order: {str(e)}"
        })


@tool
def track_shipment(order_id: str) -> str:
    """
    Get real-time tracking information for an order's shipment.
    
    Use this tool when a customer wants to know where their package is
    or wants detailed shipping updates.
    
    Args:
        order_id: The order ID to track (format: ORD-XXXX)
        
    Returns:
        JSON string with tracking details, current location, and delivery status
        
    Example:
        >>> track_shipment("ORD-1002")
        Returns current shipping status and estimated delivery for ORD-1002
    """
    try:
        orders = _load_orders()
        
        for order in orders:
            if order.get("id") == order_id:
                status = order.get("status")
                
                # Check if order can be tracked
                if status in ["processing", "cancelled"]:
                    return json.dumps({
                        "status": "not_trackable",
                        "order_id": order_id,
                        "reason": "Order has not been shipped yet" if status == "processing" 
                                 else "Order was cancelled",
                        "order_status": status
                    })
                
                # Build tracking response
                tracking = {
                    "status": "tracking_available",
                    "order_id": order_id,
                    "tracking_number": order.get("tracking_number"),
                    "carrier": "FastShip Express",  # Mock carrier
                    "current_status": status,
                    "status_description": _get_status_description(status)
                }
                
                # Add timeline
                timeline = []
                if order.get("ordered_date"):
                    timeline.append({
                        "event": "Order Placed",
                        "date": order.get("ordered_date"),
                        "completed": True
                    })
                if order.get("shipped_date"):
                    timeline.append({
                        "event": "Shipped",
                        "date": order.get("shipped_date"),
                        "completed": True
                    })
                if status == "out_for_delivery":
                    timeline.append({
                        "event": "Out for Delivery",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "completed": True
                    })
                if order.get("delivered_date"):
                    timeline.append({
                        "event": "Delivered",
                        "date": order.get("delivered_date"),
                        "completed": True
                    })
                elif order.get("estimated_delivery"):
                    timeline.append({
                        "event": "Expected Delivery",
                        "date": order.get("estimated_delivery"),
                        "completed": False
                    })
                    
                tracking["timeline"] = timeline
                
                # Add delay info if applicable
                if status == "delayed":
                    tracking["delay_info"] = {
                        "reason": order.get("delay_reason"),
                        "original_delivery": order.get("original_delivery"),
                        "new_estimated_delivery": order.get("estimated_delivery")
                    }
                    
                return json.dumps(tracking, indent=2)
        
        return json.dumps({
            "status": "not_found",
            "message": f"No order found with ID '{order_id}'"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error tracking shipment: {str(e)}"
        })


@tool
def estimate_delivery(order_id: str) -> str:
    """
    Get estimated delivery date and time window for an order.
    
    Use this tool when a customer asks "when will my order arrive?"
    or needs to know the expected delivery date.
    
    Args:
        order_id: The order ID to check (format: ORD-XXXX)
        
    Returns:
        JSON string with delivery estimate, time window, and any applicable notes
        
    Example:
        >>> estimate_delivery("ORD-1002")
        Returns "Expected delivery: December 15, 2025 between 9 AM - 5 PM"
    """
    try:
        orders = _load_orders()
        
        for order in orders:
            if order.get("id") == order_id:
                status = order.get("status")
                
                # Handle different statuses
                if status == "delivered":
                    return json.dumps({
                        "status": "delivered",
                        "order_id": order_id,
                        "message": "This order has already been delivered",
                        "delivered_date": order.get("delivered_date")
                    })
                    
                if status == "cancelled":
                    return json.dumps({
                        "status": "cancelled",
                        "order_id": order_id,
                        "message": "This order was cancelled and will not be delivered"
                    })
                    
                if status == "processing":
                    # Estimate based on typical processing time
                    ordered = datetime.strptime(order.get("ordered_date"), "%Y-%m-%d")
                    estimated = ordered + timedelta(days=7)
                    
                    return json.dumps({
                        "status": "estimated",
                        "order_id": order_id,
                        "order_status": "Processing",
                        "estimated_delivery": estimated.strftime("%Y-%m-%d"),
                        "delivery_window": "9 AM - 7 PM",
                        "note": "Estimate may change once order ships"
                    })
                
                # For shipped/delayed/out_for_delivery
                estimate_response = {
                    "status": "estimated",
                    "order_id": order_id,
                    "order_status": status,
                    "estimated_delivery": order.get("estimated_delivery"),
                    "delivery_window": "9 AM - 7 PM"
                }
                
                if status == "out_for_delivery":
                    estimate_response["message"] = "Your package is out for delivery today!"
                    estimate_response["estimated_delivery"] = datetime.now().strftime("%Y-%m-%d")
                    estimate_response["delivery_window"] = "By end of day"
                    
                if status == "delayed":
                    estimate_response["delay_info"] = {
                        "original_date": order.get("original_delivery"),
                        "reason": order.get("delay_reason"),
                        "message": "We apologize for the delay"
                    }
                    
                return json.dumps(estimate_response, indent=2)
        
        return json.dumps({
            "status": "not_found",
            "message": f"Order '{order_id}' not found"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error estimating delivery: {str(e)}"
        })


@tool  
def get_order_history(customer_email: str) -> str:
    """
    Get order history for a customer by their email address.
    
    Use this tool when a customer wants to see all their past orders
    or can't remember a specific order ID.
    
    Args:
        customer_email: Customer's email address
        
    Returns:
        JSON string with list of all orders for this customer
        
    Example:
        >>> get_order_history("john.smith@email.com")
        Returns all orders placed by john.smith@email.com
    """
    try:
        orders = _load_orders()
        
        # Find all orders for this customer
        customer_orders = [
            order for order in orders 
            if order.get("customer_email", "").lower() == customer_email.lower()
        ]
        
        if not customer_orders:
            return json.dumps({
                "status": "no_orders",
                "message": f"No orders found for email '{customer_email}'",
                "suggestion": "Please check the email address or contact support"
            })
        
        # Format order history
        history = []
        for order in customer_orders:
            history.append({
                "order_id": order.get("id"),
                "product_name": order.get("product_name"),
                "total_price": order.get("total_price"),
                "ordered_date": order.get("ordered_date"),
                "status": order.get("status"),
                "status_description": _get_status_description(order.get("status"))
            })
            
        # Sort by date (most recent first)
        history.sort(key=lambda x: x.get("ordered_date", ""), reverse=True)
        
        return json.dumps({
            "status": "success",
            "customer_email": customer_email,
            "total_orders": len(history),
            "orders": history
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error retrieving order history: {str(e)}"
        })


# Export all tools
__all__ = [
    "lookup_order",
    "track_shipment",
    "estimate_delivery",
    "get_order_history"
]
