#!/bin/bash

# Setup script for UI Security Evaluation Project
# This script sets up the environment for running the evaluation

set -e

echo "=========================================="
echo "UI Security Evaluation - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python 3.8+
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "ERROR: Python 3.8 or higher is required"
    exit 1
fi

# Install dependencies for both projects
echo ""
echo "Installing dependencies for Project A (Pre-Mitigation)..."
cd Project_A_PreMitigation_UI
pip install -q -r requirements.txt
cd ..

echo ""
echo "Installing dependencies for Project B (Post-Mitigation)..."
cd Project_B_PostMitigation_UI
pip install -q -r requirements.txt
cd ..

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
python3 -m playwright install chromium --with-deps || python3 -m playwright install chromium || python -m playwright install chromium || echo "Warning: Playwright browser installation failed. You may need to install manually."

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p results
mkdir -p Project_A_PreMitigation_UI/{results,screenshots,logs}
mkdir -p Project_B_PostMitigation_UI/{results,screenshots,logs}

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x run_all_ui.sh
chmod +x Project_A_PreMitigation_UI/run_ui_tests.sh
chmod +x Project_B_PostMitigation_UI/run_ui_tests.sh

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "You can now run the evaluation with:"
echo "  ./run_all_ui.sh"
echo ""
echo "Or run individual projects:"
echo "  cd Project_A_PreMitigation_UI && ./run_ui_tests.sh"
echo "  cd Project_B_PostMitigation_UI && ./run_ui_tests.sh"
echo ""

