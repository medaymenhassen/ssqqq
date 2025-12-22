@echo off
echo ==========================================
echo Running End-to-End Body Analysis Test
echo ==========================================

echo.
echo Installing required packages...
pip install opencv-python mediapipe requests numpy

echo.
echo Running end-to-end body analysis test...
python e2e_body_analysis_test.py

echo.
echo Test completed!
pause