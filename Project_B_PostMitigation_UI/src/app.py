from flask import Flask, render_template, request, redirect, url_for, after_this_request, make_response
import bleach, os
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['SECRET_KEY'] = 'dev_secret_key'

# do not expose secret in front-end — server keeps it safe
SECRET_KEY = 'SERVER_SIDE_SECRET_12345'

comments = []

@app.after_request
def add_csp_headers(response):
    # CSP header to block inline scripts and disallow unsafe eval
    csp = "default-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none';"
    response.headers['Content-Security-Policy'] = csp
    return response

@app.route('/')
def index():
    # use bleach to sanitize incoming comments for safety
    return render_template('index.html', comments=comments)

@app.route('/submit', methods=['POST'])
def submit_comment():
    comment = request.form.get('comment', '')
    # sanitize with bleach — allow simple tags only
    safe = bleach.clean(comment, tags=[], attributes={}, strip=True)
    comments.append(safe)
    return redirect(url_for('index'))

@app.route('/hash')
def hash_reflect():
    return render_template('hash.html')

if __name__ == '__main__':
    app.run(debug=True, port=8001)
