"""
==============================================================================
Support Agent - Specialist for Customer Support & FAQ
==============================================================================
This agent handles general support queries, FAQ searches, policy questions,
and escalations to human agents.

Capabilities:
    - Search FAQ database
    - Explain store policies
    - Check return eligibility
    - Escalate to human support
==============================================================================
"""

from strands import Agent
from strands.models import BedrockModel

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.support_tools import (
    search_faq,
    get_policy_info,
    check_return_eligibility,
    escalate_to_human
)
from utils.config import config

# =============================================================================
# Agent System Prompt
# =============================================================================

SUPPORT_AGENT_PROMPT = """
You are a Customer Support Specialist AI assistant. Your role is to help 
customers with their questions, explain policies, and resolve issues.

## Your Capabilities:
1. **FAQ Search**: Find answers to common questions
2. **Policy Information**: Explain store policies clearly
3. **Return Eligibility**: Check if orders can be returned
4. **Human Escalation**: Transfer to human agents when needed

## Guidelines:
- Always try to find an answer in FAQ first
- Explain policies clearly and completely
- Be empathetic and understanding
- Know when to escalate to a human agent

## When to Escalate:
- Customer explicitly requests human help
- Billing disputes or payment issues
- Complex complaints requiring judgment
- Customer is very upset after multiple interactions
- Legal or safety concerns

## Response Style:
- Be warm, friendly, and helpful
- Apologize when there are issues
- Provide step-by-step instructions when applicable
- Always confirm if the customer's question was answered

## Tool Usage:
- Use `search_faq` for general questions
- Use `get_policy_info` for specific policy queries
- Use `check_return_eligibility` when customer wants to return something
- Use `escalate_to_human` when escalation is appropriate

## Important:
- Never make promises you can't keep
- If unsure, check the FAQ or escalate
- Always protect customer privacy
"""


def create_support_agent(callback_handler=None) -> Agent:
    """
    Create and configure the Support Agent.
    
    The Support Agent specializes in answering customer questions,
    explaining policies, and handling support requests.
    
    Args:
        callback_handler: Optional callback for streaming responses
        
    Returns:
        Configured Agent instance for support operations
        
    Example:
        >>> agent = create_support_agent()
        >>> response = agent("What is your return policy?")
    """
    # Configure Bedrock model
    model = BedrockModel(
        model_id=config.BEDROCK_MODEL_ID,
        temperature=0.6,
        max_tokens=1024,
    )
    
    # Create agent with support-specific tools
    agent = Agent(
        name="support_agent",
        system_prompt=SUPPORT_AGENT_PROMPT,
        model=model,
        tools=[
            search_faq,
            get_policy_info,
            check_return_eligibility,
            escalate_to_human
        ],
        callback_handler=callback_handler
    )
    
    return agent


# =============================================================================
# Standalone testing
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Support Agent Test")
    print("=" * 60)
    
    try:
        agent = create_support_agent()
        
        # Test queries
        test_queries = [
            "What is your return policy?",
            "Can I return order ORD-1001?",
            "How do I contact customer service?"
        ]
        
        for query in test_queries:
            print(f"\n>>> Query: {query}")
            print("-" * 40)
            print("[Requires AWS credentials to run]")
            
    except Exception as e:
        print(f"Error: {e}")
