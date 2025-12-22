@echo off
REM Script to open the application in Google Chrome
REM Make sure Google Chrome is installed in the default location

SET CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
SET APP_URL=http://localhost:4200/bodyanalytics

echo Opening application in Google Chrome...
echo URL: %APP_URL%

REM Check if Chrome exists in the default location
if exist %CHROME_PATH% (
    echo Found Google Chrome. Opening application...
    start "" %CHROME_PATH% %APP_URL%
) else (
    echo Google Chrome not found in default location.
    echo Trying to open with default browser...
    start "" %APP_URL%
)

echo Application should now be opening in your browser.
echo If it doesn't open, please manually navigate to: %APP_URL%
pause