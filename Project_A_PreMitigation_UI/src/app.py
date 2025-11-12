"""
Project A - Pre-Mitigation UI Security Vulnerabilities
Flask application with intentional XSS vulnerabilities and secrets exposure
for demonstration and testing purposes.
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import logging
from pathlib import Path

# Get absolute paths
BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'public'
LOGS_DIR = BASE_DIR / 'logs'

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
app.config['SECRET_KEY'] = 'dev-secret-key-12345'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(LOGS_DIR / 'app_pre.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Intentionally exposed secrets (VULNERABLE)
HARDCODED_API_KEY = "sk-1234567890abcdefghijklmnopqrstuv"
DATABASE_PASSWORD = "admin_db_password_prod_2024"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTUxNjIzOTAyMn0.secret_signature_key"

# In-memory storage for comments (vulnerable to XSS)
comments = []


@app.route('/')
def index():
    """Main page with vulnerable comment box"""
    logger.info("Rendering index page (vulnerable)")
    return render_template('index.html')


@app.route('/debug')
def debug_panel():
    """Debug panel exposing sensitive information (VULNERABLE)"""
    logger.warning("Debug panel accessed - exposing sensitive data")
    debug_info = {
        'api_key': HARDCODED_API_KEY,
        'db_password': DATABASE_PASSWORD,
        'admin_token': ADMIN_TOKEN,
        'environment': os.environ.copy(),
        'comments_count': len(comments),
        'timestamp': datetime.now().isoformat()
    }
    return render_template('debug.html', debug_data=debug_info)


@app.route('/api/comments', methods=['GET', 'POST'])
def handle_comments():
    """Handle comment submission and retrieval (VULNERABLE to XSS)"""
    
    if request.method == 'POST':
        data = request.get_json()
        comment_text = data.get('comment', '')
        
        logger.info(f"Received comment: {comment_text[:50]}...")
        
        # VULNERABILITY: No input sanitization - directly storing and rendering user input
        comment_entry = {
            'id': len(comments) + 1,
            'text': comment_text,  # VULNERABLE: Stored as-is without escaping
            'timestamp': datetime.now().isoformat(),
            'author': data.get('author', 'Anonymous')
        }
        
        comments.append(comment_entry)
        
        return jsonify({
            'success': True,
            'comment_id': comment_entry['id'],
            'message': 'Comment posted successfully'
        }), 201
    
    elif request.method == 'GET':
        logger.info(f"Retrieving {len(comments)} comments")
        # VULNERABILITY: Comments are returned as-is without sanitization
        # Frontend will render them unsafely
        return jsonify({
            'comments': comments,
            'count': len(comments)
        }), 200


@app.route('/api/user-profile', methods=['GET', 'POST'])
def user_profile():
    """User profile endpoint with vulnerable data display"""
    
    if request.method == 'POST':
        data = request.get_json()
        user_input = data.get('input', '')
        
        # VULNERABILITY: Directly embedding user input in response
        response = {
            'user_id': '12345',
            'username': 'testuser',
            'email': 'user@example.com',
            'last_input': user_input,  # VULNERABLE: No sanitization
            'api_key_fragment': HARDCODED_API_KEY[:10] + '...',  # Partial exposure
            'session_token': 'token_' + user_input  # VULNERABLE: User input in token
        }
        
        logger.info(f"User profile request with input: {user_input[:50]}...")
        return jsonify(response), 200
    
    else:
        # GET - Return user profile (VULNERABLE: includes sensitive data)
        profile = {
            'user_id': '12345',
            'username': 'testuser',
            'email': 'user@example.com',
            'api_key_fragment': HARDCODED_API_KEY[:15],  # Partial key exposure
            'role': 'admin',
            'debug_mode': True,
            'secrets': {
                'backup_token': ADMIN_TOKEN,
                'recovery_code': 'REC-2024-001-SECRET'
            }
        }
        return jsonify(profile), 200


@app.route('/api/search', methods=['GET'])
def search():
    """Search endpoint vulnerable to reflected XSS"""
    query = request.args.get('q', '')
    
    logger.info(f"Search query: {query}")
    
    # VULNERABILITY: Query parameter directly embedded in HTML response
    results = {
        'query': query,  # VULNERABLE: Reflected without sanitization
        'results_count': 0,
        'results': [],
        'suggestion': f'Did you mean: {query}'  # VULNERABLE: Reflected XSS
    }
    
    return jsonify(results), 200


@app.route('/api/modal-content', methods=['POST'])
def modal_content():
    """Modal content endpoint - vulnerable to DOM XSS"""
    data = request.get_json()
    user_input = data.get('content', '')
    
    # VULNERABILITY: User input injected into HTML via innerHTML
    html_content = f"""
    <div class="modal-body">
        <h3>User Input:</h3>
        <p id="user-content">{user_input}</p>
    </div>
    """
    
    logger.info(f"Modal content request with input: {user_input[:50]}...")
    
    return jsonify({
        'html': html_content,  # VULNERABLE: HTML with unescaped user input
        'safe': False
    }), 200


@app.route('/api/test-input', methods=['POST'])
def test_input():
    """Test endpoint that echoes back user input"""
    data = request.get_json()
    user_input = data.get('input', '')
    
    # VULNERABILITY: Direct echo of user input
    response = {
        'input_received': user_input,
        'input_length': len(user_input),
        'echoed_in_js': f'console.log("User input: {user_input}");',
        'echoed_in_html': user_input
    }
    
    logger.info(f"Test input: {user_input[:50]}...")
    return jsonify(response), 200


@app.route('/api/form-handler', methods=['POST'])
def form_handler():
    """Form submission handler - vulnerable to multiple attack vectors"""
    form_data = request.get_json()
    
    # VULNERABILITY: No CSRF protection, no input validation
    handler_response = {
        'form_data': form_data,  # VULNERABLE: Echoing back form data
        'processed': True,
        'message': f"Processed form from {form_data.get('name', 'Unknown')}",
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"Form handler received: {json.dumps(form_data)[:100]}...")
    return jsonify(handler_response), 200


@app.errorhandler(404)
def not_found(error):
    """404 error handler - can expose path in error message"""
    return jsonify({'error': 'Not Found', 'path': request.path}), 404


@app.errorhandler(500)
def server_error(error):
    """500 error handler - may expose stack trace"""
    logger.error(f"Server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(error),
        'timestamp': datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    logger.info("Starting Pre-Mitigation Flask application...")
    logger.warning("WARNING: This application contains intentional security vulnerabilities for testing purposes only!")
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        threaded=True
    )
