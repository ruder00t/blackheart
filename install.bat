@echo off
REM Blackheart installer (Windows).
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Report Builder also needs pandoc and the WeasyPrint GTK runtime:
echo   pandoc:     https://pandoc.org/installing.html  (or: winget install --id JohnMacFarlane.Pandoc)
echo   WeasyPrint: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows
echo.
echo Then start with: run.bat
