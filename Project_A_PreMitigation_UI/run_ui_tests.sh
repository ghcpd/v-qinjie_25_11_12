#!/bin/bash
set -e
ROOT=$(dirname "$0")
cd "$ROOT"
python -m pip install -r requirements.txt
python -m playwright install
# Run tests — accepts optional args: repeat browser viewport
python tests/test_pre_ui.py --repeat ${1:-1} --browser ${2:-chromium} --viewport ${3:-1024x768}
echo "Results written to results/results_pre.json"
