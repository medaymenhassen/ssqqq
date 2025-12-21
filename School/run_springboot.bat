@echo off
echo ========================================
echo Starting Spring Boot Application
echo ========================================

REM Check if Maven is installed
mvn -v >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Maven is not installed or not in PATH
    echo Please install Maven and try again
    pause
    exit /b 1
)

REM Clean and build the project
echo Building the Spring Boot application...
mvn clean package -DskipTests

if %errorlevel% neq 0 (
    echo Error: Build failed
    pause
    exit /b 1
)

REM Run the application
echo Starting the Spring Boot application...
java -jar target/School-0.0.1-SNAPSHOT.jar

pause