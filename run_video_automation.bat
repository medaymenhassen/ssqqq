@echo off
echo Installing required packages...
pip install selenium

echo.
echo Running Video Analysis Automation Tool...
python video_analysis_automation.py
pause