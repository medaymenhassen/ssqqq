@echo off
echo ==========================================
echo Running Backend Token Test
echo ==========================================

echo.
echo Installing required packages...
pip install requests

echo.
echo Running backend token test...
python test_backend_tokens.py

echo.
echo Test completed!
pause