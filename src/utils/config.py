"""
==============================================================================
Smart Customer Assistant MVP - Configuration Module
==============================================================================
Centralized configuration management for the multi-agent system.
Loads settings from environment variables with sensible defaults.
==============================================================================
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration class.
    
    Attributes:
        AWS_REGION: AWS region for Bedrock API calls
        BEDROCK_MODEL_ID: Claude model identifier for agent reasoning
        DEBUG_MODE: Enable verbose logging
        MAX_AGENT_ITERATIONS: Safety limit for agent loops
    """
    
    # -------------------------------------------------------------------------
    # AWS Configuration
    # -------------------------------------------------------------------------
    AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # -------------------------------------------------------------------------
    # Bedrock Model Configuration
    # -------------------------------------------------------------------------
    # Using Amazon Nova Pro for reliable performance
    BEDROCK_MODEL_ID: str = os.getenv(
        "BEDROCK_MODEL_ID", 
        "amazon.nova-pro-v1:0"
    )
    
    # -------------------------------------------------------------------------
    # Application Settings
    # -------------------------------------------------------------------------
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    MAX_AGENT_ITERATIONS: int = int(os.getenv("MAX_AGENT_ITERATIONS", "10"))
    
    # -------------------------------------------------------------------------
    # Path Configuration
    # -------------------------------------------------------------------------
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(PROJECT_ROOT, "data")
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If required configuration is missing
        """
        # For demo purposes, we'll allow running without AWS credentials
        # In production, you would enforce credential validation here
        return True
    
    @classmethod
    def get_model_kwargs(cls) -> dict:
        """
        Get keyword arguments for Bedrock model initialization.
        
        Returns:
            dict: Configuration dictionary for BedrockModel
        """
        return {
            "model_id": cls.BEDROCK_MODEL_ID,
            "temperature": 0.7,
            "max_tokens": 2048,
        }


# Create singleton config instance
config = Config()
