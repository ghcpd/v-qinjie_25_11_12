"""
Vulnerable Flask Application - Pre-Mitigation
This application demonstrates UI-related security vulnerabilities:
- Reflected XSS in comment form
- DOM-based XSS in dynamic content
- API keys exposed in frontend JavaScript
- Sensitive data in debug panels
"""

from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# VULNERABILITY: API keys hardcoded and exposed
API_KEY = ""
SECRET_TOKEN = ""
DEBUG_MODE = True

@app.route('/')
def index():
    """Main page with comment form"""
    return render_template('index.html', api_key=API_KEY, debug_mode=DEBUG_MODE)

@app.route('/comment', methods=['POST'])
def submit_comment():
    """
    VULNERABILITY: Reflected XSS
    User input is directly rendered without sanitization
    """
    comment = request.form.get('comment', '')
    username = request.form.get('username', 'Anonymous')
    
    # VULNERABILITY: No input validation or sanitization
    return render_template('comment_result.html', 
                         comment=comment, 
                         username=username,
                         api_key=API_KEY,
                         secret_token=SECRET_TOKEN)

@app.route('/api/user-info')
def user_info():
    """
    VULNERABILITY: Sensitive data exposed in API response
    """
    return jsonify({
        'username': 'admin',
        'email': 'admin@example.com',
        'api_key': API_KEY,
        'secret_token': SECRET_TOKEN,
        'role': 'administrator',
        'permissions': ['read', 'write', 'delete']
    })

@app.route('/search')
def search():
    """
    VULNERABILITY: Reflected XSS in search query
    """
    query = request.args.get('q', '')
    # VULNERABILITY: Query directly rendered without sanitization
    return render_template('search_results.html', query=query, api_key=API_KEY)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

