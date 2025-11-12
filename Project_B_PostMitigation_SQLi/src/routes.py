from flask import request, jsonify
import sqlite3
import os
from waf import waf_check
import logging

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'patched.db')
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_PATH, exist_ok=True)
logging.basicConfig(filename=os.path.join(LOG_PATH, 'sanitized_queries.log'), level=logging.INFO)


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def register_routes(app):
    @app.before_request
    def apply_waf():
        res = waf_check()
        if res:
            return res

    @app.route('/')
    def index():
        return 'Patched app running'

    @app.route('/search')
    def search():
        q = request.args.get('query', '')
        # parameterized query: avoid injection
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # use LIKE with parameter
            cur.execute("SELECT id, username, secret FROM users WHERE username LIKE ?", (f"%{q}%",))
            logging.info('EXECUTE PARAM: %s -- %s', "SELECT id, username, secret FROM users WHERE username LIKE ?", f"%{q}%")
            rows = cur.fetchall()
            return jsonify([dict(r) for r in rows])
        except Exception as e:
            return jsonify({'error': 'An error occurred'}), 500

    @app.route('/login')
    def login():
        u = request.args.get('username', '')
        p = request.args.get('password', '')
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('SELECT id, username FROM users WHERE username=? AND password=?', (u, p))
            logging.info('EXECUTE PARAM: %s -- %s,%s', 'SELECT id, username FROM users WHERE username=? AND password=?', u, p)
            row = cur.fetchone()
            if row:
                return jsonify({'status': 'ok', 'user': row['username']})
            else:
                return jsonify({'status': 'denied'})
        except Exception as e:
            return jsonify({'error': 'An error occurred'}), 500
