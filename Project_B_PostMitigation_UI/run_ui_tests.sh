#!/usr/bin/env bash
set -e
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT_DIR"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# install playwright browsers
python -m playwright install

# Run the tests
python -u tests/test_post_ui.py --repeat 1

echo "Post-mitigation tests complete; see results_post.json and results/ for artifacts" 
