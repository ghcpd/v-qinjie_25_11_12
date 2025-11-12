#!/bin/bash
# Test execution script for Project A (Pre-Mitigation)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Project A - Pre-Mitigation SQLi Tests"
echo "=========================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    # Try python3 first, fall back to python
    if command -v python3 &> /dev/null; then
        python3 -m venv venv
    elif command -v python &> /dev/null; then
        python -m venv venv
    else
        echo "ERROR: Python not found. Please install Python 3.7+"
        exit 1
    fi
    # Verify venv was created
    if [ ! -d "venv" ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
# Handle both Unix and Windows Git Bash paths
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "ERROR: Could not find venv activation script"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p results
mkdir -p data

# Initialize database
echo "Initializing database..."
python data/init_db.py

# Set environment variables
export REPEAT_COUNT=${REPEAT_COUNT:-1}
export DB_SIZE=${DB_SIZE:-small}

# Run tests
echo "Running vulnerability tests..."
python tests/test_pre_vuln.py

echo ""
echo "=========================================="
echo "Tests completed!"
echo "Results saved to: results/results_pre.json"
echo "=========================================="

deactivate

