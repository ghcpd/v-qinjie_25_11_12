from flask import Flask, render_template, request, jsonify, after_this_request
import os
import html

app = Flask(__name__)
# Masked API key -- never expose raw key in UI
MASKED_API_KEY = "APIKEY-****-XXXX"

@app.after_request
def add_security_headers(response):
    # Strict CSP: allow scripts only from same origin, block inline script execution
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; object-src 'none';"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.route('/')
def index():
    return render_template('index.html', api_key=MASKED_API_KEY)

@app.route('/submit', methods=['POST'])
def submit():
    comment = request.form.get('comment', '')
    # Ensure the comment is escaped to prevent reflected XSS.
    safe_comment = html.escape(comment)
    return render_template('display.html', comment=safe_comment)

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5002)), debug=False)
