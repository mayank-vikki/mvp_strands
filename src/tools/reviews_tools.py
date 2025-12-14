"""
==============================================================================
Reviews Tools - Product Reviews & Sentiment Analysis
==============================================================================
Tools for fetching reviews, analyzing ratings, summarizing sentiment,
and finding helpful reviews.
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


def _load_reviews() -> list:
    """Load reviews data."""
    with open(_get_data_path("reviews.json"), "r") as f:
        data = json.load(f)
        # Handle both formats: list or dict with "reviews" key
        if isinstance(data, list):
            return data
        return data.get("reviews", [])


def _load_products() -> list:
    """Load products data."""
    with open(_get_data_path("products.json"), "r") as f:
        data = json.load(f)
        # Handle both formats: list or dict with "products" key
        if isinstance(data, list):
            return data
        return data.get("products", [])


# =============================================================================
# Reviews Tools
# =============================================================================

@tool
def get_product_reviews(product_id: str, sort_by: str = "helpful") -> str:
    """
    Get reviews for a specific product.
    
    Args:
        product_id: The product ID to get reviews for
        sort_by: Sort order - "helpful", "recent", or "rating"
        
    Returns:
        Formatted list of reviews with ratings and details
    """
    reviews = _load_reviews()
    products = _load_products()
    
    # Get product name
    product_name = None
    for p in products:
        if p["id"] == product_id:
            product_name = p["name"]
            break
    
    # Filter reviews for this product
    product_reviews = [r for r in reviews if r["product_id"] == product_id]
    
    if not product_reviews:
        return f"No reviews found for {product_name or product_id}."
    
    # Sort reviews
    if sort_by == "helpful":
        product_reviews.sort(key=lambda x: x["helpful_votes"], reverse=True)
    elif sort_by == "recent":
        product_reviews.sort(key=lambda x: x["date"], reverse=True)
    elif sort_by == "rating":
        product_reviews.sort(key=lambda x: x["rating"], reverse=True)
    
    output = f"**📝 Reviews for {product_name or product_id}** ({len(product_reviews)} reviews)\n\n"
    
    for review in product_reviews[:5]:  # Top 5 reviews
        stars = "⭐" * review["rating"] + "☆" * (5 - review["rating"])
        verified = "✅ Verified" if review["verified_purchase"] else ""
        
        output += f"**{stars} {review['title']}**\n"
        output += f"*{review['date']}* {verified}\n"
        output += f"{review['text'][:200]}{'...' if len(review['text']) > 200 else ''}\n"
        output += f"👍 {review['helpful_votes']} found this helpful\n\n"
    
    return output


@tool
def get_rating_summary(product_id: str) -> str:
    """
    Get rating summary and breakdown for a product.
    
    Args:
        product_id: The product ID
        
    Returns:
        Rating statistics including average, distribution, and insights
    """
    reviews = _load_reviews()
    products = _load_products()
    
    # Get product
    product = None
    for p in products:
        if p["id"] == product_id:
            product = p
            break
    
    product_reviews = [r for r in reviews if r["product_id"] == product_id]
    
    if not product_reviews:
        return f"No reviews found for {product.get('name', product_id) if product else product_id}."
    
    # Calculate statistics
    total = len(product_reviews)
    avg_rating = sum(r["rating"] for r in product_reviews) / total
    
    # Rating distribution
    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in product_reviews:
        distribution[r["rating"]] += 1
    
    # Sentiment breakdown
    sentiments = {"positive": 0, "mixed": 0, "negative": 0}
    for r in product_reviews:
        sentiments[r.get("sentiment", "positive")] += 1
    
    verified_count = sum(1 for r in product_reviews if r["verified_purchase"])
    
    output = f"""
**📊 Rating Summary: {product.get('name', product_id) if product else product_id}**

⭐ **Average Rating:** {avg_rating:.1f}/5.0
📝 **Total Reviews:** {total}
✅ **Verified Purchases:** {verified_count} ({int(verified_count/total*100)}%)

**Rating Distribution:**
"""
    
    for stars in [5, 4, 3, 2, 1]:
        count = distribution[stars]
        pct = int(count / total * 100)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        output += f"  {stars}⭐ {bar} {pct}% ({count})\n"
    
    output += f"""
**Sentiment Analysis:**
  😊 Positive: {sentiments['positive']} reviews
  😐 Mixed: {sentiments['mixed']} reviews
  😞 Negative: {sentiments['negative']} reviews
"""
    
    # Add recommendation
    if avg_rating >= 4.5:
        output += "\n💡 **Verdict:** Highly recommended! Excellent customer feedback."
    elif avg_rating >= 4.0:
        output += "\n💡 **Verdict:** Well-received with mostly positive reviews."
    elif avg_rating >= 3.0:
        output += "\n💡 **Verdict:** Mixed reviews. Check specific concerns before buying."
    else:
        output += "\n💡 **Verdict:** Below average ratings. Review concerns carefully."
    
    return output


@tool
def search_reviews(product_id: str, keyword: str) -> str:
    """
    Search reviews for specific keywords or topics.
    
    Useful for finding reviews mentioning specific features, issues, or use cases.
    
    Args:
        product_id: The product ID
        keyword: Keyword to search for in reviews
        
    Returns:
        Reviews containing the keyword with relevant excerpts
    """
    reviews = _load_reviews()
    products = _load_products()
    
    product_name = None
    for p in products:
        if p["id"] == product_id:
            product_name = p["name"]
            break
    
    keyword_lower = keyword.lower()
    matching_reviews = []
    
    for r in reviews:
        if r["product_id"] == product_id:
            if (keyword_lower in r["title"].lower() or 
                keyword_lower in r["text"].lower()):
                matching_reviews.append(r)
    
    if not matching_reviews:
        return f"No reviews mentioning '{keyword}' for {product_name or product_id}."
    
    output = f"**🔍 Reviews mentioning '{keyword}' for {product_name}:**\n"
    output += f"Found {len(matching_reviews)} relevant review(s)\n\n"
    
    for review in matching_reviews[:5]:
        stars = "⭐" * review["rating"]
        
        # Highlight keyword in text (simplified)
        text = review["text"]
        
        output += f"**{stars} {review['title']}**\n"
        output += f"_{review['date']}_\n"
        output += f'"{text[:250]}{"..." if len(text) > 250 else ""}"\n\n'
    
    return output


@tool
def get_review_highlights(product_id: str) -> str:
    """
    Get AI-summarized highlights from reviews (pros and cons).
    
    Args:
        product_id: The product ID
        
    Returns:
        Summarized pros and cons from customer reviews
    """
    reviews = _load_reviews()
    products = _load_products()
    
    product = None
    for p in products:
        if p["id"] == product_id:
            product = p
            break
    
    product_reviews = [r for r in reviews if r["product_id"] == product_id]
    
    if not product_reviews:
        return f"No reviews to analyze for {product.get('name', product_id) if product else product_id}."
    
    # Simple keyword-based analysis (in production, use NLP)
    positive_keywords = ["excellent", "great", "love", "perfect", "amazing", "best", "fast", "quality", "comfortable"]
    negative_keywords = ["bad", "poor", "terrible", "slow", "broken", "disappointed", "issue", "problem", "heavy", "hot"]
    
    pros = []
    cons = []
    
    for review in product_reviews:
        text_lower = review["text"].lower()
        
        if review["rating"] >= 4:
            for kw in positive_keywords:
                if kw in text_lower and kw not in [p.lower() for p in pros]:
                    # Extract context
                    if "battery" in text_lower:
                        pros.append("Great battery life")
                    elif "performance" in text_lower or "fast" in text_lower:
                        pros.append("Excellent performance")
                    elif "quality" in text_lower:
                        pros.append("High build quality")
                    elif "comfortable" in text_lower:
                        pros.append("Comfortable to use")
        
        if review["rating"] <= 3:
            for kw in negative_keywords:
                if kw in text_lower:
                    if "battery" in text_lower and "Battery concerns" not in cons:
                        cons.append("Battery concerns mentioned")
                    elif "hot" in text_lower or "warm" in text_lower and "Gets warm" not in cons:
                        cons.append("Gets warm under load")
                    elif "heavy" in text_lower and "Heavier than expected" not in cons:
                        cons.append("Heavier than expected")
    
    # Add some generic insights based on ratings
    avg_rating = sum(r["rating"] for r in product_reviews) / len(product_reviews)
    if avg_rating >= 4.0 and "Overall excellent ratings" not in pros:
        pros.append("Overall excellent customer satisfaction")
    
    output = f"""
**✨ Review Highlights: {product.get('name', product_id) if product else product_id}**

**👍 What Customers Love:**
"""
    
    for pro in pros[:5] or ["Customers generally satisfied"]:
        output += f"  ✓ {pro}\n"
    
    output += "\n**👎 Common Concerns:**\n"
    
    for con in cons[:5] or ["No major concerns reported"]:
        output += f"  ✗ {con}\n"
    
    output += f"\n_Based on analysis of {len(product_reviews)} customer reviews_"
    
    return output


@tool
def compare_product_ratings(product_id_1: str, product_id_2: str) -> str:
    """
    Compare ratings and reviews between two products.
    
    Args:
        product_id_1: First product ID
        product_id_2: Second product ID
        
    Returns:
        Side-by-side comparison of ratings and review sentiment
    """
    reviews = _load_reviews()
    products = _load_products()
    
    # Get products
    p1 = next((p for p in products if p["id"] == product_id_1), None)
    p2 = next((p for p in products if p["id"] == product_id_2), None)
    
    r1 = [r for r in reviews if r["product_id"] == product_id_1]
    r2 = [r for r in reviews if r["product_id"] == product_id_2]
    
    def calc_stats(product_reviews):
        if not product_reviews:
            return {"avg": 0, "count": 0, "positive": 0}
        return {
            "avg": sum(r["rating"] for r in product_reviews) / len(product_reviews),
            "count": len(product_reviews),
            "positive": sum(1 for r in product_reviews if r.get("sentiment") == "positive")
        }
    
    s1 = calc_stats(r1)
    s2 = calc_stats(r2)
    
    output = f"""
**📊 Rating Comparison**

| Metric | {p1['name'][:20] if p1 else product_id_1} | {p2['name'][:20] if p2 else product_id_2} |
|--------|----------|----------|
| Avg Rating | {'⭐' * int(s1['avg'])} {s1['avg']:.1f} | {'⭐' * int(s2['avg'])} {s2['avg']:.1f} |
| Reviews | {s1['count']} | {s2['count']} |
| Positive | {s1['positive']} ({int(s1['positive']/max(s1['count'],1)*100)}%) | {s2['positive']} ({int(s2['positive']/max(s2['count'],1)*100)}%) |

"""
    
    # Winner
    if s1['avg'] > s2['avg'] + 0.3:
        output += f"🏆 **{p1['name'] if p1 else product_id_1}** has significantly better reviews!"
    elif s2['avg'] > s1['avg'] + 0.3:
        output += f"🏆 **{p2['name'] if p2 else product_id_2}** has significantly better reviews!"
    else:
        output += "🤝 Both products have similar customer satisfaction ratings."
    
    return output
