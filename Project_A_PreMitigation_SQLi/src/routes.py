import time
from flask import request, jsonify
from .db import get_db
from pathlib import Path
import sqlite3

LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)


def _log(msg):
    with open(LOGS_DIR / 'server.log', 'a') as f:
        f.write(f"{time.time()}: {msg}\n")


def register_routes(app):
    @app.route('/search')
    def search():
        q = request.args.get('query', '')
        conn = get_db()
        cur = conn.cursor()
        # Vulnerable: naive string interpolation into SQL
        try:
            sql = f"SELECT id, username FROM users WHERE username LIKE '%{q}%' LIMIT 100"
            _log(f"RAW_SQL: {sql}")
            # Emulate a naive DB engine: if payload includes SLEEP token, emulate a time-injection delay
            if 'SLEEP' in q.upper():
                time.sleep(5)
            cur.execute(sql)
            rows = cur.fetchall()
            out = [dict(id=row['id'], username=row['username']) for row in rows]
            return jsonify({'results': out})
        except sqlite3.Error as e:
            _log(f"ERROR: {e}")
            return jsonify({'error': 'internal error'}), 500

    @app.route('/auth')
    def auth():
        user = request.args.get('user', '')
        pwd = request.args.get('pwd', '')
        conn = get_db()
        cur = conn.cursor()
        # Vulnerable raw SQL allowing injection
        try:
            sql = f"SELECT id, username FROM users WHERE username = '{user}' AND password = '{pwd}' LIMIT 1"
            _log(f"RAW_AUTH_SQL: {sql}")
            cur.execute(sql)
            row = cur.fetchone()
            if row:
                return jsonify({'auth': 'ok', 'user': row['username']})
            else:
                return jsonify({'auth': 'failed'}), 403
        except sqlite3.Error as e:
            _log(f"ERROR: {e}")
            return jsonify({'error': 'internal error'}), 500

    @app.route('/sleep')
    def sleep_endpoint():
        # This endpoint demonstrates delay-based injection vulnerability if abused
        q = request.args.get('q', '')
        conn = get_db()
        cur = conn.cursor()
        try:
            sql = f"SELECT id FROM users WHERE username = '{q}'"
            _log(f"RAW_SLEEP_SQL: {sql}")
            if 'SLEEP' in q.upper():
                time.sleep(5)
            cur.execute(sql)
            rows = cur.fetchall()
            return jsonify({'count': len(rows)})
        except sqlite3.Error as e:
            _log(f"ERROR: {e}")
            return jsonify({'error': 'internal error'}), 500
