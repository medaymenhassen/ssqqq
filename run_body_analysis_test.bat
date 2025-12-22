@echo off
echo ==========================================
echo Running Complete Body Analysis Test
echo ==========================================

echo.
echo Installing required packages...
pip install opencv-python mediapipe requests numpy

echo.
echo Running body analysis test...
python complete_body_analysis_test.py

echo.
echo Test completed!
pause