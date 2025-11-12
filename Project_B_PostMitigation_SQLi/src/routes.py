import time
from flask import request, jsonify, abort
from .db import get_db
from pathlib import Path
import sqlite3

LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)


def _log(msg):
    with open(LOGS_DIR / 'server.log', 'a') as f:
        f.write(f"{time.time()}: {msg}\n")


def is_input_bad(s):
    if s is None:
        return False
    # Simple WAF: block SQL operators or comments
    bad_tokens = ['--', ';', '/*', '*/', "' OR ", 'UNION', 'SLEEP', 'BENCHMARK', 'INFORMATION_SCHEMA']
    for tok in bad_tokens:
        if tok.lower() in s.lower():
            return True
    if len(s) > 200:
        return True
    if any(ord(c) < 32 for c in s):
        return True
    return False


def register_middleware(app):
    @app.before_request
    def waf_check():
        # Inspect query string params
        for k, v in request.args.items():
            if is_input_bad(v):
                _log(f"WAF_BLOCK: key={k} value={v}")
                abort(400, description='Bad request')


def register_routes(app):
    @app.route('/search')
    def search():
        q = request.args.get('query', '')
        conn = get_db()
        cur = conn.cursor()
        try:
            sql = "SELECT id, username FROM users WHERE username LIKE ? LIMIT 100"
            _log(f"PARAM_SQL: {sql} params=%{q}%")
            cur.execute(sql, (f"%{q}%",))
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
        try:
            sql = "SELECT id, username FROM users WHERE username = ? AND password = ? LIMIT 1"
            _log(f"PARAM_AUTH_SQL: {sql} user={user}")
            cur.execute(sql, (user, pwd))
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
        q = request.args.get('q', '')
        # Input validation prevents injection, so time-based injections will be blocked by WAF
        conn = get_db()
        cur = conn.cursor()
        try:
            sql = "SELECT id FROM users WHERE username = ?"
            _log(f"PARAM_SLEEP_SQL: {sql} q={q}")
            cur.execute(sql, (q,))
            rows = cur.fetchall()
            return jsonify({'count': len(rows)})
        except sqlite3.Error as e:
            _log(f"ERROR: {e}")
            return jsonify({'error': 'internal error'}), 500
