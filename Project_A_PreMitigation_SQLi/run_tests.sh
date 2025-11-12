#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/db_setup.py
python tests/run_tests.py "$@"
