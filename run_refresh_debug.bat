@echo off
echo ==========================================
echo Running Refresh Token Debug Test
echo ==========================================

echo.
echo Installing required packages...
pip install requests

echo.
echo Running refresh token debug test...
python test_refresh_token_debug.py

echo.
echo Test completed!
pause