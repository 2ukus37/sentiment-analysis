"""
PredictionService: Unified prediction router for cyberbullying detection.
Routes inputs to appropriate models (Twitter SVM or Wikipedia RF) based on source type.
"""
import logging
import time
from typing import Dict, Tuple, Optional
import numpy as np

from src.utils import load_model
from src.preprocessing import DataPreprocessor
from config.config import (
    TWITTER_MODEL_PATH, TWITTER_VECTORIZER_PATH,
    WIKIPEDIA_MODEL_PATH, WIKIPEDIA_VECTORIZER_PATH
)


class PredictionService:
    """
    Unified prediction service that routes inputs to appropriate models.
    Supports Twitter, Wikipedia, and automatic source detection.
    """
    
    def __init__(self):
        """Initialize the prediction service and load all models."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing PredictionService...")
        
        # Load models and vectorizers
        self._load_models()
        
        # Initialize preprocessor
        self.preprocessor = DataPreprocessor()
        
        self.logger.info("PredictionService initialized successfully")
    
    def _load_models(self):
        """Load all trained models and vectorizers."""
        try:
            # Twitter SVM
            self.logger.info("Loading Twitter SVM model...")
            self.twitter_model = load_model(TWITTER_MODEL_PATH)
            self.twitter_vectorizer = load_model(TWITTER_VECTORIZER_PATH)
            
            # Wikipedia Random Forest
            self.logger.info("Loading Wikipedia RF model...")
            self.wikipedia_model = load_model(WIKIPEDIA_MODEL_PATH)
            self.wikipedia_vectorizer = load_model(WIKIPEDIA_VECTORIZER_PATH)
            
            self.logger.info("All models loaded successfully")
            
        except FileNotFoundError as e:
            self.logger.error(f"Model file not found: {e}")
            raise RuntimeError(
                "Models not found. Please train models first using: "
                "python train_all_models.py"
            )
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
            raise
    
    def predict(self, text: str, source_type: str = 'auto') -> Dict:
        """
        Predict cyberbullying for given text.
        
        Args:
            text: Input text to analyze
            source_type: Source type ('twitter', 'wikipedia', or 'auto')
            
        Returns:
            Dictionary with prediction results:
            {
                'text': original text,
                'prediction': label (0 or 1),
                'label': human-readable label,
                'confidence': confidence score (0-1),
                'source_type': detected/specified source type,
                'latency_ms': prediction latency in milliseconds
            }
        """
        start_time = time.time()
        
        # Validate input
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")
        
        source_type = source_type.lower()
        if source_type not in ['twitter', 'wikipedia', 'auto']:
            raise ValueError("source_type must be 'twitter', 'wikipedia', or 'auto'")
        
        # Auto-detect source if needed
        if source_type == 'auto':
            source_type = self._detect_source(text)
            self.logger.info(f"Auto-detected source type: {source_type}")
        
        # Preprocess text
        clean_text = self.preprocessor.preprocess_text(text)
        
        # Route to appropriate model
        if source_type == 'twitter':
            prediction, confidence = self._predict_twitter(clean_text)
            label = 'Hate Speech' if prediction == 1 else 'Non-Hate'
        else:  # wikipedia
            prediction, confidence = self._predict_wikipedia(clean_text)
            label = 'Personal Attack' if prediction == 1 else 'Non-Attack'
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            'text': text,
            'prediction': int(prediction),
            'label': label,
            'confidence': float(confidence),
            'source_type': source_type,
            'latency_ms': round(latency_ms, 2)
        }
        
        self.logger.info(
            f"Prediction: {label} (confidence: {confidence:.2%}, "
            f"latency: {latency_ms:.2f}ms)"
        )
        
        return result
    
    def _predict_twitter(self, clean_text: str) -> Tuple[int, float]:
        """
        Predict using Twitter SVM model.
        
        Args:
            clean_text: Preprocessed text
            
        Returns:
            Tuple of (prediction, confidence)
        """
        vec = self.twitter_vectorizer.transform([clean_text])
        prediction = self.twitter_model.predict(vec)[0]
        probabilities = self.twitter_model.predict_proba(vec)[0]
        confidence = probabilities[prediction]
        
        return prediction, confidence
    
    def _predict_wikipedia(self, clean_text: str) -> Tuple[int, float]:
        """
        Predict using Wikipedia Random Forest model.
        
        Args:
            clean_text: Preprocessed text
            
        Returns:
            Tuple of (prediction, confidence)
        """
        vec = self.wikipedia_vectorizer.transform([clean_text])
        prediction = self.wikipedia_model.predict(vec)[0]
        probabilities = self.wikipedia_model.predict_proba(vec)[0]
        confidence = probabilities[prediction]
        
        return prediction, confidence
    
    def _detect_source(self, text: str) -> str:
        """
        Auto-detect source type based on text characteristics.
        Uses ensemble approach: runs both models and selects based on confidence.
        
        Args:
            text: Original text
            
        Returns:
            Detected source type ('twitter' or 'wikipedia')
        """
        clean_text = self.preprocessor.preprocess_text(text)
        
        # Get predictions from both models
        twitter_pred, twitter_conf = self._predict_twitter(clean_text)
        wikipedia_pred, wikipedia_conf = self._predict_wikipedia(clean_text)
        
        # Simple heuristics for source detection
        # Twitter: shorter, more informal, may have mentions/hashtags
        # Wikipedia: longer, more formal, discussion-like
        
        # Check text characteristics
        has_mention = '@' in text
        has_hashtag = '#' in text
        is_short = len(text.split()) < 15
        
        # If clear Twitter indicators, use Twitter model
        if has_mention or has_hashtag:
            return 'twitter'
        
        # If very short, likely Twitter
        if is_short:
            return 'twitter'
        
        # Otherwise, use confidence-based selection
        # Choose the model with higher confidence
        if twitter_conf > wikipedia_conf:
            return 'twitter'
        else:
            return 'wikipedia'
    
    def predict_batch(self, texts: list, source_type: str = 'auto') -> list:
        """
        Predict cyberbullying for multiple texts.
        
        Args:
            texts: List of input texts
            source_type: Source type for all texts
            
        Returns:
            List of prediction dictionaries
        """
        results = []
        for text in texts:
            try:
                result = self.predict(text, source_type)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error predicting text '{text[:50]}...': {e}")
                results.append({
                    'text': text,
                    'error': str(e)
                })
        
        return results
    
    def get_model_info(self) -> Dict:
        """
        Get information about loaded models.
        
        Returns:
            Dictionary with model information
        """
        return {
            'twitter_model': {
                'type': 'Support Vector Machine (SVM)',
                'kernel': getattr(self.twitter_model, 'kernel', 'unknown'),
                'classes': ['Non-Hate', 'Hate Speech']
            },
            'wikipedia_model': {
                'type': 'Random Forest',
                'n_estimators': getattr(self.wikipedia_model, 'n_estimators', 'unknown'),
                'classes': ['Non-Attack', 'Personal Attack']
            },
            'preprocessor': {
                'max_features': self.preprocessor.max_features,
                'ngram_range': self.preprocessor.ngram_range
            }
        }
