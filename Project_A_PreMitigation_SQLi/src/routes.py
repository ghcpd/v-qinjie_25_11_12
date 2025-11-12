from flask import request, jsonify
import sqlite3
import os
import logging

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'vulnerable.db')
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_PATH, exist_ok=True)
logging.basicConfig(filename=os.path.join(LOG_PATH, 'raw_queries.log'), level=logging.INFO)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    import time
    # expose a sleep function to simulate blind SQLi timing attacks (intentional for testing)
    conn.create_function('sleep', 1, lambda s: (time.sleep(s), 0)[1])
    return conn


def register_routes(app):
    @app.route('/')
    def index():
        return 'Vulnerable app running'

    # Vulnerable endpoint: raw SQL concatenation
    @app.route('/search')
    def search():
        q = request.args.get('query', '')
        conn = get_db_connection()
        cur = conn.cursor()
        # Vulnerable: raw SQL injection via string formatting
        sql = f"SELECT id, username, secret FROM users WHERE username LIKE '%{q}%';"
        try:
            cur.execute(sql)
            logging.info('EXECUTE: %s', sql)
            rows = cur.fetchall()
            return jsonify([dict(r) for r in rows])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/login')
    def login():
        u = request.args.get('username', '')
        p = request.args.get('password', '')
        conn = get_db_connection()
        cur = conn.cursor()
        # Vulnerable: concatenated where clause
        sql = f"SELECT id, username FROM users WHERE username='{u}' AND password='{p}';"
        try:
            cur.execute(sql)
            logging.info('EXECUTE: %s', sql)
            rows = cur.fetchall()
            if rows:
                return jsonify({'status': 'ok', 'user': rows[0]['username']})
            else:
                return jsonify({'status': 'denied'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
