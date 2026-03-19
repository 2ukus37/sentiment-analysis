"""
Flask API for Cyberbullying Detection System.
Provides REST endpoints for text analysis.
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.prediction_service import PredictionService
from src.utils import setup_logger
from config.config import API_HOST, API_PORT, DEBUG, LOGS_DIR

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../../templates',
            static_folder='../../static')
CORS(app)

# Setup logging
logger = setup_logger('api', LOGS_DIR)

# Initialize prediction service
try:
    prediction_service = PredictionService()
    logger.info("Prediction service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize prediction service: {e}")
    prediction_service = None


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with service status
    """
    if prediction_service is None:
        return jsonify({
            'status': 'error',
            'message': 'Prediction service not initialized'
        }), 503
    
    return jsonify({
        'status': 'healthy',
        'message': 'Cyberbullying Detection API is running',
        'version': '1.0.0'
    })


@app.route('/api/models', methods=['GET'])
def get_models():
    """
    Get information about loaded models.
    
    Returns:
        JSON response with model information
    """
    if prediction_service is None:
        return jsonify({'error': 'Prediction service not initialized'}), 503
    
    try:
        model_info = prediction_service.get_model_info()
        return jsonify(model_info)
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict cyberbullying for given text.
    
    Request JSON:
        {
            "text": "Text to analyze",
            "source_type": "twitter|wikipedia|auto" (optional, default: "auto")
        }
    
    Returns:
        JSON response with prediction results
    """
    if prediction_service is None:
        return jsonify({'error': 'Prediction service not initialized'}), 503
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Missing required field: text'}), 400
        
        source_type = data.get('source_type', 'auto')
        
        # Validate source_type
        if source_type not in ['twitter', 'wikipedia', 'auto']:
            return jsonify({
                'error': 'Invalid source_type. Must be "twitter", "wikipedia", or "auto"'
            }), 400
        
        # Make prediction
        result = prediction_service.predict(text, source_type)
        
        logger.info(f"Prediction request: source={source_type}, result={result['label']}")
        
        return jsonify(result)
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """
    Predict cyberbullying for multiple texts.
    
    Request JSON:
        {
            "texts": ["Text 1", "Text 2", ...],
            "source_type": "twitter|wikipedia|auto" (optional, default: "auto")
        }
    
    Returns:
        JSON response with list of prediction results
    """
    if prediction_service is None:
        return jsonify({'error': 'Prediction service not initialized'}), 503
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        texts = data.get('texts')
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'Missing or invalid field: texts (must be a list)'}), 400
        
        if len(texts) > 100:
            return jsonify({'error': 'Maximum 100 texts per batch request'}), 400
        
        source_type = data.get('source_type', 'auto')
        
        # Make predictions
        results = prediction_service.predict_batch(texts, source_type)
        
        logger.info(f"Batch prediction request: {len(texts)} texts")
        
        return jsonify({
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Run the Flask application."""
    logger.info("=" * 70)
    logger.info("Starting Cyberbullying Detection API")
    logger.info("=" * 70)
    logger.info(f"Host: {API_HOST}")
    logger.info(f"Port: {API_PORT}")
    logger.info(f"Debug: {DEBUG}")
    logger.info("=" * 70)
    
    print("\n" + "=" * 70)
    print(" " * 15 + "CYBERBULLYING DETECTION API")
    print("=" * 70)
    print(f"\n✓ Server starting on http://{API_HOST}:{API_PORT}")
    print(f"✓ Web UI: http://localhost:{API_PORT}")
    print(f"✓ API Docs: http://localhost:{API_PORT}/api/health")
    print("\nEndpoints:")
    print(f"  GET  /                    - Web interface")
    print(f"  GET  /api/health          - Health check")
    print(f"  GET  /api/models          - Model information")
    print(f"  POST /api/predict         - Single prediction")
    print(f"  POST /api/predict/batch   - Batch predictions")
    print("\n" + "=" * 70)
    print("Press CTRL+C to stop the server")
    print("=" * 70 + "\n")
    
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG)


if __name__ == '__main__':
    main()
