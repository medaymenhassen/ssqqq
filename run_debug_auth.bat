@echo off
echo ==========================================
echo Running Authentication Debug Steps
echo ==========================================

echo.
echo Installing required packages...
pip install requests

echo.
echo Running step-by-step authentication debug...
python debug_auth_steps.py

echo.
echo Debug completed!
pause