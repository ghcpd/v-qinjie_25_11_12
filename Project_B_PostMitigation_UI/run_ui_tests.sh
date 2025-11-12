#!/bin/bash

# Run UI Security Tests for Post-Mitigation Project
# Usage: ./run_ui_tests.sh [repeat_count] [browser_type] [viewport_width] [viewport_height]

set -e

REPEAT_COUNT=${1:-1}
BROWSER_TYPE=${2:-chromium}
VIEWPORT_WIDTH=${3:-1920}
VIEWPORT_HEIGHT=${4:-1080}

echo "=========================================="
echo "Post-Mitigation UI Security Tests"
echo "=========================================="
echo "Repeat Count: $REPEAT_COUNT"
echo "Browser: $BROWSER_TYPE"
echo "Viewport: ${VIEWPORT_WIDTH}x${VIEWPORT_HEIGHT}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create necessary directories
mkdir -p results screenshots logs

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
python3 -m playwright install chromium --with-deps || python -m playwright install chromium || echo "Warning: Playwright browser installation failed"

# Start Flask server in background
echo "Starting Flask server..."
python src/app.py > logs/server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Check if server is running
if ! curl -s http://localhost:5001 > /dev/null; then
    echo "ERROR: Server failed to start"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

echo "Server started (PID: $SERVER_PID)"

# Run tests
echo "Running UI security tests..."
python tests/test_post_ui.py

# Stop server
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo ""
echo "=========================================="
echo "Tests completed!"
echo "Results: results/results_post.json"
echo "Screenshots: screenshots/"
echo "Logs: logs/"
echo "=========================================="

