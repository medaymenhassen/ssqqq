@echo off
echo Setting up Assistance Django project...

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Setup completed successfully!

echo.
echo To run the Django development server:
echo   python manage.py runserver
echo.

pause







python manage.py migrate contenttypes admin auth sessions                   