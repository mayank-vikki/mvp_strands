"""
==============================================================================
Reviews Agent - Customer Reviews & Sentiment Analysis
==============================================================================
This agent handles product reviews, ratings, sentiment analysis,
and review-based recommendations.
==============================================================================
"""

from strands import Agent
from strands.models import BedrockModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.reviews_tools import (
    get_product_reviews,
    get_rating_summary,
    search_reviews,
    get_review_highlights,
    compare_product_ratings
)
from utils.config import config


REVIEWS_AGENT_PROMPT = """
You are a Reviews Analyst AI for a large e-commerce platform. Your role
is to help customers make informed decisions using customer reviews.

## Your Capabilities:
1. **Product Reviews**: Fetch and present customer reviews
2. **Rating Summary**: Provide rating statistics and breakdowns
3. **Review Search**: Find reviews mentioning specific topics
4. **Review Highlights**: Summarize pros and cons from reviews
5. **Rating Comparison**: Compare reviews between products

## Guidelines:
- Present balanced view (both pros and cons)
- Prioritize verified purchase reviews
- Highlight patterns in customer feedback
- Use sentiment analysis to summarize opinions
- Help customers find relevant review content

## Response Style:
- Use star ratings visually ⭐⭐⭐⭐⭐
- Quote relevant excerpts from reviews
- Summarize key themes
- Be objective and unbiased

## Tool Usage:
- Use `get_product_reviews` for full reviews
- Use `get_rating_summary` for statistics
- Use `search_reviews` for specific concerns
- Use `get_review_highlights` for quick pros/cons
- Use `compare_product_ratings` for comparisons

## Important:
- Don't cherry-pick only positive reviews
- Acknowledge common complaints
- Provide context for low ratings
"""


def create_reviews_agent(callback_handler=None) -> Agent:
    """
    Create and configure the Reviews Agent.
    
    Args:
        callback_handler: Optional callback for streaming
        
    Returns:
        Configured Agent for review operations
    """
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.4,
        max_tokens=1500,
    )
    
    agent = Agent(
        name="reviews_agent",
        system_prompt=REVIEWS_AGENT_PROMPT,
        model=model,
        tools=[
            get_product_reviews,
            get_rating_summary,
            search_reviews,
            get_review_highlights,
            compare_product_ratings
        ],
        callback_handler=callback_handler
    )
    
    return agent


if __name__ == "__main__":
    print("Reviews Agent - Test Mode")
    print("=" * 50)
    
    test_queries = [
        "What do customers say about PROD-001?",
        "Show me reviews mentioning battery life for PROD-003",
        "Compare ratings of PROD-001 and PROD-003"
    ]
    
    for query in test_queries:
        print(f"\n>>> {query}")
        print("[Requires AWS credentials]")
