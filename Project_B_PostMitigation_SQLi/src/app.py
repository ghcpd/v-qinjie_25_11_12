from flask import Flask, request, jsonify, g
import logging
import os
import re
try:
    from .db import get_db, query_param
    from .waf import waf_middleware
except Exception:
    # allow running as `python src/app.py` for convenience
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from db import get_db, query_param
    from waf import waf_middleware

app = Flask(__name__)

# Logger
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'access.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
handler = logging.FileHandler(log_path)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

MAX_QUERY_LEN = 100
ALLOWED_RE = re.compile(r'^[\w\s@.\-]*$')


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(str(e))
    return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/search')
def search():
    q = request.args.get('query', '')

    # WAF middleware rejects suspicious patterns
    block = waf_middleware()
    if block is not None:
        return block

    # Input validation
    if len(q) > MAX_QUERY_LEN or not ALLOWED_RE.match(q):
        return jsonify({'error': 'Invalid input'}), 400

    # Parameterized query - safe
    sql = "SELECT id, username, email FROM users WHERE username LIKE ?"
    params = (f"%{q}%",)
    app.logger.info('Query executed (sanitized), len=%d', len(q))

    rows = query_param(sql, params)
    return jsonify({'results': rows})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
