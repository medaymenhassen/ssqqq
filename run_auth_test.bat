@echo off
echo ==========================================
echo Running Authentication Flow Test
echo ==========================================

echo.
echo Installing required packages...
pip install requests

echo.
echo Running authentication flow test...
python test_auth_flow.py

echo.
echo Test completed!
pause