#!/usr/bin/env python3
"""
Setup script for the Assistance Django project.
This script creates a virtual environment and installs required packages.
"""

import os
import sys
import subprocess
import venv

def create_virtual_environment():
    """Create a virtual environment."""
    venv_dir = os.path.join(os.path.dirname(__file__), 'venv')
    
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        venv.create(venv_dir, with_pip=True)
        print("Virtual environment created successfully!")
    else:
        print("Virtual environment already exists.")

def install_requirements():
    """Install requirements from requirements.txt."""
    venv_dir = os.path.join(os.path.dirname(__file__), 'venv')
    
    # Determine the path to pip based on the operating system
    if os.name == 'nt':  # Windows
        pip_path = os.path.join(venv_dir, 'Scripts', 'pip')
    else:  # Unix/Linux/Mac
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
    
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if os.path.exists(requirements_file):
        print("Installing requirements...")
        try:
            subprocess.check_call([pip_path, 'install', '-r', requirements_file])
            print("Requirements installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing requirements: {e}")
            sys.exit(1)
    else:
        print("requirements.txt not found!")

def main():
    """Main function to setup the Django project."""
    print("Setting up Assistance Django project...")
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install requirements
    install_requirements()
    
    print("\nSetup completed successfully!")
    print("\nTo activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("  venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("  source venv/bin/activate")
    
    print("\nTo run the Django development server:")
    print("  python manage.py runserver")

if __name__ == "__main__":
    main()