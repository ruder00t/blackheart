#!/usr/bin/env bash
# Start Blackheart. Creates a local venv on first run.
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install -q -r requirements.txt
echo "Blackheart -> http://127.0.0.1:8090"
python run.py
