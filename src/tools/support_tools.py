"""
==============================================================================
Support Tools - Agent Tool Functions for Customer Support
==============================================================================
These tools are designed to be used by the Support Agent to answer FAQs,
check policies, and handle support escalations.

Tools defined here:
    - search_faq: Search frequently asked questions
    - get_policy_info: Get information about store policies
    - check_return_eligibility: Check if a product/order can be returned
    - escalate_to_human: Flag a conversation for human review
==============================================================================
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Optional
from strands import tool


def _load_faq() -> List[dict]:
    """
    Helper function to load FAQ data from JSON file.
    
    Returns:
        List of FAQ dictionaries
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    faq_path = os.path.join(project_root, 'data', 'faq.json')
    
    with open(faq_path, 'r') as f:
        data = json.load(f)
    return data.get('faqs', [])


def _load_orders() -> List[dict]:
    """
    Helper function to load orders data.
    
    Returns:
        List of order dictionaries
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    orders_path = os.path.join(project_root, 'data', 'orders.json')
    
    with open(orders_path, 'r') as f:
        data = json.load(f)
    return data.get('orders', [])


@tool
def search_faq(query: str, category: Optional[str] = None) -> str:
    """
    Search the FAQ database to find relevant answers.
    
    Use this tool when a customer asks a general question that might
    be covered in our FAQ, such as shipping, returns, payments, etc.
    
    Args:
        query: The customer's question or keywords to search for
               Examples: "return policy", "shipping time", "payment methods"
        category: Optional category filter 
                 Options: "returns", "shipping", "orders", "payment", "warranty", "support"
        
    Returns:
        JSON string with matching FAQ entries and answers
        
    Example:
        >>> search_faq("how do I return a product")
        Returns FAQ entries about the return policy
    """
    try:
        faqs = _load_faq()
        query_words = set(query.lower().split())
        
        # Score each FAQ by keyword match
        scored_faqs = []
        for faq in faqs:
            # Apply category filter if specified
            if category and faq.get("category", "").lower() != category.lower():
                continue
                
            # Calculate relevance score
            score = 0
            faq_keywords = set(faq.get("keywords", []))
            question_words = set(faq.get("question", "").lower().split())
            
            # Match against keywords
            score += len(query_words & faq_keywords) * 2
            # Match against question
            score += len(query_words & question_words)
            
            if score > 0:
                scored_faqs.append((score, faq))
        
        # Sort by score (highest first) and take top 3
        scored_faqs.sort(key=lambda x: x[0], reverse=True)
        top_faqs = scored_faqs[:3]
        
        if not top_faqs:
            return json.dumps({
                "status": "no_matches",
                "query": query,
                "message": "No FAQ entries matched your question",
                "suggestion": "Try rephrasing your question or contact customer support"
            })
        
        # Format results
        results = []
        for score, faq in top_faqs:
            results.append({
                "id": faq.get("id"),
                "question": faq.get("question"),
                "answer": faq.get("answer"),
                "category": faq.get("category"),
                "relevance": "high" if score > 3 else "medium"
            })
            
        return json.dumps({
            "status": "success",
            "query": query,
            "matches_found": len(results),
            "faqs": results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error searching FAQ: {str(e)}"
        })


@tool
def get_policy_info(policy_type: str) -> str:
    """
    Get detailed information about store policies.
    
    Use this tool when a customer asks specifically about our policies
    for returns, shipping, warranty, or other store policies.
    
    Args:
        policy_type: The type of policy to retrieve
                    Options: "return", "shipping", "warranty", "privacy", "price_match"
        
    Returns:
        JSON string with detailed policy information
        
    Example:
        >>> get_policy_info("return")
        Returns complete return policy details
    """
    # Policy definitions (in production, this would come from a database)
    policies = {
        "return": {
            "name": "Return Policy",
            "summary": "30-day hassle-free returns on all products",
            "details": [
                "Items must be returned within 30 days of delivery",
                "Products must be in original packaging and unused condition",
                "Electronics must include all original accessories",
                "Refunds processed within 5-7 business days after receipt",
                "Free return shipping for defective items",
                "Return shipping label provided for all returns"
            ],
            "exceptions": [
                "Opened software cannot be returned",
                "Personalized items are final sale",
                "Items marked 'Final Sale' cannot be returned"
            ],
            "process": "Initiate return through your account dashboard or contact support"
        },
        "shipping": {
            "name": "Shipping Policy",
            "summary": "Free shipping on orders over $50",
            "details": [
                "Standard shipping: 5-7 business days",
                "Express shipping: 2-3 business days ($9.99)",
                "Same-day delivery in select areas for orders before 12 PM",
                "Free standard shipping on orders over $50",
                "Tracking provided for all shipments"
            ],
            "international": "Ships to 50+ countries, 10-15 business days",
            "restrictions": "Some items may have shipping restrictions"
        },
        "warranty": {
            "name": "Warranty Policy",
            "summary": "Minimum 1-year warranty on all electronics",
            "details": [
                "1-year manufacturer warranty standard on all electronics",
                "Extended warranty options available at checkout",
                "2-year extended warranty: +10% of product price",
                "3-year extended warranty: +15% of product price",
                "Warranty covers manufacturing defects only"
            ],
            "not_covered": [
                "Accidental damage",
                "Water damage",
                "Normal wear and tear",
                "Unauthorized modifications"
            ],
            "claim_process": "Contact support with proof of purchase to initiate warranty claim"
        },
        "privacy": {
            "name": "Privacy Policy",
            "summary": "Your data is protected and never sold",
            "details": [
                "We collect only necessary information for orders",
                "Payment information is encrypted and secure",
                "We never sell your personal data to third parties",
                "You can request data deletion at any time",
                "Cookies used to improve shopping experience"
            ],
            "contact": "privacy@store.com for data requests"
        },
        "price_match": {
            "name": "Price Match Policy",
            "summary": "We'll match competitor prices within 14 days",
            "details": [
                "Price match available within 14 days of purchase",
                "Matches Amazon, Best Buy, Walmart prices",
                "Item must be identical (same model, color, specs)",
                "Competitor must have item in stock",
                "Excludes marketplace sellers and auction sites"
            ],
            "how_to_claim": "Contact support with link to competitor's lower price"
        }
    }
    
    policy_type_lower = policy_type.lower().replace("_", "").replace(" ", "")
    
    # Map common variations
    type_mapping = {
        "returns": "return",
        "refund": "return",
        "refunds": "return",
        "ship": "shipping",
        "delivery": "shipping",
        "guarantee": "warranty",
        "protection": "warranty",
        "pricematch": "price_match",
        "matchprice": "price_match"
    }
    
    normalized_type = type_mapping.get(policy_type_lower, policy_type_lower)
    
    if normalized_type in policies:
        policy = policies[normalized_type]
        return json.dumps({
            "status": "success",
            "policy_type": policy_type,
            "policy": policy
        }, indent=2)
    else:
        return json.dumps({
            "status": "not_found",
            "message": f"Policy type '{policy_type}' not found",
            "available_policies": list(policies.keys())
        })


@tool
def check_return_eligibility(order_id: str) -> str:
    """
    Check if an order is eligible for return and calculate the return window.
    
    Use this tool when a customer wants to return a product and needs
    to know if they're still within the return window.
    
    Args:
        order_id: The order ID to check (format: ORD-XXXX)
        
    Returns:
        JSON string with eligibility status, return window, and instructions
        
    Example:
        >>> check_return_eligibility("ORD-1001")
        Returns whether order ORD-1001 can be returned and how
    """
    try:
        orders = _load_orders()
        
        for order in orders:
            if order.get("id") == order_id:
                status = order.get("status")
                delivered_date = order.get("delivered_date")
                
                # Check if order is delivered
                if status != "delivered":
                    return json.dumps({
                        "status": "not_eligible",
                        "order_id": order_id,
                        "reason": f"Order status is '{status}'. Only delivered orders can be returned.",
                        "current_status": status
                    })
                
                if not delivered_date:
                    return json.dumps({
                        "status": "error",
                        "message": "Delivery date not found for this order"
                    })
                
                # Calculate return window
                delivery = datetime.strptime(delivered_date, "%Y-%m-%d")
                return_deadline = delivery + timedelta(days=30)
                today = datetime.now()
                
                days_remaining = (return_deadline - today).days
                
                if days_remaining < 0:
                    return json.dumps({
                        "status": "not_eligible",
                        "order_id": order_id,
                        "reason": "Return window has expired",
                        "delivered_date": delivered_date,
                        "return_deadline": return_deadline.strftime("%Y-%m-%d"),
                        "expired_days_ago": abs(days_remaining),
                        "alternative": "Contact support for possible exceptions or warranty claims"
                    })
                
                return json.dumps({
                    "status": "eligible",
                    "order_id": order_id,
                    "product_name": order.get("product_name"),
                    "delivered_date": delivered_date,
                    "return_deadline": return_deadline.strftime("%Y-%m-%d"),
                    "days_remaining": days_remaining,
                    "refund_amount": order.get("total_price"),
                    "return_instructions": [
                        "Log into your account and go to Orders",
                        "Select this order and click 'Return Item'",
                        "Print the prepaid return label",
                        "Pack item in original packaging",
                        "Drop off at any carrier location"
                    ]
                }, indent=2)
        
        return json.dumps({
            "status": "not_found",
            "message": f"Order '{order_id}' not found in our system"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error checking return eligibility: {str(e)}"
        })


@tool
def escalate_to_human(
    reason: str,
    customer_context: str,
    urgency: str = "normal"
) -> str:
    """
    Escalate the conversation to a human support agent.
    
    Use this tool when:
    - The customer explicitly requests human help
    - The issue is too complex for automated resolution
    - The customer is very upset or frustrated
    - There's a billing/payment dispute
    - Safety or legal concerns arise
    
    Args:
        reason: Brief description of why escalation is needed
        customer_context: Summary of the conversation and customer's issue
        urgency: Priority level - "low", "normal", "high", or "urgent"
        
    Returns:
        JSON string confirming escalation and providing next steps
        
    Example:
        >>> escalate_to_human("Customer disputing charge", "Customer claims...", "high")
        Creates escalation ticket for human review
    """
    # In production, this would create a ticket in your support system
    # For demo, we simulate the escalation
    
    urgency_levels = {
        "low": {"response_time": "24-48 hours", "priority": 1},
        "normal": {"response_time": "12-24 hours", "priority": 2},
        "high": {"response_time": "4-6 hours", "priority": 3},
        "urgent": {"response_time": "1-2 hours", "priority": 4}
    }
    
    urgency_info = urgency_levels.get(urgency.lower(), urgency_levels["normal"])
    
    # Generate mock ticket ID
    ticket_id = f"ESC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return json.dumps({
        "status": "escalated",
        "ticket_id": ticket_id,
        "urgency": urgency,
        "expected_response": urgency_info["response_time"],
        "message_to_customer": (
            f"I've escalated your case to our support team (Ticket: {ticket_id}). "
            f"A human agent will contact you within {urgency_info['response_time']}. "
            "You'll receive an email confirmation shortly."
        ),
        "escalation_details": {
            "reason": reason,
            "context_summary": customer_context,
            "priority": urgency_info["priority"],
            "created_at": datetime.now().isoformat()
        },
        "next_steps": [
            "Customer will receive email confirmation",
            "Human agent will review the case",
            "Customer will be contacted via their preferred channel"
        ]
    }, indent=2)


# Export all tools
__all__ = [
    "search_faq",
    "get_policy_info",
    "check_return_eligibility",
    "escalate_to_human"
]
