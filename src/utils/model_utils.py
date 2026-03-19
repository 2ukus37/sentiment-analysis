"""
Utility functions for model persistence and loading.
"""
import pickle
import joblib
import os
import logging

logger = logging.getLogger(__name__)


def save_model(model, filepath, use_joblib=True):
    """
    Save a trained model to disk.
    
    Args:
        model: Trained model or vectorizer object
        filepath: Path to save the model
        use_joblib: Use joblib instead of pickle (better for sklearn models)
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        if use_joblib:
            joblib.dump(model, filepath, compress=3)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
        
        logger.info(f"Model saved successfully to {filepath}")
        
        # Log file size
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        logger.info(f"Model file size: {size_mb:.2f} MB")
        
    except Exception as e:
        logger.error(f"Error saving model to {filepath}: {str(e)}")
        raise


def load_model(filepath, use_joblib=True):
    """
    Load a trained model from disk.
    
    Args:
        filepath: Path to the saved model
        use_joblib: Use joblib instead of pickle
        
    Returns:
        Loaded model object
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file not found: {filepath}")
    
    try:
        if use_joblib:
            model = joblib.load(filepath)
        else:
            with open(filepath, 'rb') as f:
                model = pickle.load(f)
        
        logger.info(f"Model loaded successfully from {filepath}")
        return model
        
    except Exception as e:
        logger.error(f"Error loading model from {filepath}: {str(e)}")
        raise
