#!/usr/bin/env bash
set -e
REPEAT=${1:-1}
BROWSER=${2:-chromium}
VIEWPORT=${3:-1280x720}

# Create venv and install deps if not present
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install --with-deps

# Start server
mkdir -p logs results
nohup python src/app.py > logs/server.log 2>&1 &
PID=$!
echo "Server PID: $PID"

# Run tests
export BASE_URL="http://localhost:5002"
python tests/test_post_ui.py

# Stop server
kill $PID || true

echo "Tests finished. Results in results/"
