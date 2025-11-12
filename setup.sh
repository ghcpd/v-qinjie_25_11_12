#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate
pip install -r Project_A_PreMitigation_SQLi/requirements.txt
pip install -r Project_B_PostMitigation_SQLi/requirements.txt
