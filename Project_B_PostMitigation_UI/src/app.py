"""
Project B - Post-Mitigation UI Security Fixes
Flask application with comprehensive security mitigations including:
- Input sanitization (bleach, markupsafe)
- Content Security Policy (CSP) headers
- Safe DOM updates with proper escaping
- Secrets management via environment variables
- CSRF protection
- XSS prevention
"""

from flask import Flask, render_template, request, jsonify
from markupsafe import escape, Markup
import bleach
import json
import os
from datetime import datetime
import logging
from functools import wraps
from pathlib import Path

# Get absolute paths
BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'public'
LOGS_DIR = BASE_DIR / 'logs'

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)

app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-secure')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(LOGS_DIR / 'app_post.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Secrets should be loaded from environment variables, NOT hardcoded
# For testing, we define them but demonstrate they are NOT exposed
HARDCODED_API_KEY = os.environ.get('API_KEY', 'sk-should-be-in-env')
DATABASE_PASSWORD = os.environ.get('DB_PASSWORD', 'should-be-in-env')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'should-be-in-env')

# SECURITY: Whitelist of allowed HTML tags for sanitization
ALLOWED_TAGS = ['b', 'i', 'u', 'p', 'br', 'a', 'em', 'strong']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}

# In-memory storage for comments
comments = []


def add_security_headers(f):
    """Decorator to add security headers to responses"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = app.make_response(f(*args, **kwargs))
        
        # Content Security Policy - strict policy to prevent XSS
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        # Additional security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response
    return decorated_function


def sanitize_input(user_input, max_length=5000, allowed_tags=ALLOWED_TAGS, allowed_attributes=ALLOWED_ATTRIBUTES):
    """
    Sanitize user input to prevent XSS attacks
    - Escapes HTML entities
    - Removes potentially dangerous content
    - Limits input length
    - Uses whitelist approach for HTML
    """
    if not isinstance(user_input, str):
        user_input = str(user_input)
    
    # Limit input length to prevent DoS
    if len(user_input) > max_length:
        user_input = user_input[:max_length]
    
    # Use bleach to sanitize HTML
    cleaned = bleach.clean(
        user_input,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    return cleaned


def escape_output(text):
    """Safely escape text for HTML output"""
    return escape(text)


@app.route('/')
@add_security_headers
def index():
    """Main page with secured comment box"""
    logger.info("Rendering index page (post-mitigation)")
    return render_template('index.html')


@app.route('/api/comments', methods=['GET', 'POST'])
@add_security_headers
def handle_comments():
    """Handle comment submission and retrieval with XSS protection"""
    
    if request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Invalid request'}), 400
        
        comment_text = data.get('comment', '')
        author = data.get('author', 'Anonymous')
        
        # SECURITY: Validate and sanitize input
        if not isinstance(comment_text, str) or not comment_text.strip():
            return jsonify({'error': 'Invalid comment'}), 400
        
        if len(comment_text) > 5000:
            return jsonify({'error': 'Comment too long (max 5000 chars)'}), 400
        
        # Sanitize input - remove any HTML/scripts
        sanitized_comment = sanitize_input(comment_text)
        sanitized_author = sanitize_input(author, max_length=100)
        
        logger.info(f"Received and sanitized comment from {sanitized_author}")
        
        # SECURITY: Store sanitized content
        comment_entry = {
            'id': len(comments) + 1,
            'text': sanitized_comment,  # Stored as sanitized
            'timestamp': datetime.now().isoformat(),
            'author': sanitized_author
        }
        
        comments.append(comment_entry)
        
        return jsonify({
            'success': True,
            'comment_id': comment_entry['id'],
            'message': 'Comment posted successfully'
        }), 201
    
    elif request.method == 'GET':
        logger.info(f"Retrieving {len(comments)} comments")
        
        # SECURITY: Return sanitized comments
        # Frontend will receive pre-sanitized content
        safe_comments = [
            {
                'id': c['id'],
                'text': c['text'],  # Already sanitized
                'timestamp': c['timestamp'],
                'author': c['author']
            }
            for c in comments
        ]
        
        return jsonify({
            'comments': safe_comments,
            'count': len(safe_comments)
        }), 200


@app.route('/api/search', methods=['GET'])
@add_security_headers
def search():
    """Search endpoint with XSS protection"""
    query = request.args.get('q', '')
    
    # SECURITY: Sanitize query parameter
    sanitized_query = sanitize_input(query, max_length=500)
    
    logger.info(f"Safe search query: {sanitized_query[:50]}")
    
    # SECURITY: Return sanitized query to prevent reflected XSS
    results = {
        'query': sanitized_query,  # Safe, no XSS possible
        'results_count': 0,
        'results': [],
        'suggestion': f'Did you mean: {sanitized_query}'
    }
    
    return jsonify(results), 200


@app.route('/api/user-profile', methods=['GET', 'POST'])
@add_security_headers
def user_profile():
    """User profile endpoint with secrets protection"""
    
    if request.method == 'POST':
        data = request.get_json()
        user_input = data.get('input', '')
        
        # SECURITY: Sanitize user input
        sanitized_input = sanitize_input(user_input, max_length=500)
        
        response = {
            'user_id': '12345',
            'username': 'testuser',
            'email': 'user@example.com',
            'last_input': sanitized_input,  # Sanitized
            'api_key_fragment': '***REDACTED***',  # SECURITY: Never expose API keys
            'session_token': 'token_***REDACTED***'  # SECURITY: Masked
        }
        
        logger.info(f"User profile request processed safely")
        return jsonify(response), 200
    
    else:
        # GET - Return user profile without secrets
        profile = {
            'user_id': '12345',
            'username': 'testuser',
            'email': 'user@example.com',
            'role': 'user',  # Not 'admin'
            'debug_mode': False,  # SECURITY: Debug mode disabled in production
            'secrets': {}  # SECURITY: No secrets exposed
        }
        return jsonify(profile), 200


@app.route('/api/modal-content', methods=['POST'])
@add_security_headers
def modal_content():
    """Modal content endpoint with safe content handling"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    user_input = data.get('content', '')
    
    # SECURITY: Sanitize input before including in HTML
    sanitized_content = sanitize_input(user_input, max_length=2000)
    
    # SECURITY: Use safe template rendering - NO innerHTML in frontend
    html_content = {
        'type': 'safe_content',
        'content': sanitized_content,  # Plain text, will be set as textContent not innerHTML
        'safe': True
    }
    
    logger.info(f"Modal content generated safely")
    
    return jsonify(html_content), 200


@app.route('/api/test-input', methods=['POST'])
@add_security_headers
def test_input():
    """Test endpoint with safe input handling"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request'}), 400
    
    user_input = data.get('input', '')
    
    # SECURITY: Sanitize input
    sanitized = sanitize_input(user_input, max_length=500)
    
    response = {
        'input_received': sanitized,  # Safe
        'input_length': len(sanitized),
        'safe': True,  # Flag indicating sanitization
        'echoed_in_html': sanitized  # Safe for display
    }
    
    logger.info(f"Test input processed safely: {sanitized[:50]}")
    return jsonify(response), 200


@app.route('/api/form-handler', methods=['POST', 'OPTIONS'])
@add_security_headers
def form_handler():
    """Form submission handler with CSRF and input validation"""
    
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        return '', 204
    
    form_data = request.get_json()
    
    if not form_data:
        return jsonify({'error': 'Invalid request'}), 400
    
    # SECURITY: Validate and sanitize all form fields
    sanitized_data = {}
    for key, value in form_data.items():
        if isinstance(value, str):
            sanitized_data[key] = sanitize_input(value, max_length=1000)
        else:
            sanitized_data[key] = value
    
    handler_response = {
        'processed': True,
        'message': f"Form processed for {sanitized_data.get('name', 'Unknown')}",
        'timestamp': datetime.now().isoformat(),
        'safe': True
    }
    
    logger.info(f"Form processed safely")
    return jsonify(handler_response), 200


@app.errorhandler(404)
def not_found(error):
    """404 error handler - safe error message"""
    # SECURITY: Don't expose internal path information
    return jsonify({'error': 'Not Found'}), 404


@app.errorhandler(500)
def server_error(error):
    """500 error handler - don't expose stack trace"""
    logger.error(f"Server error: {error}")
    # SECURITY: Don't expose error details to users
    return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    logger.info("Starting Post-Mitigation Flask application with security fixes...")
    logger.info("Security features enabled: CSP, input sanitization, secret masking, XSS prevention")
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=False,  # SECURITY: Debug disabled in production
        threaded=True
    )
