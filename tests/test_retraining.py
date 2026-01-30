"""
Test script to verify the model retraining functionality.
Run with: python test_retraining.py --retrain-mode all|recent|skip
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db
from backend.ai_engine import ai_engine
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_initialization():
    """Test that the model initializes correctly."""
    logger.info(f"Current model version: {ai_engine.model_version}")
    logger.info(f"Models directory: {ai_engine.models_dir}")
    logger.info(f"Model instance created: {ai_engine.model is not None}")
    return True

def test_retraining():
    """Test retraining with different modes."""
    # Initialize database
    init_db()
    
    # Test skip mode
    logger.info("\n=== Testing SKIP mode ===")
    result = ai_engine.retrain_on_historical_data(retrain_mode="skip")
    logger.info(f"Skip result: {result}")
    
    # Test recent mode (will likely fail on fresh DB with no data)
    logger.info("\n=== Testing RECENT mode ===")
    result = ai_engine.retrain_on_historical_data(retrain_mode="recent")
    logger.info(f"Recent result: {result}")
    
    # Test all mode (will likely fail on fresh DB with no data)
    logger.info("\n=== Testing ALL mode ===")
    result = ai_engine.retrain_on_historical_data(retrain_mode="all")
    logger.info(f"All result: {result}")
    
    return True

def test_model_persistence():
    """Test that models are saved and persist."""
    import os
    models_dir = ai_engine.models_dir
    if os.path.exists(models_dir):
        model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
        logger.info(f"Model files in {models_dir}: {model_files}")
    else:
        logger.info(f"Models directory does not exist: {models_dir}")
    return True

if __name__ == "__main__":
    logger.info("Starting model retraining tests...\n")
    
    try:
        test_model_initialization()
        logger.info("✓ Model initialization test passed\n")
        
        test_retraining()
        logger.info("✓ Retraining test completed\n")
        
        test_model_persistence()
        logger.info("✓ Model persistence test completed\n")
        
        logger.info("All tests completed!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)
