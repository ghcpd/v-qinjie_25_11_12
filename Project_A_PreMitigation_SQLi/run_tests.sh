#!/bin/bash
# Project A: Run tests script for vulnerable application (Linux/Mac version)

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$PROJECT_DIR/src"
DATA_DIR="$PROJECT_DIR/data"
LOGS_DIR="$PROJECT_DIR/logs"
TESTS_DIR="$PROJECT_DIR/tests"
RESULTS_DIR="$PROJECT_DIR/results"

echo "========================================"
echo "Project A: Pre-Mitigation Tests"
echo "========================================"
echo ""

# Ensure directories exist
mkdir -p "$DATA_DIR" "$LOGS_DIR" "$RESULTS_DIR"

# Create virtual environment
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv"
fi

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Install requirements
echo "Installing requirements..."
pip install -r "$PROJECT_DIR/requirements.txt" -q

# Initialize database
echo "Initializing database..."
cd "$SRC_DIR"
python init_db.py

# Start Flask app in background
echo "Starting Flask application..."
python app.py > "$LOGS_DIR/app_output.log" 2> "$LOGS_DIR/app_error.log" &
APP_PID=$!
echo "Flask app started with PID: $APP_PID"

# Wait for app to start
sleep 3

# Run tests
echo "Running tests..."
cd "$TESTS_DIR"
python test_pre_vuln.py
TEST_RESULT=$?

# Kill Flask app
echo "Stopping Flask application..."
kill $APP_PID 2>/dev/null || true

echo ""
echo "========================================"
echo "Test Run Completed"
echo "Results: $RESULTS_DIR/results_pre.json"
echo "Logs: $LOGS_DIR"
echo "========================================"

exit $TEST_RESULT
