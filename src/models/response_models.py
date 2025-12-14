"""
==============================================================================
Structured Output Models
==============================================================================
Pydantic models for typed, validated responses from agents.

Benefits:
    - Type safety and validation
    - Consistent API responses
    - Easy serialization/deserialization
    - IDE autocompletion support
    - Documentation generation

Usage:
    from models.response_models import ProductResponse, OrderResponse
    
    # Agent returns structured data
    response = ProductResponse(
        product_id="PROD-001",
        name="Gaming Laptop Pro",
        price=1299.99,
        in_stock=True
    )
==============================================================================
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator


# =============================================================================
# Enums for Constrained Values
# =============================================================================

class OrderStatus(str, Enum):
    """Valid order statuses."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class StockStatus(str, Enum):
    """Stock availability status."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    BACKORDERED = "backordered"


class ShippingMethod(str, Enum):
    """Available shipping methods."""
    STANDARD = "standard"
    EXPRESS = "express"
    OVERNIGHT = "overnight"
    SAME_DAY = "same_day"
    PICKUP = "pickup"


class AgentType(str, Enum):
    """Types of specialist agents."""
    PRODUCT = "product"
    ORDER = "order"
    SUPPORT = "support"
    INVENTORY = "inventory"
    PRICING = "pricing"
    REVIEWS = "reviews"
    LOGISTICS = "logistics"
    SUPERVISOR = "supervisor"


class OrchestrationPattern(str, Enum):
    """Multi-agent orchestration patterns."""
    AGENTS_AS_TOOLS = "agents_as_tools"
    SWARM = "swarm"
    GRAPH = "graph"
    WORKFLOW = "workflow"


# =============================================================================
# Base Response Model
# =============================================================================

class BaseResponse(BaseModel):
    """Base model for all agent responses."""
    
    success: bool = Field(default=True, description="Whether the operation succeeded")
    message: str = Field(default="", description="Human-readable response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    agent_type: Optional[AgentType] = Field(default=None, description="Agent that generated response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# Product Domain Models
# =============================================================================

class ProductSpec(BaseModel):
    """Product specification details."""
    key: str = Field(..., description="Specification name")
    value: str = Field(..., description="Specification value")


class Product(BaseModel):
    """Product information model."""
    
    product_id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    price: float = Field(..., ge=0, description="Product price")
    description: Optional[str] = Field(default=None, description="Product description")
    specs: List[ProductSpec] = Field(default_factory=list, description="Product specifications")
    image_url: Optional[str] = Field(default=None, description="Product image URL")
    
    @validator('price')
    def round_price(cls, v):
        return round(v, 2)


class ProductSearchResponse(BaseResponse):
    """Response from product search."""
    
    agent_type: AgentType = AgentType.PRODUCT
    query: str = Field(..., description="Original search query")
    products: List[Product] = Field(default_factory=list, description="Found products")
    total_results: int = Field(default=0, description="Total number of results")
    
    @validator('total_results', always=True)
    def set_total(cls, v, values):
        return v or len(values.get('products', []))


class ProductRecommendation(BaseModel):
    """Product recommendation with reasoning."""
    
    product: Product
    score: float = Field(..., ge=0, le=1, description="Recommendation score 0-1")
    reason: str = Field(..., description="Why this product is recommended")


class ProductRecommendationResponse(BaseResponse):
    """Response from product recommendations."""
    
    agent_type: AgentType = AgentType.PRODUCT
    recommendations: List[ProductRecommendation] = Field(
        default_factory=list, 
        description="Recommended products"
    )
    based_on: Optional[str] = Field(default=None, description="What recommendations are based on")


# =============================================================================
# Order Domain Models
# =============================================================================

class OrderItem(BaseModel):
    """Item in an order."""
    
    product_id: str
    product_name: str
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., ge=0)
    total_price: float = Field(..., ge=0)


class ShippingInfo(BaseModel):
    """Shipping information for an order."""
    
    carrier: str
    method: ShippingMethod
    tracking_number: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    shipping_cost: float = Field(default=0, ge=0)
    address_zip: Optional[str] = None


class Order(BaseModel):
    """Order information model."""
    
    order_id: str = Field(..., description="Unique order identifier")
    status: OrderStatus = Field(..., description="Current order status")
    items: List[OrderItem] = Field(default_factory=list, description="Items in order")
    subtotal: float = Field(..., ge=0, description="Order subtotal")
    tax: float = Field(default=0, ge=0, description="Tax amount")
    total: float = Field(..., ge=0, description="Order total")
    shipping: Optional[ShippingInfo] = Field(default=None, description="Shipping details")
    created_at: Optional[datetime] = Field(default=None, description="Order creation time")
    updated_at: Optional[datetime] = Field(default=None, description="Last update time")


class OrderLookupResponse(BaseResponse):
    """Response from order lookup."""
    
    agent_type: AgentType = AgentType.ORDER
    order: Optional[Order] = Field(default=None, description="Order details")
    order_id: str = Field(..., description="Queried order ID")


class OrderTrackingResponse(BaseResponse):
    """Response from order tracking."""
    
    agent_type: AgentType = AgentType.ORDER
    order_id: str
    status: OrderStatus
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    tracking_events: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Inventory Domain Models
# =============================================================================

class WarehouseStock(BaseModel):
    """Stock info for a specific warehouse."""
    
    warehouse_id: str
    warehouse_name: str
    quantity: int = Field(..., ge=0)
    location: Optional[str] = None


class StockInfo(BaseModel):
    """Stock information for a product."""
    
    product_id: str
    status: StockStatus
    total_quantity: int = Field(..., ge=0)
    warehouses: List[WarehouseStock] = Field(default_factory=list)
    restock_date: Optional[datetime] = None
    low_stock_threshold: int = Field(default=10)


class InventoryResponse(BaseResponse):
    """Response from inventory check."""
    
    agent_type: AgentType = AgentType.INVENTORY
    product_id: str
    stock_info: StockInfo
    alternative_products: List[str] = Field(
        default_factory=list, 
        description="Alternative product IDs if out of stock"
    )


# =============================================================================
# Pricing Domain Models
# =============================================================================

class Discount(BaseModel):
    """Discount or promotion details."""
    
    type: str = Field(..., description="Deal type (percentage, fixed, bogo)")
    code: Optional[str] = Field(default=None, description="Coupon/promo code")
    amount: float = Field(..., description="Discount amount")
    description: str = Field(..., description="Discount description")
    valid_until: Optional[datetime] = None


class PriceBreakdown(BaseModel):
    """Detailed price breakdown."""
    
    original_price: float = Field(..., ge=0)
    discounts: List[Discount] = Field(default_factory=list)
    discount_total: float = Field(default=0, ge=0)
    final_price: float = Field(..., ge=0)
    savings_percentage: float = Field(default=0, ge=0, le=100)


class PricingResponse(BaseResponse):
    """Response from pricing query."""
    
    agent_type: AgentType = AgentType.PRICING
    product_id: str
    price_breakdown: PriceBreakdown
    available_coupons: List[str] = Field(default_factory=list)


class DealResponse(BaseResponse):
    """Response from deals query."""
    
    agent_type: AgentType = AgentType.PRICING
    deals: List[Dict[str, Any]] = Field(default_factory=list)
    category: Optional[str] = None
    expires_at: Optional[datetime] = None


# =============================================================================
# Reviews Domain Models
# =============================================================================

class ReviewSummary(BaseModel):
    """Summary of product reviews."""
    
    product_id: str
    average_rating: float = Field(..., ge=0, le=5)
    total_reviews: int = Field(..., ge=0)
    rating_distribution: Dict[int, int] = Field(
        default_factory=dict,
        description="Count of reviews per star rating (1-5)"
    )


class ReviewHighlight(BaseModel):
    """Key highlight from reviews."""
    
    type: str = Field(..., description="positive or negative")
    text: str = Field(..., description="Highlight text")
    frequency: int = Field(default=1, description="How often mentioned")


class Review(BaseModel):
    """Individual review."""
    
    reviewer: str
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    text: str
    date: datetime
    verified_purchase: bool = False
    helpful_votes: int = Field(default=0, ge=0)


class ReviewsResponse(BaseResponse):
    """Response from reviews query."""
    
    agent_type: AgentType = AgentType.REVIEWS
    product_id: str
    summary: ReviewSummary
    highlights: List[ReviewHighlight] = Field(default_factory=list)
    recent_reviews: List[Review] = Field(default_factory=list)


# =============================================================================
# Logistics Domain Models
# =============================================================================

class ShippingOption(BaseModel):
    """Available shipping option."""
    
    method: ShippingMethod
    carrier: str
    cost: float = Field(..., ge=0)
    estimated_days: int = Field(..., ge=0)
    estimated_delivery: Optional[datetime] = None


class DeliverySlot(BaseModel):
    """Available delivery time slot."""
    
    date: datetime
    start_time: str  # e.g., "09:00"
    end_time: str    # e.g., "12:00"
    available: bool = True
    premium: bool = False
    cost: float = Field(default=0, ge=0)


class ShippingResponse(BaseResponse):
    """Response from shipping query."""
    
    agent_type: AgentType = AgentType.LOGISTICS
    destination_zip: str
    options: List[ShippingOption] = Field(default_factory=list)
    delivery_slots: List[DeliverySlot] = Field(default_factory=list)


class TrackingEvent(BaseModel):
    """Shipping tracking event."""
    
    timestamp: datetime
    status: str
    location: Optional[str] = None
    description: str


class DetailedTrackingResponse(BaseResponse):
    """Response from detailed tracking query."""
    
    agent_type: AgentType = AgentType.LOGISTICS
    tracking_number: str
    carrier: str
    status: str
    events: List[TrackingEvent] = Field(default_factory=list)
    estimated_delivery: Optional[datetime] = None


# =============================================================================
# Support Domain Models
# =============================================================================

class FAQItem(BaseModel):
    """FAQ question and answer."""
    
    question: str
    answer: str
    category: str
    relevance_score: float = Field(default=1.0, ge=0, le=1)


class PolicyInfo(BaseModel):
    """Policy information."""
    
    policy_name: str
    summary: str
    full_text: Optional[str] = None
    last_updated: Optional[datetime] = None


class SupportResponse(BaseResponse):
    """Response from support query."""
    
    agent_type: AgentType = AgentType.SUPPORT
    faqs: List[FAQItem] = Field(default_factory=list)
    policies: List[PolicyInfo] = Field(default_factory=list)
    escalation_needed: bool = False
    escalation_reason: Optional[str] = None


class ReturnEligibility(BaseModel):
    """Return eligibility check result."""
    
    eligible: bool
    reason: str
    return_window_days: Optional[int] = None
    return_method: Optional[str] = None
    refund_amount: Optional[float] = None


class ReturnResponse(BaseResponse):
    """Response from return eligibility check."""
    
    agent_type: AgentType = AgentType.SUPPORT
    order_id: str
    eligibility: ReturnEligibility


# =============================================================================
# Multi-Agent Orchestration Models
# =============================================================================

class AgentAction(BaseModel):
    """Action taken by an agent."""
    
    agent: AgentType
    action: str
    timestamp: datetime = Field(default_factory=datetime.now)
    duration_ms: Optional[float] = None
    tools_used: List[str] = Field(default_factory=list)


class HandoffEvent(BaseModel):
    """Agent handoff event in Swarm pattern."""
    
    from_agent: AgentType
    to_agent: AgentType
    reason: str
    context: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class WorkflowStep(BaseModel):
    """Step in a Graph workflow."""
    
    node_id: str
    agent: AgentType
    status: str  # "pending", "executing", "completed", "failed"
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    execution_time_ms: Optional[float] = None


class OrchestratorResponse(BaseResponse):
    """Response from multi-agent orchestration."""
    
    pattern: OrchestrationPattern
    total_agents_used: int = Field(default=0)
    agent_actions: List[AgentAction] = Field(default_factory=list)
    handoffs: List[HandoffEvent] = Field(default_factory=list)
    workflow_steps: List[WorkflowStep] = Field(default_factory=list)
    total_execution_time_ms: float = Field(default=0)
    
    # The synthesized final response
    final_response: str = Field(..., description="Final synthesized response")
    
    # Token usage for cost tracking
    total_tokens: int = Field(default=0)
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)


# =============================================================================
# Conversation Models
# =============================================================================

class ConversationTurn(BaseModel):
    """Single turn in conversation."""
    
    role: str = Field(..., description="user or assistant")
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    agent_type: Optional[AgentType] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationHistory(BaseModel):
    """Full conversation history."""
    
    session_id: str
    turns: List[ConversationTurn] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    discussed_products: List[str] = Field(default_factory=list)
    discussed_orders: List[str] = Field(default_factory=list)


# =============================================================================
# API Request/Response Models
# =============================================================================

class CustomerQuery(BaseModel):
    """Incoming customer query."""
    
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    preferred_pattern: Optional[OrchestrationPattern] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class CustomerResponse(BaseResponse):
    """Final response to customer."""
    
    query: str = Field(..., description="Original query")
    response: str = Field(..., description="Assistant response")
    session_id: Optional[str] = None
    agents_used: List[AgentType] = Field(default_factory=list)
    pattern_used: Optional[OrchestrationPattern] = None
    confidence: float = Field(default=1.0, ge=0, le=1)
    follow_up_suggestions: List[str] = Field(default_factory=list)


# =============================================================================
# Utility Functions
# =============================================================================

def create_error_response(
    error_message: str,
    agent_type: AgentType = None
) -> BaseResponse:
    """Create a standardized error response."""
    return BaseResponse(
        success=False,
        message=error_message,
        agent_type=agent_type,
        metadata={"error": True}
    )


def create_success_response(
    message: str,
    agent_type: AgentType = None,
    **kwargs
) -> BaseResponse:
    """Create a standardized success response."""
    return BaseResponse(
        success=True,
        message=message,
        agent_type=agent_type,
        metadata=kwargs
    )
