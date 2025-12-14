"""
==============================================================================
Product Tools - Agent Tool Functions for Product Operations
==============================================================================
These tools are designed to be used by the Product Agent to search,
recommend, and compare products using the PyTorch recommendation model.

Tools defined here:
    - search_products: Search products by keyword
    - get_recommendations: Get AI-powered product recommendations  
    - compare_products: Compare multiple products side-by-side
    - get_product_details: Get detailed info about a specific product
==============================================================================
"""

import json
import os
from typing import List, Dict, Optional
from strands import tool

# Import our PyTorch recommender
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.recommender import get_recommender


def _load_products() -> List[Dict]:
    """
    Helper function to load products from JSON file.
    
    Returns:
        List of product dictionaries
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    products_path = os.path.join(project_root, 'data', 'products.json')
    
    with open(products_path, 'r') as f:
        data = json.load(f)
    return data.get('products', [])


@tool
def search_products(
    query: str,
    category: Optional[str] = None,
    max_price: Optional[float] = None
) -> str:
    """
    Search for products based on a text query with optional filters.
    
    Use this tool when a customer is looking for products by describing
    what they need. The search uses AI-powered similarity matching.
    
    Args:
        query: The search query describing what the customer wants
               Examples: "gaming laptop", "wireless headphones", "budget laptop"
        category: Optional category filter (e.g., "Laptops", "Audio", "Accessories")
        max_price: Optional maximum price filter in dollars
        
    Returns:
        JSON string containing matching products with details and relevance scores
        
    Example:
        >>> search_products("gaming laptop", max_price=2000)
        Returns laptops suitable for gaming under $2000
    """
    try:
        recommender = get_recommender()
        results = recommender.recommend(
            query=query,
            top_k=5,
            category_filter=category,
            max_price=max_price
        )
        
        if not results:
            return json.dumps({
                "status": "no_results",
                "message": f"No products found matching '{query}'",
                "suggestions": ["Try broader search terms", "Remove filters"]
            })
        
        # Format results for agent
        formatted_results = []
        for product in results:
            formatted_results.append({
                "id": product.get("id"),
                "name": product.get("name"),
                "category": product.get("category"),
                "price": product.get("price"),
                "description": product.get("description"),
                "rating": product.get("rating"),
                "stock": product.get("stock"),
                "relevance_score": product.get("similarity_score", 0)
            })
            
        return json.dumps({
            "status": "success",
            "query": query,
            "filters_applied": {
                "category": category,
                "max_price": max_price
            },
            "result_count": len(formatted_results),
            "products": formatted_results
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error searching products: {str(e)}"
        })


@tool
def get_recommendations(
    query: str,
    num_recommendations: int = 3
) -> str:
    """
    Get AI-powered product recommendations using the PyTorch model.
    
    This tool uses a neural network to find the most relevant products
    based on the customer's query. It analyzes product features,
    categories, and tags to find the best matches.
    
    Args:
        query: Description of what the customer is looking for
               Examples: "laptop for video editing", "fitness tracking"
        num_recommendations: Number of products to recommend (default: 3)
        
    Returns:
        JSON string with recommended products and AI confidence scores
        
    Example:
        >>> get_recommendations("laptop for video editing", num_recommendations=3)
        Returns top 3 laptops best suited for video editing
    """
    try:
        recommender = get_recommender()
        results = recommender.recommend(query=query, top_k=num_recommendations)
        
        if not results:
            return json.dumps({
                "status": "no_recommendations",
                "message": "Could not generate recommendations for this query",
                "query": query
            })
        
        # Format with recommendation reasoning
        recommendations = []
        for idx, product in enumerate(results, 1):
            recommendations.append({
                "rank": idx,
                "product_id": product.get("id"),
                "name": product.get("name"),
                "price": product.get("price"),
                "category": product.get("category"),
                "description": product.get("description"),
                "features": product.get("features", []),
                "rating": product.get("rating"),
                "confidence_score": product.get("similarity_score", 0),
                "in_stock": product.get("stock", 0) > 0
            })
            
        return json.dumps({
            "status": "success",
            "query": query,
            "model": "PyTorch ProductRecommender",
            "recommendations": recommendations
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error generating recommendations: {str(e)}"
        })


@tool
def compare_products(product_ids: List[str]) -> str:
    """
    Compare multiple products side-by-side.
    
    Use this tool when a customer wants to compare features, prices,
    or specifications of multiple products to make a decision.
    
    Args:
        product_ids: List of product IDs to compare (2-4 products recommended)
                    Example: ["P001", "P002", "P003"]
        
    Returns:
        JSON string with side-by-side comparison of products
        
    Example:
        >>> compare_products(["P001", "P002"])
        Returns detailed comparison of UltraBook Pro 15 vs Gaming Beast X1
    """
    try:
        products = _load_products()
        
        # Find requested products
        comparison_products = []
        not_found = []
        
        for pid in product_ids:
            found = False
            for product in products:
                if product.get("id") == pid:
                    comparison_products.append(product)
                    found = True
                    break
            if not found:
                not_found.append(pid)
        
        if not comparison_products:
            return json.dumps({
                "status": "error",
                "message": "No valid products found for comparison",
                "invalid_ids": not_found
            })
        
        # Build comparison matrix
        comparison = {
            "status": "success",
            "products_compared": len(comparison_products),
            "comparison": []
        }
        
        for product in comparison_products:
            comparison["comparison"].append({
                "id": product.get("id"),
                "name": product.get("name"),
                "category": product.get("category"),
                "price": product.get("price"),
                "rating": product.get("rating"),
                "features": product.get("features", []),
                "stock_status": "In Stock" if product.get("stock", 0) > 0 else "Out of Stock"
            })
            
        # Add summary
        prices = [p.get("price", 0) for p in comparison_products]
        ratings = [p.get("rating", 0) for p in comparison_products]
        
        comparison["summary"] = {
            "price_range": f"${min(prices)} - ${max(prices)}",
            "highest_rated": max(comparison_products, key=lambda x: x.get("rating", 0)).get("name"),
            "lowest_price": min(comparison_products, key=lambda x: x.get("price", 0)).get("name")
        }
        
        if not_found:
            comparison["warnings"] = f"Products not found: {not_found}"
            
        return json.dumps(comparison, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error comparing products: {str(e)}"
        })


@tool
def get_product_details(product_id: str) -> str:
    """
    Get detailed information about a specific product.
    
    Use this tool when a customer asks about a specific product
    or needs more details about a product found in search results.
    
    Args:
        product_id: The unique product ID (e.g., "P001", "P002")
        
    Returns:
        JSON string with complete product details
        
    Example:
        >>> get_product_details("P001")
        Returns full details for UltraBook Pro 15
    """
    try:
        products = _load_products()
        
        # Find the product
        for product in products:
            if product.get("id") == product_id:
                # Get similar products
                recommender = get_recommender()
                similar = recommender.get_similar_products(product_id, top_k=3)
                
                return json.dumps({
                    "status": "success",
                    "product": {
                        "id": product.get("id"),
                        "name": product.get("name"),
                        "category": product.get("category"),
                        "price": product.get("price"),
                        "description": product.get("description"),
                        "features": product.get("features", []),
                        "tags": product.get("tags", []),
                        "rating": product.get("rating"),
                        "stock": product.get("stock"),
                        "availability": "In Stock" if product.get("stock", 0) > 0 else "Out of Stock"
                    },
                    "similar_products": [
                        {"id": p.get("id"), "name": p.get("name"), "price": p.get("price")}
                        for p in similar
                    ]
                }, indent=2)
        
        return json.dumps({
            "status": "not_found",
            "message": f"Product with ID '{product_id}' not found",
            "suggestion": "Use search_products to find available products"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error getting product details: {str(e)}"
        })


# Export all tools
__all__ = [
    "search_products",
    "get_recommendations", 
    "compare_products",
    "get_product_details"
]
