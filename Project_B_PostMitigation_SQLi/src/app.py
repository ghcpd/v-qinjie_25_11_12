from flask import Flask, request, jsonify
from .db import get_db
from .routes import register_routes, register_middleware

app = Flask(__name__)
register_middleware(app)
register_routes(app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)
