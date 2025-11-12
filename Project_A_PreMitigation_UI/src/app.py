from flask import Flask, render_template, request, jsonify, Markup
import os

app = Flask(__name__)

# Simulate a leaked API key for pre-mitigation
LEAKED_API_KEY = "APIKEY-1234567890-UNMASKED"

@app.route('/')
def index():
    return render_template('index.html', api_key=LEAKED_API_KEY)

@app.route('/submit', methods=['POST'])
def submit():
    comment = request.form.get('comment', '')
    # Vulnerable: direct injection of user input into template without sanitization
    return render_template('display.html', comment=Markup(comment))

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=True)
