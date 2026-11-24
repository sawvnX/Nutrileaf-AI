#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then echo "Install Python 3.10–3.12 first."; exit 1; fi
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
