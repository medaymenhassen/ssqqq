# PowerShell script to open the application in Google Chrome
# This script will try multiple locations for Chrome installation

$AppUrl = "http://localhost:4200/bodyanalytics"
$ChromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles}\Google\Chrome Beta\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome Beta\Application\chrome.exe"
)

Write-Host "Opening application in Google Chrome..."
Write-Host "URL: $AppUrl"

# Try to find Chrome in various locations
$ChromeFound = $false
foreach ($Path in $ChromePaths) {
    if (Test-Path $Path) {
        Write-Host "Found Google Chrome at: $Path"
        try {
            Start-Process -FilePath $Path -ArgumentList $AppUrl
            Write-Host "Application opened successfully in Google Chrome!"
            $ChromeFound = $true
            break
        } catch {
            Write-Host "Error opening Chrome: $_"
        }
    }
}

# If Chrome wasn't found, try the default browser
if (-not $ChromeFound) {
    Write-Host "Google Chrome not found. Trying default browser..."
    try {
        Start-Process $AppUrl
        Write-Host "Application opened in default browser!"
    } catch {
        Write-Host "Error opening default browser: $_"
        Write-Host "Please manually navigate to: $AppUrl"
    }
}

Write-Host "Press any key to exit..."
$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")