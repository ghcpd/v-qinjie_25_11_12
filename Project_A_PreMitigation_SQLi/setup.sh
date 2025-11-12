#!/usr/bin/env bash
set -e

# Ensure system python has pip installed (so we can create venvs reliably)
SYS_PY=$(command -v python3 || command -v python || true)
if [ -n "$SYS_PY" ]; then
  if ! "$SYS_PY" -m pip --version >/dev/null 2>&1; then
    echo "System pip not found, trying ensurepip or apt-get install..."
    if "$SYS_PY" -m ensurepip --upgrade >/dev/null 2>&1; then
      echo "ensurepip succeeded"
      "$SYS_PY" -m pip install --upgrade pip setuptools wheel
    elif command -v apt-get >/dev/null 2>&1; then
      echo "Attempting to install python3-pip via apt-get (may require sudo)"
      sudo apt-get -y update; sudo apt-get -y install python3-pip
    else
      echo "No system pip and no apt-get available; proceeding — venv creation may still succeed."
    fi
  fi
fi

if [ ! -d ".venv" ]; then
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv .venv
  elif command -v python >/dev/null 2>&1; then
    python -m venv .venv
  else
    echo "No python interpreter found. Please install Python."
    exit 1
  fi
fi

# identify venv python executable
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

$VENV_PY -m pip install --upgrade pip
$VENV_PY -m pip install -r requirements.txt
$VENV_PY -c "from src.db import init_db; init_db(); print('DB initialized')"
