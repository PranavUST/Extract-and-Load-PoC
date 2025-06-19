@echo off
REM Run backend (pytest) coverage
python -m pytest --cov=src --cov-report=html

REM Copy all backend coverage assets to public folder for full report functionality
xcopy /Y /E /I htmlcov\* extract-load-ui\public\
