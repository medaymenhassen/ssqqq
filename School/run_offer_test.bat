@echo off
echo ========================================
echo Running Offer System Test
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

REM Run the offer system test
echo Running offer system test...
python test_offer_system.py

pause