"""
Flask web app for the Gherkin Test Case Generation Agent.
Provides REST API endpoints for file upload and test case generation.
"""

import os
import sys
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_file
import json

# Ensure current directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import agents at module level to catch import errors early
try:
    from test_summary_agent import generate_summary_from_html, SerenityReportParser, generate_ai_insights, generate_interactive_html_report
except ImportError as e:
    print(f"Warning: test_summary_agent import failed: {e}")
    print("Summary endpoints will be unavailable. Install beautifulsoup4: pip install beautifulsoup4")


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

        # Debug/logging: capture type and repr to help diagnose streaming/async results
        try:
            import inspect, types
            tc_type = type(test_cases)
            tc_dir = [n for n in dir(test_cases) if not n.startswith('_')]
            app.logger.debug('generate_test_cases returned type=%s', tc_type)
            app.logger.debug('generate_test_cases dir=%s', tc_dir)
        except Exception:
            pass

        # Normalize result: some LLM SDKs return async generators or awaitables
        import asyncio, inspect, types
        if inspect.isasyncgen(test_cases) or isinstance(test_cases, types.AsyncGeneratorType):
            async def _collect(gen):
                parts = []
                async for part in gen:
                    parts.append(str(part))
                return ''.join(parts)
            try:
                test_cases = asyncio.run(_collect(test_cases))
            except Exception as e:
                app.logger.exception('Async generator collection failed')
                # Return diagnostics to the client to speed up debugging
                return jsonify({
                    'error': f'Failed to collect async generator result: {e}',
                    'type': str(tc_type),
                    'dir': tc_dir,
                    'status': 'failed'
                }), 500
        elif inspect.isawaitable(test_cases):
            try:
                test_cases = asyncio.run(test_cases)
            except Exception as e:
                app.logger.exception('Awaiting result failed')
                return jsonify({'error': f'Failed to await result: {e}', 'status': 'failed'}), 500
        else:
            test_cases = str(test_cases)
        
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

        # Normalize result: some LLM SDKs return async generators or awaitables
        import asyncio, inspect, types
        if inspect.isasyncgen(test_cases) or isinstance(test_cases, types.AsyncGeneratorType):
            async def _collect(gen):
                parts = []
                async for part in gen:
                    parts.append(str(part))
                return ''.join(parts)
            try:
                test_cases = asyncio.run(_collect(test_cases))
            except Exception as e:
                return jsonify({'error': f'Failed to collect async generator result: {e}', 'status': 'failed'}), 500
        elif inspect.isawaitable(test_cases):
            try:
                test_cases = asyncio.run(test_cases)
            except Exception as e:
                return jsonify({'error': f'Failed to await result: {e}', 'status': 'failed'}), 500
        else:
            test_cases = str(test_cases)
        
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


@app.route('/summary/upload', methods=['POST'])
def summary_from_upload():
    """
    Generate test execution summary from an uploaded Serenity HTML report.

    Expected: multipart/form-data with file field containing the Serenity report
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith('.html'):
            return jsonify({
                'error': 'Invalid file type. Only HTML files are accepted.'
            }), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(str(filepath))

        # Generate summary
        metrics, report_html = generate_summary_from_html(str(filepath))

        # Save report
        report_filename = filepath.stem + '_summary.html'
        report_filepath = RESULTS_FOLDER / report_filename
        with open(str(report_filepath), 'w', encoding='utf-8') as f:
            f.write(report_html)

        return jsonify({
            'status': 'success',
            'message': 'Test execution summary generated successfully',
            'metrics': metrics,
            'report_file': report_filename,
            'download_url': f'/download/{report_filename}'
        }), 200

    except ImportError:
        return jsonify({
            'error': 'test_summary_agent module not available. Install beautifulsoup4: pip install beautifulsoup4',
            'status': 'failed'
        }), 500
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500


@app.route('/summary/text', methods=['POST'])
def summary_from_text():
    """
    Generate test execution summary from Serenity HTML content as text.

    Expected: JSON with 'html_content' field containing the Serenity HTML
    """
    try:
        if not request.json or 'html_content' not in request.json:
            return jsonify({'error': 'No HTML content provided in request body'}), 400

        html_content = request.json['html_content']

        if not isinstance(html_content, str):
            return jsonify({'error': 'HTML content must be a string'}), 400

        if len(html_content) < 100:
            return jsonify({'error': 'HTML content is too short. Please provide a valid Serenity report.'}), 400

        # Parse and generate summary
        parser = SerenityReportParser(html_content)
        metrics = parser.get_metrics()

        insights = generate_ai_insights(metrics, html_content)
        report_html = generate_interactive_html_report(metrics, insights)

        return jsonify({
            'status': 'success',
            'message': 'Test execution summary generated successfully',
            'metrics': metrics,
            'report': report_html
        }), 200

    except ImportError:
        return jsonify({
            'error': 'test_summary_agent module not available. Install beautifulsoup4: pip install beautifulsoup4',
            'status': 'failed'
        }), 500
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500


@app.route('/summary/metrics/<filename>', methods=['GET'])
def get_summary_metrics(filename):
    """
    Get metrics from a previously generated summary.

    Expected: filename of the saved report
    """
    try:
        filepath = RESULTS_FOLDER / secure_filename(filename)

        if not filepath.exists():
            return jsonify({'error': 'Report file not found'}), 404

        # Read the HTML and extract metrics
        with open(str(filepath), 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extract metrics from the report
        parser = SerenityReportParser(html_content)
        metrics = parser.get_metrics()

        return jsonify({
            'status': 'success',
            'metrics': metrics,
            'report_file': filename
        }), 200

    except ImportError:
        return jsonify({
            'error': 'test_summary_agent module not available. Install beautifulsoup4: pip install beautifulsoup4',
            'status': 'failed'
        }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500



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
    
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Gherkin Test Case Generation Agent on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)
