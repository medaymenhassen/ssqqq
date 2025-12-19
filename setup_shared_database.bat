@echo off
echo Setting up shared database configuration...

REM Check if database-config.json exists
if not exist "database-config.json" (
    echo Error: database-config.json not found!
    pause
    exit /b 1
)

echo Loading database configuration...
for /f "delims=" %%x in ('type database-config.json ^| jq -r ".host"') do set DB_HOST=%%x
for /f "delims=" %%x in ('type database-config.json ^| jq -r ".port"') do set DB_PORT=%%x
for /f "delims=" %%x in ('type database-config.json ^| jq -r ".user"') do set DB_USER=%%x
for /f "delims=" %%x in ('type database-config.json ^| jq -r ".password"') do set DB_PASSWORD=%%x
for /f "delims=" %%x in ('type database-config.json ^| jq -r ".database"') do set DB_NAME=%%x

echo Database configuration loaded:
echo   Host: %DB_HOST%
echo   Port: %DB_PORT%
echo   User: %DB_USER%
echo   Database: %DB_NAME%

echo.
echo Please ensure PostgreSQL is running and the database "%DB_NAME%" exists.
echo If it doesn't exist, please create it manually using pgAdmin or psql.

echo.
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Start Django application: cd assistance && python manage.py runserver
echo 2. Start Spring Boot application: cd School && mvn spring-boot:run
echo 3. Start Angular application: cd 3Dproject && npm start

pause