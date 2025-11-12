"""
Project B: Patched Flask Application with SQL Injection Mitigations
This application implements security best practices to prevent SQL injection.
"""

import os
import sys
import logging
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, g
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'logs', 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
DATABASE = os.path.join(os.path.dirname(__file__), '..', 'data', 'patched.db')
PORT = 5001
MAX_QUERY_LENGTH = 100


def validate_input(field_name, max_length=MAX_QUERY_LENGTH, pattern=None):
    """Input validation decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            value = request.args.get(field_name, '') or request.json.get(field_name, '')
            
            # Check length
            if len(value) > max_length:
                logger.warning(f"Input validation failed: {field_name} exceeds max length")
                return jsonify({
                    'status': 'error',
                    'message': f'Input exceeds maximum length of {max_length} characters'
                }), 400
            
            # Check for suspicious patterns
            suspicious_patterns = [
                'UNION', 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP',
                '--', ';', '/*', '*/', 'EXEC', 'EXECUTE', 'SCRIPT',
                'xp_', 'sp_'
            ]
            
            value_upper = value.upper()
            for pattern in suspicious_patterns:
                if pattern in value_upper:
                    logger.warning(f"Suspicious pattern detected: {pattern} in {field_name}")
                    return jsonify({
                        'status': 'error',
                        'message': f'Invalid input detected'
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_db():
    """Get database connection."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    """Close database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/search', methods=['GET'])
@validate_input('query', max_length=100)
def search():
    """
    PATCHED ENDPOINT: SQL Injection prevention via parameterized queries
    This endpoint uses prepared statements to prevent SQL injection.
    """
    query_param = request.args.get('query', '').strip()
    
    logger.info(f"Search request with query parameter (length={len(query_param)})")
    
    try:
        # Input validation: reject empty queries
        if not query_param or len(query_param) == 0:
            logger.warning("Empty query parameter rejected")
            return jsonify({
                'status': 'error',
                'message': 'Query parameter cannot be empty'
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # SECURE: Use parameterized query (?) to prevent SQL injection
        secure_sql = "SELECT id, name, email, role FROM users WHERE name LIKE ?"
        
        # The parameter is safely passed separately from the query
        cursor.execute(secure_sql, (f'%{query_param}%',))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'name': row['name'],
                'email': row['email'],
                'role': row['role']
            })
        
        logger.info(f"Search returned {len(results)} results")
        return jsonify({
            'status': 'success',
            'count': len(results),
            'data': results
        }), 200
        
    except Exception as e:
        # SECURE: Generic error message - no stack trace exposure
        logger.error(f"Error in search: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'An error occurred while processing your request'
        }), 500


@app.route('/login', methods=['POST'])
def login():
    """
    PATCHED ENDPOINT: SQL Injection prevention with parameterized queries
    Authentication with proper input validation and parameterized queries.
    """
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    # Input validation
    if not username or not password:
        logger.warning("Login attempt with missing credentials")
        return jsonify({
            'status': 'error',
            'message': 'Username and password are required'
        }), 400
    
    if len(username) > 50 or len(password) > 100:
        logger.warning("Login attempt with oversized credentials")
        return jsonify({
            'status': 'error',
            'message': 'Credentials exceed maximum length'
        }), 400
    
    logger.info(f"Login attempt for username (length={len(username)})")
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # SECURE: Use parameterized query with ? placeholders
        secure_sql = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"
        
        cursor.execute(secure_sql, (username, password))
        user = cursor.fetchone()
        
        if user:
            logger.warning(f"Login successful with role: {user['role']}")
            return jsonify({
                'status': 'success',
                'message': 'Authentication successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
            }), 200
        else:
            logger.warning("Login failed: invalid credentials")
            return jsonify({
                'status': 'error',
                'message': 'Authentication failed'
            }), 401
            
    except Exception as e:
        logger.error(f"Error in login: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'An error occurred during authentication'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'patched-api'}), 200


if __name__ == '__main__':
    logger.info(f"Starting patched Flask application on port {PORT}")
    app.run(host='127.0.0.1', port=PORT, debug=False)
