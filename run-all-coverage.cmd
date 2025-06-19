@echo off
REM Run backend (pytest) coverage
python -m pytest --cov=src --cov-report=html

REM Copy backend coverage to public folder
copy /Y htmlcov\index.html extract-load-ui\public\backend-coverage.html
