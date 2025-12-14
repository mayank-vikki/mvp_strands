"""
==============================================================================
Models Package - Smart Customer Assistant MVP
==============================================================================
Contains:
    - PyTorch models for product recommendation and similarity search
    - Pydantic models for structured agent responses
==============================================================================
"""

from .recommender import (
    ProductRecommender,
    ProductEmbeddingModel,
    get_recommender,
    recommend_products
)

from .response_models import (
    # Enums
    OrderStatus,
    StockStatus,
    ShippingMethod,
    AgentType,
    OrchestrationPattern,
    
    # Base
    BaseResponse,
    
    # Product Domain
    Product,
    ProductSpec,
    ProductSearchResponse,
    ProductRecommendation,
    ProductRecommendationResponse,
    
    # Order Domain
    Order,
    OrderItem,
    ShippingInfo,
    OrderLookupResponse,
    OrderTrackingResponse,
    
    # Inventory Domain
    StockInfo,
    WarehouseStock,
    InventoryResponse,
    
    # Pricing Domain
    Discount,
    PriceBreakdown,
    PricingResponse,
    DealResponse,
    
    # Reviews Domain
    Review,
    ReviewSummary,
    ReviewHighlight,
    ReviewsResponse,
    
    # Logistics Domain
    ShippingOption,
    DeliverySlot,
    ShippingResponse,
    TrackingEvent,
    DetailedTrackingResponse,
    
    # Support Domain
    FAQItem,
    PolicyInfo,
    SupportResponse,
    ReturnEligibility,
    ReturnResponse,
    
    # Orchestration
    AgentAction,
    HandoffEvent,
    WorkflowStep,
    OrchestratorResponse,
    
    # Conversation
    ConversationTurn,
    ConversationHistory,
    
    # API
    CustomerQuery,
    CustomerResponse,
    
    # Utilities
    create_error_response,
    create_success_response,
)

__all__ = [
    # Recommender
    "ProductRecommender",
    "ProductEmbeddingModel", 
    "get_recommender",
    "recommend_products",
    
    # Enums
    "OrderStatus",
    "StockStatus",
    "ShippingMethod",
    "AgentType",
    "OrchestrationPattern",
    
    # Response Models
    "BaseResponse",
    "Product",
    "ProductSpec",
    "ProductSearchResponse",
    "ProductRecommendation",
    "ProductRecommendationResponse",
    "Order",
    "OrderItem",
    "ShippingInfo",
    "OrderLookupResponse",
    "OrderTrackingResponse",
    "StockInfo",
    "WarehouseStock",
    "InventoryResponse",
    "Discount",
    "PriceBreakdown",
    "PricingResponse",
    "DealResponse",
    "Review",
    "ReviewSummary",
    "ReviewHighlight",
    "ReviewsResponse",
    "ShippingOption",
    "DeliverySlot",
    "ShippingResponse",
    "TrackingEvent",
    "DetailedTrackingResponse",
    "FAQItem",
    "PolicyInfo",
    "SupportResponse",
    "ReturnEligibility",
    "ReturnResponse",
    "AgentAction",
    "HandoffEvent",
    "WorkflowStep",
    "OrchestratorResponse",
    "ConversationTurn",
    "ConversationHistory",
    "CustomerQuery",
    "CustomerResponse",
    "create_error_response",
    "create_success_response",
]
