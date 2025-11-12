from flask import Flask, request, render_template, jsonify
import os

# App root is in src/; templates and static are in parent project directory
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'), static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
# Expose a fake API key in the front end for testing secrets exposure
FAKE_API_KEY = os.environ.get('FAKE_API_KEY', 'FAKE-SECRET-ABC-123')

@app.route('/', methods=['GET'])
def index():
    # Simple comment input that will be rendered back unsafely (reflective XSS)
    comment = request.args.get('comment', '')
    return render_template('index.html', comment=comment, api_key=FAKE_API_KEY)

@app.route('/debug', methods=['GET'])
def debug_info():
    # A debug endpoint that exposes secrets to the UI intentionally
    return jsonify({'api_key': FAKE_API_KEY, 'secret_note': 'This is a debug panel with secrets.'})

@app.route('/submit', methods=['POST'])
def submit_comment():
    # Accept a submitted comment; store it in localStorage via JS on purpose (vulnerable by design)
    comment = request.form.get('comment', '')
    return render_template('index.html', comment=comment, api_key=FAKE_API_KEY)

if __name__ == '__main__':
    # Run without reloader in tests to avoid spawning separate process
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
