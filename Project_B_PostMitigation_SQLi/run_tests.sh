#!/usr/bin/env bash
set -e
PROJECT_DIR=$(cd "$(dirname "$0")" && pwd)
python -m venv "$PROJECT_DIR/.venv"
. "$PROJECT_DIR/.venv/bin/activate"
pip install -r "$PROJECT_DIR/requirements.txt"
REPEAT=${1:-1}
DB_SIZE=${2:-4}
export REPEAT DB_SIZE
python "$PROJECT_DIR/setup_db.py"
# Run tests (script will start and stop server)
python "$PROJECT_DIR/tests/test_post_vuln.py"

echo "Results written to $PROJECT_DIR/results/results_post.json"
