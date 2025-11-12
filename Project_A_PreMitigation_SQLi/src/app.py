from flask import Flask, request, jsonify, g
import logging
import os
import time
try:
    from .db import get_db, query_raw
except Exception:
    # allow running as `python src/app.py` for convenience
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from db import get_db, query_raw

app = Flask(__name__)

# Logger
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'sql.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
handler = logging.FileHandler(log_path)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/search')
def search():
    q = request.args.get('query', '')

    # Simulate time-based blind injection capability: vulnerable app acknowledges SLEEP()
    if 'SLEEP(' in q.upper():
        try:
            # naive: parse SLEEP(n)
            n = int(q[q.upper().index('SLEEP(')+6:q.upper().index(')')])
            time.sleep(n)
        except Exception:
            pass

    # Vulnerable: building raw SQL string (INSECURE)
    sql = f"SELECT id, username, email FROM users WHERE username LIKE '%{q}%';"

    # Log raw SQL (deliberate for testing)
    app.logger.info(sql)

    try:
        rows = query_raw(sql)
        return jsonify({'results': rows})
    except Exception as e:
        # return error message with details (vulnerable behavior)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
