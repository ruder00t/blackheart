@echo off
REM Start Blackheart. Creates a local venv on first run.
cd /d %~dp0
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -q -r requirements.txt
echo Blackheart -^> http://127.0.0.1:8090
python run.py
