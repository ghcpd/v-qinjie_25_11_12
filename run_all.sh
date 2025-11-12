#!/usr/bin/env bash
set -e
ROOT=$(cd "$(dirname "$0")" && pwd)

# Run Project A
echo "Running Project A tests (pre-mitigation)"
cd "$ROOT/Project_A_PreMitigation_SQLi"
REPEAT=${1:-1}
DB_SIZE=${2:-10}
./run_tests.sh $REPEAT $DB_SIZE

# Run Project B
echo "Running Project B tests (post-mitigation)"
cd "$ROOT/Project_B_PostMitigation_SQLi"
./run_tests.sh $REPEAT $DB_SIZE

# Generate compare report
python "$ROOT/generate_compare_report.py"

echo "Compare report at $ROOT/compare_report.md"
