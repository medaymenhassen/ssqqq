#!/bin/bash

echo "Setting up Assistance Django project..."

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup completed successfully!"

echo ""
echo "To run the Django development server:"
echo "  python manage.py runserver"
echo ""