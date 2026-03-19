
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.enhanced_prediction_service import EnhancedPredictionService
from src.utils import setup_logger
from config.config import API_HOST, API_PORT, DEBUG, LOGS_DIR

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../../templates',
            static_folder='../../static')
CORS(app)

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv', 'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logger = setup_logger('api_enhanced', LOGS_DIR)

# Get API key from environment (.env file or system env)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')

# Initialize enhanced prediction service
try:
    prediction_service = EnhancedPredictionService(openrouter_api_key=OPENROUTER_API_KEY)
    logger.info("Enhanced prediction service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize prediction service: {e}")
    prediction_service = None


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Serve the enhanced web interface."""
    return render_template('index_enhanced.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with service status."""
    if prediction_service is None:
        return jsonify({
            'status': 'error',
            'message': 'Prediction service not initialized'
        }), 503
    
    status = prediction_service.get_service_status()
    
    return jsonify({
        'status': 'healthy',
        'message': 'Enhanced Cyberbullying Detection API',
        'version': '2.0.0',
        'services': status
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Enhanced prediction endpoint with optional GPT analysis.
    
    Request JSON:
        {
            "text": "Text to analyze",
            "source_type": "twitter|wikipedia|auto",
            "use_gpt": true|false
        }
    """
    if prediction_service is None:
        return jsonify({'error': 'Prediction service not initialized'}), 503
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Missing required field: text'}), 400
        
        source_type = data.get('source_type', 'auto')
        use_gpt = data.get('use_gpt', True)  # GPT enabled by default
        
        # Make enhanced prediction
        result = prediction_service.predict_enhanced(text, source_type, use_gpt)
        
        logger.info(f"Enhanced prediction: {result.get('ensemble_label', 'N/A')}")
        
        return jsonify(result)
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/predict/image', methods=['POST'])
def predict_image():
    """
    Predict cyberbullying from image (OCR + analysis).
    
    Form data:
        file: Image file
        source_type: twitter|wikipedia|auto
        use_gpt: true|false
    """
    if prediction_service is None:
        return jsonify({
            'success': False,
            'error': 'Prediction service not initialized'
        }), 503
    
    try:
        # Debug logging
        logger.info("=== Image Upload Request ===")
        logger.info(f"Files in request: {list(request.files.keys())}")
        logger.info(f"Form data: {dict(request.form)}")
        
        # Check if file is present
        if 'file' not in request.files:
            logger.warning("No file in request.files")
            return jsonify({
                'success': False,
                'error': 'No file provided. Expected field name: "file"'
            }), 400
        
        file = request.files['file']
        
        # Debug file info
        logger.info(f"File received: {file.filename}")
        
        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif, bmp'
            }), 400
        
        # Read file data
        image_data = file.read()
        file_size = len(image_data)
        logger.info(f"File size: {file_size} bytes")
        
        # Get parameters
        source_type = request.form.get('source_type', 'auto')
        use_gpt = request.form.get('use_gpt', 'true').lower() == 'true'
        
        logger.info(f"Processing image with source_type={source_type}, use_gpt={use_gpt}")
        
        # Predict from image
        result = prediction_service.predict_from_image(image_data, source_type, use_gpt)
        
        if not result.get('success'):
            logger.warning(f"Prediction failed: {result.get('error')}")
            return jsonify(result), 400
        
        logger.info(f"Image prediction successful: {result.get('ensemble_label', 'N/A')}")
        
        # Ensure success flag is set
        result['success'] = True
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Image prediction error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/predict/file', methods=['POST'])
def predict_file():
    """
    Predict cyberbullying from CSV/TXT file (batch processing).
    
    Form data:
        file: CSV or TXT file
        text_column: Column name for CSV (default: 'text')
        source_type: twitter|wikipedia|auto
        use_gpt: true|false (default: false for batch)
    """
    if prediction_service is None:
        return jsonify({
            'success': False,
            'error': 'Prediction service not initialized'
        }), 503
    
    try:
        # Debug logging
        logger.info("=== File Upload Request ===")
        logger.info(f"Files in request: {list(request.files.keys())}")
        logger.info(f"Form data: {dict(request.form)}")
        
        if 'file' not in request.files:
            logger.warning("No file in request.files")
            return jsonify({
                'success': False,
                'error': 'No file provided. Expected field name: "file"'
            }), 400
        
        file = request.files['file']
        
        # Debug file info
        logger.info(f"File received: {file.filename}")
        
        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: csv, txt'
            }), 400
        
        # Get parameters
        source_type = request.form.get('source_type', 'auto')
        use_gpt = request.form.get('use_gpt', 'false').lower() == 'true'
        text_column = request.form.get('text_column', 'text')
        
        # Read file based on type
        filename = secure_filename(file.filename)
        logger.info(f"Processing file: {filename}, source_type={source_type}")
        
        texts = []
        
        if filename.endswith('.csv'):
            # Read CSV - try multiple encodings and handle malformed CSV
            df = None
            errors_encountered = []
            
            # Try different parsing strategies
            strategies = [
                {'encoding': 'utf-8', 'on_bad_lines': 'skip'},
                {'encoding': 'latin-1', 'on_bad_lines': 'skip'},
                {'encoding': 'cp1252', 'on_bad_lines': 'skip'},
                {'encoding': 'utf-8', 'error_bad_lines': False, 'warn_bad_lines': False},
                {'encoding': 'utf-8', 'on_bad_lines': 'skip', 'engine': 'python'},
                {'encoding': 'latin-1', 'on_bad_lines': 'skip', 'engine': 'python'},
            ]
            
            for strategy in strategies:
                try:
                    file.seek(0)
                    df = pd.read_csv(file, **strategy)
                    logger.info(f"CSV parsed successfully with strategy: {strategy}")
                    break
                except Exception as e:
                    errors_encountered.append(str(e))
                    continue
            
            if df is None:
                logger.error(f"All CSV parsing strategies failed. Errors: {errors_encountered}")
                
                # Last resort: try reading as plain text
                try:
                    file.seek(0)
                    content = file.read().decode('utf-8', errors='ignore')
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    
                    if lines:
                        logger.info(f"Falling back to plain text parsing: {len(lines)} lines")
                        # Skip header if it looks like one
                        if lines[0].lower().startswith(('text', 'content', 'message', 'comment', 'tweet')):
                            texts = lines[1:]
                        else:
                            texts = lines
                        
                        if texts:
                            logger.info(f"Using {len(texts)} lines from plain text fallback")
                            # Skip to batch prediction
                            results = prediction_service.predict_batch_enhanced(texts, source_type, use_gpt)
                            logger.info(f"File batch prediction: {len(results)} texts processed successfully")
                            
                            return jsonify({
                                'success': True,
                                'count': len(results),
                                'results': results,
                                'filename': filename,
                                'note': 'File was parsed as plain text due to CSV format issues'
                            }), 200
                except Exception as fallback_error:
                    logger.error(f"Plain text fallback also failed: {str(fallback_error)}")
                
                return jsonify({
                    'success': False,
                    'error': 'Failed to read CSV file. The file may be corrupted or have inconsistent formatting. Please ensure:\n' +
                             '1. All rows have the same number of columns\n' +
                             '2. Text fields with commas are properly quoted\n' +
                             '3. The file is saved in UTF-8 encoding\n' +
                             'Try opening the file in Excel and re-saving it as CSV (UTF-8).'
                }), 400
            
            logger.info(f"CSV columns: {list(df.columns)}")
            logger.info(f"CSV rows: {len(df)}")
            
            # Try to find text column (case-insensitive)
            text_col_found = None
            for col in df.columns:
                if col.lower() == text_column.lower():
                    text_col_found = col
                    break
            
            # If not found, try common variations
            if not text_col_found:
                common_names = ['text', 'Text', 'TEXT', 'content', 'Content', 'message', 'Message', 'comment', 'Comment', 'tweet', 'Tweet']
                for name in common_names:
                    if name in df.columns:
                        text_col_found = name
                        break
            
            if not text_col_found:
                logger.warning(f"No text column found. Available: {list(df.columns)}")
                return jsonify({
                    'success': False,
                    'error': f'No text column found. Available columns: {list(df.columns)}. Please specify the column name.'
                }), 400
            
            logger.info(f"Using column: {text_col_found}")
            texts = df[text_col_found].astype(str).tolist()
            
        elif filename.endswith('.txt'):
            # Read text file (one text per line) - try multiple encodings
            try:
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                try:
                    file.seek(0)
                    content = file.read().decode('latin-1')
                except UnicodeDecodeError:
                    file.seek(0)
                    content = file.read().decode('cp1252', errors='ignore')
            
            texts = [line.strip() for line in content.split('\n') if line.strip()]
            logger.info(f"TXT file: {len(texts)} lines")
        
        else:
            return jsonify({
                'success': False,
                'error': 'Unsupported file type'
            }), 400
        
        if not texts:
            return jsonify({
                'success': False,
                'error': 'No text found in file'
            }), 400
        
        logger.info(f"Processing {len(texts)} texts...")
        
        # Batch prediction
        results = prediction_service.predict_batch_enhanced(texts, source_type, use_gpt)
        
        logger.info(f"File batch prediction: {len(results)} texts processed successfully")
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results,
            'filename': filename
        }), 200
        
    except Exception as e:
        logger.error(f"File prediction error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """
    Batch prediction endpoint.
    
    Request JSON:
        {
            "texts": ["text1", "text2", ...],
            "source_type": "auto",
            "use_gpt": false
        }
    """
    if prediction_service is None:
        return jsonify({'error': 'Prediction service not initialized'}), 503
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        texts = data.get('texts')
        if not texts or not isinstance(texts, list):
            return jsonify({'error': 'Missing or invalid field: texts'}), 400
        
        if len(texts) > 100:
            return jsonify({'error': 'Maximum 100 texts per batch request'}), 400
        
        source_type = data.get('source_type', 'auto')
        use_gpt = data.get('use_gpt', False)  # GPT disabled by default for batch
        
        results = prediction_service.predict_batch_enhanced(texts, source_type, use_gpt)
        
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


@app.errorhandler(413)
def file_too_large(error):
    """Handle file too large errors."""
    return jsonify({'error': 'File too large. Maximum size: 16MB'}), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Run the enhanced Flask application."""
    logger.info("=" * 70)
    logger.info("Starting Enhanced Cyberbullying Detection API v2.0")
    logger.info("=" * 70)
    logger.info(f"Host: {API_HOST}")
    logger.info(f"Port: {API_PORT}")
    logger.info(f"Debug: {DEBUG}")
    logger.info("=" * 70)
    
    print("\n" + "=" * 70)
    print(" " * 10 + "ENHANCED CYBERBULLYING DETECTION API v2.0")
    print("=" * 70)
    print(f"\n✓ Server starting on http://{API_HOST}:{API_PORT}")
    print(f"✓ Web UI: http://localhost:{API_PORT}")
    print(f"✓ API Health: http://localhost:{API_PORT}/api/health")
    print("\nNew Features:")
    print("  🤖 GPT-enhanced predictions")
    print("  📷 Image text extraction (OCR)")
    print("  📁 File upload (CSV, TXT, Images)")
    print("  🎯 Ensemble predictions")
    print("\nEndpoints:")
    print(f"  GET  /                      - Enhanced web interface")
    print(f"  GET  /api/health            - Health check + service status")
    print(f"  POST /api/predict           - Enhanced text prediction")
    print(f"  POST /api/predict/image     - Image analysis (OCR)")
    print(f"  POST /api/predict/file      - File upload (CSV/TXT)")
    print(f"  POST /api/predict/batch     - Batch predictions")
    print("\n" + "=" * 70)
    print("Press CTRL+C to stop the server")
    print("=" * 70 + "\n")
    
    app.run(host=API_HOST, port=API_PORT, debug=DEBUG)


if __name__ == '__main__':
    main()
