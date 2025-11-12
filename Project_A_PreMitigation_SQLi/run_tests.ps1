python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; python src/db_setup.py; python tests/run_tests.py $args
