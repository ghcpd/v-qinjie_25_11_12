#!/bin/bash
set -e
ROOT=$(pwd)
# Run pre-mitigation tests
cd Project_A_PreMitigation_UI
./run_ui_tests.sh
cd $ROOT

# Run post-mitigation tests
cd Project_B_PostMitigation_UI
./run_ui_tests.sh
cd $ROOT

# Generate comparison
python shared_artifacts/generate_compare_report.py

echo "Comparison report at shared_artifacts/compare_ui_security_report.md"
