@echo off
cd /d "%~dp0"

echo Starting Local Data Analysis Agent...
echo.

call .venv\Scripts\activate.bat

python -m streamlit run app.py

pause