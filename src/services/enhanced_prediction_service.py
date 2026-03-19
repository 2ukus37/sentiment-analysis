"""
Enhanced Prediction Service: Combines ML models with GPT for superior detection.
Provides ensemble predictions with multiple confidence scores.
"""
import logging
from typing import Dict, Optional
import time

from src.services.prediction_service import PredictionService
from src.services.gpt_service import GPTService
from src.services.image_service import ImageService


class EnhancedPredictionService:
    """
    Enhanced prediction service combining ML models and GPT.
    """
    
    def __init__(self, openrouter_api_key: Optional[str] = None):
        """
        Initialize enhanced prediction service.
        
        Args:
            openrouter_api_key: OpenRouter API key for GPT access
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Enhanced Prediction Service...")
        
        # Initialize base ML prediction service
        self.ml_service = PredictionService()
        
        # Initialize GPT service
        self.gpt_service = GPTService(api_key=openrouter_api_key)
        
        # Initialize image service
        self.image_service = ImageService()
        
        self.logger.info("Enhanced Prediction Service initialized")
    
    def predict_enhanced(self, text: str, source_type: str = 'auto', 
                        use_gpt: bool = True) -> Dict:
        """
        Enhanced prediction using both ML models and GPT.
        
        Args:
            text: Text to analyze
            source_type: Source type ('twitter', 'wikipedia', 'auto')
            use_gpt: Whether to use GPT for additional analysis
            
        Returns:
            Enhanced prediction results with ensemble scoring
        """
        start_time = time.time()
        
        # Get ML prediction
        ml_result = self.ml_service.predict(text, source_type)
        
        # Get GPT prediction if enabled
        gpt_result = None
        if use_gpt and self.gpt_service.enabled:
            gpt_result = self.gpt_service.analyze_text(text, context=source_type)
        
        # Combine results
        ensemble_result = self._combine_predictions(ml_result, gpt_result)
        
        # Add timing
        ensemble_result['total_latency_ms'] = round((time.time() - start_time) * 1000, 2)
        
        return ensemble_result
    
    def _combine_predictions(self, ml_result: Dict, gpt_result: Optional[Dict]) -> Dict:
        """
        Combine ML and GPT predictions into ensemble result.
        
        Args:
            ml_result: ML model prediction
            gpt_result: GPT prediction (optional)
            
        Returns:
            Combined ensemble prediction
        """
        # Start with ML result
        result = {
            'text': ml_result['text'],
            'ml_prediction': ml_result['prediction'],
            'ml_label': ml_result['label'],
            'ml_confidence': ml_result['confidence'],
            'ml_source': ml_result['source_type'],
            'ml_latency_ms': ml_result['latency_ms']
        }
        
        # Add GPT results if available
        if gpt_result and gpt_result.get('enabled') and 'error' not in gpt_result:
            result['gpt_enabled'] = True
            result['gpt_prediction'] = 1 if gpt_result.get('is_cyberbullying') else 0
            result['gpt_confidence'] = gpt_result.get('confidence', 50) / 100.0
            result['gpt_severity'] = gpt_result.get('severity', 'unknown')
            result['gpt_type'] = gpt_result.get('type', 'unknown')
            result['gpt_reasoning'] = gpt_result.get('reasoning', '')
            
            # Ensemble prediction: weighted average with adaptive weights
            ml_score = ml_result['prediction']
            gpt_score = result['gpt_prediction']
            
            # Adaptive weighting: if models disagree and GPT detects hate, trust GPT more
            models_disagree = (ml_score != gpt_score)
            gpt_detects_hate = (gpt_score == 1)
            
            if models_disagree and gpt_detects_hate:
                # When GPT detects hate but ML doesn't, give GPT more weight
                # This helps catch subtle cases like profanity mixed with positive text
                ml_weight = 0.4
                gpt_weight = 0.6
            else:
                # Default weights: ML is trained specifically for this task
                ml_weight = 0.6
                gpt_weight = 0.4
            
            ensemble_score = (ml_weight * ml_score) + (gpt_weight * gpt_score)
            ensemble_prediction = 1 if ensemble_score >= 0.5 else 0
            
            # Ensemble confidence: weighted average
            ensemble_confidence = (ml_weight * ml_result['confidence']) + (gpt_weight * result['gpt_confidence'])
            
            result['ensemble_prediction'] = ensemble_prediction
            result['ensemble_confidence'] = round(ensemble_confidence, 4)
            result['ensemble_label'] = self._get_ensemble_label(
                ensemble_prediction, 
                ml_result['source_type']
            )
            
            # Agreement indicator
            result['models_agree'] = (ml_result['prediction'] == result['gpt_prediction'])
            
        else:
            # GPT not available, use ML only
            result['gpt_enabled'] = False
            result['ensemble_prediction'] = ml_result['prediction']
            result['ensemble_confidence'] = ml_result['confidence']
            result['ensemble_label'] = ml_result['label']
            result['models_agree'] = True
            
            if gpt_result and 'error' in gpt_result:
                result['gpt_error'] = gpt_result['error']
        
        return result
    
    def _get_ensemble_label(self, prediction: int, source_type: str) -> str:
        """Get human-readable label for ensemble prediction."""
        if source_type == 'twitter':
            return 'Hate Speech' if prediction == 1 else 'Non-Hate'
        else:
            return 'Personal Attack' if prediction == 1 else 'Non-Attack'
    
    def predict_from_image(self, image_data: bytes, source_type: str = 'auto',
                          use_gpt: bool = True) -> Dict:
        """
        Extract text from image and predict cyberbullying.
        """
        ocr_result = self.image_service.extract_text_from_image(image_data)

        if not ocr_result['success']:
            return {'success': False, 'error': ocr_result['error']}

        extracted_text = ocr_result.get('text', '').strip()

        if len(extracted_text) < 3:
            return {
                'success': False,
                'error': (
                    'No readable text found in the image.\n'
                    'Tips for better results:\n'
                    '• Use a clear, high-resolution image\n'
                    '• Ensure text has good contrast (dark text on light background)\n'
                    '• Avoid heavily stylized or handwritten fonts\n'
                    '• Try a screenshot instead of a photo'
                ),
                'ocr_used': True,
                'extracted_text': extracted_text,
            }

        self.logger.info(f"OCR extracted {len(extracted_text)} chars via '{ocr_result.get('method', 'unknown')}'")

        prediction = self.predict_enhanced(extracted_text, source_type, use_gpt)
        prediction['success'] = True
        prediction['ocr_used'] = True
        prediction['extracted_text'] = extracted_text
        prediction['ocr_method'] = ocr_result.get('method', 'unknown')
        prediction['image_size'] = ocr_result.get('image_size')

        return prediction
    
    def predict_batch_enhanced(self, texts: list, source_type: str = 'auto',
                              use_gpt: bool = False) -> list:
        """
        Batch prediction with optional GPT enhancement.
        Note: GPT disabled by default for batch to save costs.
        
        Args:
            texts: List of texts to analyze
            source_type: Source type
            use_gpt: Whether to use GPT (expensive for batches)
            
        Returns:
            List of prediction results
        """
        results = []
        for text in texts:
            try:
                result = self.predict_enhanced(text, source_type, use_gpt)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Batch prediction error: {e}")
                results.append({
                    'text': text,
                    'error': str(e)
                })
        
        return results
    
    def get_service_status(self) -> Dict:
        """
        Get status of all services.
        
        Returns:
            Dictionary with service status
        """
        return {
            'ml_service': 'available',
            'gpt_service': 'available' if self.gpt_service.enabled else 'disabled',
            'ocr_service': 'available' if self.image_service.ocr_available else 'disabled',
            'gpt_model': self.gpt_service.model if self.gpt_service.enabled else None
        }
