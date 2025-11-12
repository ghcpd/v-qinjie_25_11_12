from flask import Flask, request, render_template, jsonify, make_response
import os
import bleach

# App root is in src/; templates and static are in parent project directory
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'), static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
FAKE_API_KEY = os.environ.get('FAKE_API_KEY', 'FAKE-SECRET-ABC-123')

# Simple mask for displayed secrets
def mask_secret(secret):
    if not secret:
        return ''
    return secret[:4] + '...' + secret[-4:]

@app.after_request
def add_csp(response):
    # Content Security Policy disallowing inline scripts and external dangerous sources
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; object-src 'none';"
    return response

@app.route('/', methods=['GET'])
def index():
    # Use default Jinja2 escaping and additionally sanitize input to remove scripts
    comment_raw = request.args.get('comment', '')
    # sanitize removing script tags
    comment = bleach.clean(comment_raw, tags=[], attributes={}, styles=[], strip=True)
    masked_api_key = mask_secret(FAKE_API_KEY)
    resp = make_response(render_template('index.html', comment=comment, api_key=masked_api_key))
    return resp

@app.route('/submit', methods=['POST'])
def submit_comment():
    comment_raw = request.form.get('comment', '')
    comment = bleach.clean(comment_raw, tags=[], attributes={}, styles=[], strip=True)
    masked_api_key = mask_secret(FAKE_API_KEY)
    resp = make_response(render_template('index.html', comment=comment, api_key=masked_api_key))
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
