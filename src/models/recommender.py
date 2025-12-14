"""
==============================================================================
PyTorch Product Recommendation Model
==============================================================================
A simple neural network-based product recommendation system using embeddings
and cosine similarity for the MVP demonstration.

This model demonstrates:
1. Product embedding generation using a simple MLP
2. Similarity-based product recommendations
3. Query-to-product matching

Note: This is a lightweight demo model. In production, you would use
      pre-trained transformers or more sophisticated architectures.
==============================================================================
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional


class ProductEmbeddingModel(nn.Module):
    """
    A simple neural network for generating product embeddings.
    
    Architecture:
        - Input: One-hot encoded product features
        - Hidden: Linear layers with ReLU activation
        - Output: Dense embedding vector
    
    This model is intentionally simple for demo purposes.
    """
    
    def __init__(self, input_dim: int = 50, hidden_dim: int = 64, embedding_dim: int = 32):
        """
        Initialize the embedding model.
        
        Args:
            input_dim: Dimension of input feature vector
            hidden_dim: Dimension of hidden layer
            embedding_dim: Dimension of output embedding
        """
        super(ProductEmbeddingModel, self).__init__()
        
        # Simple 2-layer MLP for embedding generation
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, embedding_dim)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass to generate embeddings.
        
        Args:
            x: Input feature tensor [batch_size, input_dim]
            
        Returns:
            Normalized embedding tensor [batch_size, embedding_dim]
        """
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        # L2 normalize for cosine similarity
        x = F.normalize(x, p=2, dim=-1)
        return x


class ProductRecommender:
    """
    Product Recommendation System using PyTorch embeddings.
    
    This class provides:
        - Product similarity computation
        - Query-based product search
        - Top-K recommendations
    
    Example Usage:
        >>> recommender = ProductRecommender()
        >>> recommender.load_products('data/products.json')
        >>> results = recommender.recommend("gaming laptop", top_k=3)
    """
    
    def __init__(self, embedding_dim: int = 32):
        """
        Initialize the recommender system.
        
        Args:
            embedding_dim: Dimension of product embeddings
        """
        self.embedding_dim = embedding_dim
        self.model = ProductEmbeddingModel(embedding_dim=embedding_dim)
        self.products: List[Dict] = []
        self.product_embeddings: Optional[torch.Tensor] = None
        self.feature_vocabulary: Dict[str, int] = {}
        
    def load_products(self, products_path: str) -> None:
        """
        Load products from JSON file and generate embeddings.
        
        Args:
            products_path: Path to products.json file
        """
        # Load product data
        with open(products_path, 'r') as f:
            data = json.load(f)
        self.products = data.get('products', [])
        
        # Build feature vocabulary from product attributes
        self._build_vocabulary()
        
        # Generate embeddings for all products
        self._generate_embeddings()
        
    def _build_vocabulary(self) -> None:
        """
        Build a vocabulary mapping from product features to indices.
        
        This creates a simple bag-of-words style feature representation
        from product categories, tags, and features.
        """
        vocab_set = set()
        
        for product in self.products:
            # Add category words
            category = product.get('category', '').lower()
            vocab_set.update(category.split())
            
            # Add tags
            tags = product.get('tags', [])
            vocab_set.update([t.lower() for t in tags])
            
            # Add feature keywords
            features = product.get('features', [])
            for f in features:
                vocab_set.update(f.lower().split())
                
        # Create vocabulary mapping
        self.feature_vocabulary = {word: idx for idx, word in enumerate(sorted(vocab_set))}
        
        # Update model input dimension
        vocab_size = max(len(self.feature_vocabulary), 50)
        self.model = ProductEmbeddingModel(input_dim=vocab_size, embedding_dim=self.embedding_dim)
        
    def _product_to_features(self, product: Dict) -> torch.Tensor:
        """
        Convert a product dictionary to a feature tensor.
        
        Args:
            product: Product dictionary with category, tags, features
            
        Returns:
            Feature tensor [vocab_size]
        """
        vocab_size = len(self.feature_vocabulary)
        features = torch.zeros(vocab_size)
        
        # Extract words from product
        words = []
        words.extend(product.get('category', '').lower().split())
        words.extend([t.lower() for t in product.get('tags', [])])
        for f in product.get('features', []):
            words.extend(f.lower().split())
            
        # Set feature indices
        for word in words:
            if word in self.feature_vocabulary:
                features[self.feature_vocabulary[word]] = 1.0
                
        return features
    
    def _query_to_features(self, query: str) -> torch.Tensor:
        """
        Convert a text query to a feature tensor.
        
        Args:
            query: Search query string
            
        Returns:
            Feature tensor [vocab_size]
        """
        vocab_size = len(self.feature_vocabulary)
        features = torch.zeros(vocab_size)
        
        words = query.lower().split()
        for word in words:
            if word in self.feature_vocabulary:
                features[self.feature_vocabulary[word]] = 1.0
                
        return features
        
    def _generate_embeddings(self) -> None:
        """
        Generate embeddings for all loaded products.
        
        Uses the PyTorch model to create dense embeddings
        that can be compared using cosine similarity.
        """
        if not self.products:
            return
            
        # Convert all products to feature tensors
        feature_tensors = []
        for product in self.products:
            features = self._product_to_features(product)
            feature_tensors.append(features)
            
        # Stack into batch tensor
        batch_features = torch.stack(feature_tensors)
        
        # Generate embeddings (no gradient needed)
        self.model.eval()
        with torch.no_grad():
            self.product_embeddings = self.model(batch_features)
            
    def recommend(
        self, 
        query: str, 
        top_k: int = 5,
        category_filter: Optional[str] = None,
        max_price: Optional[float] = None
    ) -> List[Dict]:
        """
        Get product recommendations based on a text query.
        
        Args:
            query: Search query describing desired product
            top_k: Number of recommendations to return
            category_filter: Optional category to filter by
            max_price: Optional maximum price filter
            
        Returns:
            List of recommended products with similarity scores
            
        Example:
            >>> results = recommender.recommend("gaming laptop under 2000", top_k=3)
            >>> for r in results:
            ...     print(f"{r['name']}: {r['similarity_score']:.2f}")
        """
        if self.product_embeddings is None:
            return []
            
        # Convert query to features and embedding
        query_features = self._query_to_features(query).unsqueeze(0)
        
        self.model.eval()
        with torch.no_grad():
            query_embedding = self.model(query_features)
            
        # Compute cosine similarity with all products
        similarities = torch.mm(query_embedding, self.product_embeddings.t()).squeeze()
        
        # Get top-k indices
        scores, indices = torch.topk(similarities, min(top_k * 2, len(self.products)))
        
        # Build results with filtering
        results = []
        for score, idx in zip(scores.tolist(), indices.tolist()):
            product = self.products[idx].copy()
            
            # Apply filters
            if category_filter and product.get('category', '').lower() != category_filter.lower():
                continue
            if max_price and product.get('price', 0) > max_price:
                continue
                
            # Add similarity score
            product['similarity_score'] = round(score, 3)
            results.append(product)
            
            if len(results) >= top_k:
                break
                
        return results
    
    def get_similar_products(self, product_id: str, top_k: int = 5) -> List[Dict]:
        """
        Find products similar to a given product.
        
        Args:
            product_id: ID of the reference product
            top_k: Number of similar products to return
            
        Returns:
            List of similar products with similarity scores
        """
        if self.product_embeddings is None:
            return []
            
        # Find product index
        product_idx = None
        for idx, p in enumerate(self.products):
            if p.get('id') == product_id:
                product_idx = idx
                break
                
        if product_idx is None:
            return []
            
        # Get product embedding
        product_embedding = self.product_embeddings[product_idx].unsqueeze(0)
        
        # Compute similarities
        similarities = torch.mm(product_embedding, self.product_embeddings.t()).squeeze()
        
        # Get top-k (excluding the product itself)
        scores, indices = torch.topk(similarities, top_k + 1)
        
        results = []
        for score, idx in zip(scores.tolist(), indices.tolist()):
            if idx == product_idx:  # Skip self
                continue
            product = self.products[idx].copy()
            product['similarity_score'] = round(score, 3)
            results.append(product)
            
            if len(results) >= top_k:
                break
                
        return results


# =============================================================================
# Module-level convenience functions
# =============================================================================

# Global recommender instance (lazy loaded)
_recommender: Optional[ProductRecommender] = None


def get_recommender() -> ProductRecommender:
    """
    Get or create the global recommender instance.
    
    Returns:
        Initialized ProductRecommender instance
    """
    global _recommender
    
    if _recommender is None:
        _recommender = ProductRecommender()
        
        # Determine data path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        products_path = os.path.join(project_root, 'data', 'products.json')
        
        if os.path.exists(products_path):
            _recommender.load_products(products_path)
            
    return _recommender


def recommend_products(query: str, top_k: int = 5, **filters) -> List[Dict]:
    """
    Convenience function for getting product recommendations.
    
    Args:
        query: Search query
        top_k: Number of results
        **filters: Additional filters (category_filter, max_price)
        
    Returns:
        List of recommended products
    """
    recommender = get_recommender()
    return recommender.recommend(query, top_k=top_k, **filters)


# =============================================================================
# Demo / Testing
# =============================================================================

if __name__ == "__main__":
    # Simple demonstration
    print("=" * 60)
    print("PyTorch Product Recommender Demo")
    print("=" * 60)
    
    recommender = ProductRecommender()
    
    # Load products
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'data', 'products.json'
    )
    
    if os.path.exists(data_path):
        recommender.load_products(data_path)
        print(f"\nLoaded {len(recommender.products)} products")
        print(f"Vocabulary size: {len(recommender.feature_vocabulary)}")
        print(f"Embedding shape: {recommender.product_embeddings.shape}")
        
        # Test recommendation
        print("\n--- Query: 'gaming laptop' ---")
        results = recommender.recommend("gaming laptop", top_k=3)
        for r in results:
            print(f"  {r['name']}: ${r['price']} (score: {r['similarity_score']})")
            
        print("\n--- Query: 'office productivity' ---")
        results = recommender.recommend("office productivity", top_k=3)
        for r in results:
            print(f"  {r['name']}: ${r['price']} (score: {r['similarity_score']})")
    else:
        print(f"Products file not found: {data_path}")
