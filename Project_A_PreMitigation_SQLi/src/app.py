"""
Project A: Vulnerable Flask Application with SQL Injection
This application intentionally exposes SQL injection vulnerabilities for testing.
"""

import os
import sys
import logging
import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, g

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
DATABASE = os.path.join(os.path.dirname(__file__), '..', 'data', 'vulnerable.db')
PORT = 5000


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
def search():
    """
    VULNERABLE ENDPOINT: SQL Injection via 'query' parameter
    This endpoint intentionally uses raw SQL concatenation to demonstrate vulnerability.
    """
    query_param = request.args.get('query', '')
    
    logger.info(f"Search request with query parameter: {query_param}")
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # VULNERABLE: Direct string concatenation - allows SQL injection
        vulnerable_sql = f"SELECT id, name, email, role FROM users WHERE name LIKE '%{query_param}%'"
        logger.debug(f"Executing SQL: {vulnerable_sql}")
        
        cursor.execute(vulnerable_sql)
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
        # VULNERABLE: Stack trace exposure
        logger.error(f"Error in search: {str(e)}")
        error_msg = str(e)
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'type': type(e).__name__
        }), 500


@app.route('/login', methods=['POST'])
def login():
    """
    VULNERABLE ENDPOINT: SQL Injection via POST body
    Authentication bypass through SQL injection.
    """
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    logger.info(f"Login attempt for username: {username}")
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # VULNERABLE: Direct string concatenation in WHERE clause
        vulnerable_sql = f"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password}'"
        logger.debug(f"Executing SQL: {vulnerable_sql}")
        
        cursor.execute(vulnerable_sql)
        user = cursor.fetchone()
        
        if user:
            logger.warning(f"Login successful for: {username} with role: {user['role']}")
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
            logger.warning(f"Login failed for: {username}")
            return jsonify({
                'status': 'error',
                'message': 'Authentication failed'
            }), 401
            
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'vulnerable-api'}), 200


if __name__ == '__main__':
    logger.info(f"Starting vulnerable Flask application on port {PORT}")
    app.run(host='127.0.0.1', port=PORT, debug=False)
