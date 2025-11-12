"""
Vulnerable Flask Application - Pre-Mitigation
This application contains SQL injection vulnerabilities for security testing.
DO NOT USE IN PRODUCTION!
"""

from flask import Flask, request, jsonify
import sqlite3
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.db')


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "vulnerable_app"})


@app.route('/search', methods=['GET'])
def search():
    """
    VULNERABLE ENDPOINT: SQL Injection via query parameter
    This endpoint is intentionally vulnerable to demonstrate SQL injection attacks.
    """
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    try:
        conn = get_db_connection()
        # VULNERABLE: Direct string concatenation - SQL INJECTION RISK
        sql_query = f"SELECT id, username, email, role FROM users WHERE username LIKE '%{query}%' OR email LIKE '%{query}%'"
        
        logger.info(f"Executing query: {sql_query}")
        cursor = conn.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        
        # Convert rows to dictionaries
        users = [dict(row) for row in results]
        
        return jsonify({
            "query": query,
            "results": users,
            "count": len(users)
        })
    
    except Exception as e:
        # VULNERABLE: Exposing stack trace and error details
        logger.error(f"Error executing query: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "query": query
        }), 500


@app.route('/login', methods=['POST'])
def login():
    """
    VULNERABLE ENDPOINT: SQL Injection via username/password
    This endpoint is intentionally vulnerable to demonstrate authentication bypass.
    """
    data = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    try:
        conn = get_db_connection()
        # VULNERABLE: Direct string concatenation - SQL INJECTION RISK
        sql_query = f"SELECT id, username, email, role FROM users WHERE username='{username}' AND password='{password}'"
        
        logger.info(f"Login attempt - Query: {sql_query}")
        cursor = conn.execute(sql_query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return jsonify({
                "success": True,
                "user": dict(user),
                "message": "Login successful"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401
    
    except Exception as e:
        # VULNERABLE: Exposing stack trace and error details
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500


@app.route('/users', methods=['GET'])
def list_users():
    """
    VULNERABLE ENDPOINT: SQL Injection via filter parameter
    """
    filter_role = request.args.get('role', '')
    order_by = request.args.get('order_by', 'id')
    
    try:
        conn = get_db_connection()
        # VULNERABLE: Direct string interpolation
        if filter_role:
            sql_query = f"SELECT id, username, email, role FROM users WHERE role='{filter_role}' ORDER BY {order_by}"
        else:
            sql_query = f"SELECT id, username, email, role FROM users ORDER BY {order_by}"
        
        logger.info(f"Listing users - Query: {sql_query}")
        cursor = conn.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        
        users = [dict(row) for row in results]
        
        return jsonify({
            "users": users,
            "count": len(users)
        })
    
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500


if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'), exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

