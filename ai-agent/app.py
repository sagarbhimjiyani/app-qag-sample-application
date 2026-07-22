"""
Flask web app for the Gherkin Test Case Generation Agent.
Provides REST API endpoints for file upload and test case generation.
"""

import os
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file
import json


app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = Path('uploads')
RESULTS_FOLDER = Path('results')
ALLOWED_EXTENSIONS = {'yaml', 'yml', 'json'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create folders if they don't exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Gherkin Test Case Generation Agent'
    }), 200


@app.route('/generate/upload', methods=['POST'])
def generate_from_upload():
    """
    Generate Gherkin test cases from an uploaded Swagger/OpenAPI file.
    
    Expected: multipart/form-data with file field containing the swagger file
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))
        
        # Generate test cases
        from main import generate_test_cases
        test_cases = generate_test_cases(str(filepath))
        
        # Save results
        result_filename = filepath.stem + '_tests.feature'
        result_filepath = RESULTS_FOLDER / result_filename
        with open(str(result_filepath), 'w', encoding='utf-8') as f:
            f.write(test_cases)
        
        return jsonify({
            'status': 'success',
            'message': 'Test cases generated successfully',
            'test_cases': test_cases,
            'result_file': result_filename,
            'download_url': f'/download/{result_filename}'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500


@app.route('/generate/text', methods=['POST'])
def generate_from_text():
    """
    Generate Gherkin test cases from Swagger/OpenAPI specification as JSON text.
    
    Expected: JSON with 'specification' field containing the OpenAPI spec
    """
    if not request.json or 'specification' not in request.json:
        return jsonify({'error': 'No specification provided in request body'}), 400
    
    spec_text = request.json['specification']
    
    if not isinstance(spec_text, str):
        return jsonify({'error': 'Specification must be a string'}), 400
    
    try:
        # Generate test cases
        from main import generate_test_cases_from_text
        test_cases = generate_test_cases_from_text(spec_text)
        
        return jsonify({
            'status': 'success',
            'message': 'Test cases generated successfully',
            'test_cases': test_cases
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated test case file."""
    try:
        filepath = RESULTS_FOLDER / secure_filename(filename)
        
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            str(filepath),
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'error': f'File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB'
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Gherkin Test Case Generation Agent on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)
