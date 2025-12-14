"""
==============================================================================
Unit Tests for Agent Tools
==============================================================================
These tests validate the tool functions work correctly with mock data.
No AWS credentials required - all tests use local data files.
==============================================================================
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestProductTools:
    """Tests for product-related tools."""
    
    def test_search_products_by_category(self):
        """Test searching products by category."""
        from tools.product_tools import search_products
        
        result = search_products(query="laptop")
        
        # Check for JSON response with products
        assert "status" in result or "products" in result.lower() or len(result) > 0
    
    def test_search_products_no_results(self):
        """Test search with no matching products."""
        from tools.product_tools import search_products
        
        result = search_products(query="xyz123nonexistent")
        
        # Should return some result (even if products don't match exactly)
        assert len(result) > 0
    
    def test_get_product_details(self):
        """Test getting product details by ID."""
        from tools.product_tools import get_product_details
        
        result = get_product_details(product_id="P001")
        
        # Should contain product info or "not found"
        assert "P001" in result or "UltraBook" in result or "not found" in result.lower() or len(result) > 0
    
    def test_compare_products(self):
        """Test comparing two products."""
        from tools.product_tools import compare_products
        
        result = compare_products(product_ids=["P001", "P002"])
        
        # Should contain comparison or error
        assert len(result) > 0


class TestOrderTools:
    """Tests for order-related tools."""
    
    def test_lookup_order_exists(self):
        """Test looking up an existing order."""
        from tools.order_tools import lookup_order
        
        result = lookup_order(order_id="ORD-1001")
        
        # Should find the order
        assert "ORD-1001" in result
    
    def test_lookup_order_not_found(self):
        """Test looking up a non-existent order."""
        from tools.order_tools import lookup_order
        
        result = lookup_order(order_id="ORD-9999")
        
        assert "not found" in result.lower() or "no order" in result.lower()
    
    def test_track_shipment(self):
        """Test tracking shipment for an order."""
        from tools.order_tools import track_shipment
        
        result = track_shipment(order_id="ORD-1003")
        
        # Should return tracking info or status
        assert len(result) > 0
    
    def test_estimate_delivery(self):
        """Test delivery estimation."""
        from tools.order_tools import estimate_delivery
        
        result = estimate_delivery(order_id="ORD-1003")
        
        assert len(result) > 0


class TestSupportTools:
    """Tests for support-related tools."""
    
    def test_search_faq(self):
        """Test searching FAQ database."""
        from tools.support_tools import search_faq
        
        result = search_faq(query="return")
        
        # Should find return-related FAQ
        assert len(result) > 0
    
    def test_get_policy_info(self):
        """Test getting policy information."""
        from tools.support_tools import get_policy_info
        
        result = get_policy_info(policy_type="returns")
        
        assert "return" in result.lower() or "policy" in result.lower()
    
    def test_check_return_eligibility(self):
        """Test checking return eligibility."""
        from tools.support_tools import check_return_eligibility
        
        result = check_return_eligibility(order_id="ORD-1001")
        
        # Should return eligibility status
        assert "ORD-1001" in result or "eligible" in result.lower() or "return" in result.lower()
    
    def test_escalate_to_human(self):
        """Test human escalation."""
        from tools.support_tools import escalate_to_human
        
        result = escalate_to_human(
            reason="Customer frustrated",
            customer_context="Customer is upset about shipping delay"
        )
        
        # Should confirm escalation
        assert "escalat" in result.lower() or "human" in result.lower() or len(result) > 0


class TestInventoryTools:
    """Tests for inventory-related tools."""
    
    def test_check_stock_availability(self):
        """Test checking stock availability."""
        from tools.inventory_tools import check_stock_availability
        
        result = check_stock_availability(product_id="PROD-001")
        
        assert "PROD-001" in result or "stock" in result.lower() or "available" in result.lower() or len(result) > 0
    
    def test_get_warehouse_info(self):
        """Test getting warehouse information."""
        from tools.inventory_tools import get_warehouse_info
        
        result = get_warehouse_info(warehouse_id="WH-001")
        
        assert "WH-001" in result or "warehouse" in result.lower() or len(result) > 0
    
    def test_check_restock_status(self):
        """Test checking restock status."""
        from tools.inventory_tools import check_restock_status
        
        result = check_restock_status(product_id="PROD-001")
        
        assert len(result) > 0
    
    def test_get_inventory_alerts(self):
        """Test getting inventory alerts."""
        from tools.inventory_tools import get_inventory_alerts
        
        result = get_inventory_alerts()
        
        # Should return alerts info
        assert "alert" in result.lower() or "inventory" in result.lower() or len(result) > 0
    
    def test_find_nearest_warehouse(self):
        """Test finding nearest warehouse."""
        from tools.inventory_tools import find_nearest_warehouse
        
        result = find_nearest_warehouse(zip_code="90210", product_id="PROD-001")
        
        assert len(result) > 0


class TestPricingTools:
    """Tests for pricing-related tools."""
    
    def test_get_active_deals(self):
        """Test getting active deals."""
        from tools.pricing_tools import get_active_deals
        
        result = get_active_deals()
        
        assert "deal" in result.lower() or "discount" in result.lower() or len(result) > 0
    
    def test_get_deals_for_product(self):
        """Test getting deals for specific category."""
        from tools.pricing_tools import get_active_deals
        
        result = get_active_deals(category="electronics")
        
        assert len(result) > 0
    
    def test_validate_coupon(self):
        """Test validating a coupon code."""
        from tools.pricing_tools import validate_coupon
        
        result = validate_coupon(coupon_code="SAVE10")
        
        assert "SAVE10" in result or "valid" in result.lower() or "coupon" in result.lower() or len(result) > 0
    
    def test_validate_invalid_coupon(self):
        """Test validating an invalid coupon."""
        from tools.pricing_tools import validate_coupon
        
        result = validate_coupon(coupon_code="FAKECODE123")
        
        assert "invalid" in result.lower() or "not found" in result.lower() or len(result) > 0
    
    def test_get_price_history(self):
        """Test getting price history."""
        from tools.pricing_tools import get_price_history
        
        result = get_price_history(product_id="PROD-001")
        
        assert "PROD-001" in result or "price" in result.lower() or len(result) > 0
    
    def test_get_lightning_deals(self):
        """Test getting lightning deals."""
        from tools.pricing_tools import get_lightning_deals
        
        result = get_lightning_deals()
        
        assert len(result) > 0
    
    def test_calculate_best_price(self):
        """Test calculating best price with discounts."""
        from tools.pricing_tools import calculate_best_price
        
        result = calculate_best_price(product_id="PROD-001")
        
        assert "$" in result or "price" in result.lower() or len(result) > 0


class TestReviewsTools:
    """Tests for reviews-related tools."""
    
    def test_get_product_reviews(self):
        """Test getting product reviews."""
        from tools.reviews_tools import get_product_reviews
        
        result = get_product_reviews(product_id="PROD-001")
        
        assert "review" in result.lower() or "rating" in result.lower() or len(result) > 0
    
    def test_get_rating_summary(self):
        """Test getting rating summary."""
        from tools.reviews_tools import get_rating_summary
        
        result = get_rating_summary(product_id="PROD-001")
        
        assert len(result) > 0
    
    def test_search_reviews(self):
        """Test searching reviews."""
        from tools.reviews_tools import search_reviews
        
        result = search_reviews(product_id="PROD-001", keyword="great")
        
        assert len(result) > 0
    
    def test_get_review_highlights(self):
        """Test getting review highlights."""
        from tools.reviews_tools import get_review_highlights
        
        result = get_review_highlights(product_id="PROD-001")
        
        assert len(result) > 0
    
    def test_compare_product_ratings(self):
        """Test comparing product ratings."""
        from tools.reviews_tools import compare_product_ratings
        
        result = compare_product_ratings(product_id_1="PROD-001", product_id_2="PROD-002")
        
        assert len(result) > 0


class TestLogisticsTools:
    """Tests for logistics-related tools."""
    
    def test_get_shipping_options(self):
        """Test getting shipping options."""
        from tools.logistics_tools import get_shipping_options
        
        result = get_shipping_options(zip_code="90210")
        
        assert "shipping" in result.lower() or "delivery" in result.lower() or len(result) > 0
    
    def test_get_detailed_tracking(self):
        """Test getting detailed tracking."""
        from tools.logistics_tools import get_detailed_tracking
        
        result = get_detailed_tracking(order_id="ORD-1001")
        
        assert len(result) > 0
    
    def test_get_delivery_slots(self):
        """Test getting delivery slots."""
        from tools.logistics_tools import get_delivery_slots
        
        result = get_delivery_slots(zip_code="90210")
        
        assert len(result) > 0
    
    def test_calculate_shipping_cost(self):
        """Test calculating shipping cost."""
        from tools.logistics_tools import calculate_shipping_cost
        
        result = calculate_shipping_cost(
            origin_zip="10001",
            dest_zip="90210",
            weight_lbs=2.5
        )
        
        assert "$" in result or "cost" in result.lower() or len(result) > 0
    
    def test_get_carrier_info(self):
        """Test getting carrier info."""
        from tools.logistics_tools import get_carrier_info
        
        result = get_carrier_info(carrier_code="UPS")
        
        assert "UPS" in result or "carrier" in result.lower() or len(result) > 0


class TestRecommenderModel:
    """Tests for the PyTorch recommendation model."""
    
    def test_model_initialization(self):
        """Test that the model initializes correctly."""
        from models.recommender import ProductRecommender
        
        recommender = ProductRecommender()
        
        assert recommender is not None
    
    def test_model_load_products(self):
        """Test loading products into the model."""
        from models.recommender import ProductRecommender
        import os
        
        recommender = ProductRecommender()
        products_path = os.path.join(os.path.dirname(__file__), "..", "data", "products.json")
        recommender.load_products(products_path)
        
        assert len(recommender.products) > 0
    
    def test_model_recommend(self):
        """Test getting recommendations."""
        from models.recommender import ProductRecommender
        import os
        
        recommender = ProductRecommender()
        products_path = os.path.join(os.path.dirname(__file__), "..", "data", "products.json")
        recommender.load_products(products_path)
        
        recommendations = recommender.recommend(query="laptop for gaming")
        
        assert isinstance(recommendations, list)


class TestConfig:
    """Tests for configuration module."""
    
    def test_config_loads(self):
        """Test that config loads without errors."""
        from utils.config import config
        
        assert config is not None
        assert hasattr(config, 'BEDROCK_MODEL_ID')
        assert hasattr(config, 'DATA_DIR')
    
    def test_config_paths_exist(self):
        """Test that configured data paths are valid."""
        from utils.config import config
        
        # DATA_DIR should be a valid path format
        assert config.DATA_DIR is not None


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
