@echo off
echo ========================================
echo Running Image Body Analysis Test
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if requests library is installed
python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requests library...
    pip install requests
    if %errorlevel% neq 0 (
        echo Error: Failed to install requests library
        pause
        exit /b 1
    )
)

REM Run the image body analysis test
echo Running image body analysis test...
python test_image_body_analysis.py

pause