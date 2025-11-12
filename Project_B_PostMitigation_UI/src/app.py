"""
Secure Flask Application - Post-Mitigation
This application demonstrates proper security practices:
- Input sanitization using bleach
- Content Security Policy headers
- Safe DOM updates
- Secrets management via environment variables
- No sensitive data exposure
"""

from flask import Flask, render_template, request, jsonify, make_response
import os
import bleach
from functools import wraps

app = Flask(__name__)

# SECURITY: Use environment variables for secrets
API_KEY = os.environ.get('API_KEY', 'REDACTED_IN_PRODUCTION')
SECRET_TOKEN = os.environ.get('SECRET_TOKEN', 'REDACTED_IN_PRODUCTION')
DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'

# SECURITY: Configure CSP header
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

app.after_request(add_security_headers)

def sanitize_input(text):
    """
    SECURITY: Sanitize user input to prevent XSS
    Allows only safe HTML tags and attributes
    """
    if not text:
        return ''
    
    # Allow only safe tags and attributes
    allowed_tags = ['p', 'br', 'strong', 'em', 'u']
    allowed_attributes = {}
    
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def escape_html(text):
    """
    SECURITY: Escape HTML special characters
    """
    if not text:
        return ''
    return bleach.clean(text, tags=[], attributes={}, strip=True)

@app.route('/')
def index():
    """Main page with comment form - no secrets exposed"""
    # SECURITY: Don't pass API keys to templates
    return render_template('index.html', debug_mode=DEBUG_MODE)

@app.route('/comment', methods=['POST'])
def submit_comment():
    """
    SECURITY: Sanitized input handling
    All user input is sanitized before rendering
    """
    comment = request.form.get('comment', '')
    username = request.form.get('username', 'Anonymous')
    
    # SECURITY: Sanitize all inputs
    comment_sanitized = sanitize_input(comment)
    username_sanitized = escape_html(username)
    
    # SECURITY: No secrets passed to template
    return render_template('comment_result.html', 
                         comment=comment_sanitized, 
                         username=username_sanitized)

@app.route('/api/user-info')
def user_info():
    """
    SECURITY: Sanitized API response - no secrets exposed
    """
    return jsonify({
        'username': 'admin',
        'email': 'admin@example.com',
        'role': 'administrator',
        'permissions': ['read', 'write', 'delete']
        # SECURITY: API keys and secrets removed from response
    })

@app.route('/search')
def search():
    """
    SECURITY: Sanitized search query
    """
    query = request.args.get('q', '')
    # SECURITY: Query sanitized before rendering
    query_sanitized = escape_html(query)
    return render_template('search_results.html', query=query_sanitized)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)  # SECURITY: Debug mode disabled

