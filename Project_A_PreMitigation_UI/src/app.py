from flask import Flask, render_template, request, redirect, url_for
import os
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config['SECRET_KEY'] = 'dev_secret_key'

# intentionally exposed "secret" string to simulate secrets exposure
PUBLIC_API_KEY = "API_KEY_12345_SECRET"

comments = []

@app.route('/')
def index():
    # debug_panel shows secrets on purpose
    return render_template('index.html', comments=comments, api_key=PUBLIC_API_KEY)

@app.route('/submit', methods=['POST'])
def submit_comment():
    comment = request.form.get('comment', '')
    comments.append(comment)
    return redirect(url_for('index'))

@app.route('/hash')
def hash_reflect():
    # accept hash param and render, for DOM XSS via JS
    return render_template('hash.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
