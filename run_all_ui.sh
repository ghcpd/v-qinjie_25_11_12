#!/usr/bin/env bash
set -e

# Run Project A (pre-mitigation)
(cd Project_A_PreMitigation_UI; ./run_ui_tests.sh)
# Copy pre results to root results folder
mkdir -p results
cp Project_A_PreMitigation_UI/results/results_pre.json results/results_pre.json || true

# Run Project B (post-mitigation)
(cd Project_B_PostMitigation_UI; ./run_ui_tests.sh)
cp Project_B_PostMitigation_UI/results/results_post.json results/results_post.json || true

# Generate comparison report
python compare_results.py

echo "All tests executed and report generated: compare_ui_security_report.md"
