#!/bin/bash

# Run all UI security tests and generate comparison report
# This script runs both pre-mitigation and post-mitigation tests sequentially

set -e

echo "=========================================="
echo "UI Security Evaluation - Complete Test Suite"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create results directory
mkdir -p results

# Run Project A (Pre-Mitigation) tests
echo "=========================================="
echo "Phase 1: Running Pre-Mitigation Tests"
echo "=========================================="
cd Project_A_PreMitigation_UI
chmod +x run_ui_tests.sh
./run_ui_tests.sh
cd ..

# Run Project B (Post-Mitigation) tests
echo ""
echo "=========================================="
echo "Phase 2: Running Post-Mitigation Tests"
echo "=========================================="
cd Project_B_PostMitigation_UI
chmod +x run_ui_tests.sh
./run_ui_tests.sh
cd ..

# Generate comparison report
echo ""
echo "=========================================="
echo "Phase 3: Generating Comparison Report"
echo "=========================================="
python generate_comparison_report.py

echo ""
echo "=========================================="
echo "All tests completed!"
echo "=========================================="
echo "Comparison report: compare_ui_security_report.md"
echo "Pre-mitigation results: Project_A_PreMitigation_UI/results/results_pre.json"
echo "Post-mitigation results: Project_B_PostMitigation_UI/results/results_post.json"
echo "=========================================="

