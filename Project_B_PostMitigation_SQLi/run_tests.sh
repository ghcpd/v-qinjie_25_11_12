#!/usr/bin/env bash
set -e
ROOT=$(pwd)
# Create venv if missing
if [ ! -d ".venv" ]; then
  if command -v python3 >/dev/null 2>&1; then
      python3 -m venv .venv
  elif command -v python >/dev/null 2>&1; then
      python -m venv .venv
  else
      echo "No python interpreter found. Please install Python or run this inside a system with python available."
      exit 1
  fi
fi

# Find venv python
if [ -x ".venv/bin/python" ]; then
  VENV_PY=.venv/bin/python
elif [ -x ".venv/Scripts/python" ]; then
  VENV_PY=.venv/Scripts/python
else
  if command -v python3 >/dev/null 2>&1; then
    VENV_PY=$(command -v python3)
  else
    VENV_PY=$(command -v python)
  fi
fi

# Install and initialize DB
$VENV_PY -m pip install --upgrade pip
$VENV_PY -m pip install -r requirements.txt
$VENV_PY -c "from src.db import init_db; init_db(); print('DB initialized')"
# Run tests
$VENV_PY tests/test_post_vuln.py
mkdir -p artifacts
cp logs/server.log artifacts/ || true
cp results/results_post.json artifacts/ || true

if [ -f artifacts/results_post.json ]; then
    echo "Tests finished, results available at artifacts/results_post.json"
else
    echo "No results found."
fi
