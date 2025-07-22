"""
Simple Flask Web Interface for Customer Sentiment Analysis

Upload audio files and get real-time sentiment analysis with purchase intent detection.
"""

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import logging
from pathlib import Path

# Import our sentiment analyzer (will be available after installing dependencies)
try:
    from customer_sentiment_analyzer import CustomerSentimentAnalyzer
except ImportError:
    CustomerSentimentAnalyzer = None

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload directory
UPLOAD_FOLDER = Path(app.config['UPLOAD_FOLDER'])
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Allowed audio extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'ogg', 'aac'}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global analyzer instance
analyzer = None

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_analyzer():
    """Initialize the sentiment analyzer."""
    global analyzer
    if CustomerSentimentAnalyzer is None:
        logger.error("CustomerSentimentAnalyzer not available. Please install dependencies.")
        return False
    
    try:
        analyzer = CustomerSentimentAnalyzer(model_size="large", device="cpu", default_language="hi")
        logger.info("Sentiment analyzer initialized successfully (large, Hindi)")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize analyzer: {str(e)}")
        return False

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis."""
    if 'audio' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS)}), 400
    
    if analyzer is None:
        return jsonify({'error': 'Sentiment analyzer not initialized'}), 500
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        logger.info(f"Processing uploaded file: {filename}")
        
        # Analyze the audio file
        result = analyzer.analyze_audio(str(filepath))
        
        # Save results
        analyzer.save_result(result, filename)
        
        # Prepare response
        response_data = {
            'success': True,
            'filename': filename,
            'text': result.text,
            'sentiment': {
                'score': round(result.sentiment_score, 3),
                'label': 'Positive' if result.sentiment_score > 0.1 else 'Negative' if result.sentiment_score < -0.1 else 'Neutral',
                'confidence': round(result.confidence, 3)
            },
            'purchase_intent': {
                'detected': result.purchase_intent,
                'confidence': round(result.purchase_confidence, 3),
                'strength': 'HIGH' if result.purchase_confidence > 0.7 else 'MEDIUM' if result.purchase_confidence > 0.4 else 'LOW',
                'key_phrases': result.key_phrases
            },
            'emotions': {k: round(v, 2) for k, v in result.emotions.items() if v > 0.1},
            'timestamp': result.timestamp
        }
        
        # Clean up uploaded file (optional - you may want to keep it)
        # os.remove(filepath)
        
        return jsonify(response_data)
    
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Error processing file {filename}: {str(e)}\nTraceback:\n{tb}")
        return jsonify({'error': f'Processing failed: {str(e)}', 'traceback': tb}), 500

@app.route('/results')
def list_results():
    """List all previous analysis results."""
    results_dir = Path('sentiment_results')
    if not results_dir.exists():
        return jsonify({'results': []})
    
    results = []
    for file_path in results_dir.glob('*.json'):
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
                result['file'] = file_path.name
                results.append(result)
        except Exception as e:
            logger.warning(f"Could not load result file {file_path}: {str(e)}")
    
    # Sort by timestamp (most recent first)
    results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return jsonify({'results': results})

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'analyzer_ready': analyzer is not None,
        'upload_folder': str(UPLOAD_FOLDER),
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })

if __name__ == '__main__':
    # Initialize the analyzer
    if not initialize_analyzer():
        print("Warning: Sentiment analyzer could not be initialized")
        print("Please install dependencies first:")
        print("pip install -r requirements_extended.txt")
    
    # Run the Flask app
    print("Starting Customer Sentiment Analysis Web Interface...")
    print("Upload audio files to analyze customer sentiment and purchase intentions")
    app.run(debug=True, host='0.0.0.0', port=5000)
