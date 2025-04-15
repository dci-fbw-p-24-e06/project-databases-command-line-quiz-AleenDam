#!/usr/bin/env python3
"""
Launcher script for the Python Quiz Master application.
This script checks for required dependencies and launches the appropriate version of the app.
"""

import os
import sys
import subprocess
import importlib.util

def check_dependency(module_name):
    """Check if a Python module is installed."""
    return importlib.util.find_spec(module_name) is not None

def install_dependency(module_name):
    """Install a Python module using pip."""
    print(f"Installing {module_name}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

def check_and_install_dependencies():
    """Check for required dependencies and install them if missing."""
    dependencies = {
        "pygame": "pygame",
        "psycopg2": "psycopg2-binary",
        "PIL": "pillow"
    }
    
    missing_deps = []
    for module, pip_package in dependencies.items():
        if not check_dependency(module):
            missing_deps.append((module, pip_package))
    
    if missing_deps:
        print("Some required dependencies are missing.")
        choice = input("Would you like to install them now? (y/n): ").strip().lower()
        if choice == 'y':
            for module, pip_package in missing_deps:
                install_dependency(pip_package)
            print("All dependencies installed successfully!")
        else:
            print("Dependencies not installed. The application may not work correctly.")
            return False
    
    return True

def create_resources():
    """Create sound and image resources if they don't exist."""
    # Check if sounds directory exists and has files
    if not os.path.exists("sounds") or not os.listdir("sounds"):
        print("Generating sound files...")
        try:
            subprocess.check_call([sys.executable, "scripts/create_sounds.py"])
        except Exception as e:
            print(f"Error generating sound files: {e}")
    
    # Check if welcome image exists
    if not os.path.exists("images/welcome.png"):
        print("Generating welcome image...")
        try:
            if not os.path.exists("images"):
                os.makedirs("images")
            subprocess.check_call([sys.executable, "scripts/create_welcome_image.py"])
        except Exception as e:
            print(f"Error generating welcome image: {e}")

def main():
    """Main function to launch the application."""
    print("Python Quiz Master Launcher")
    print("==========================")
    
    # Check dependencies
    if not check_and_install_dependencies():
        return
    
    # Create resources
    create_resources()
    
    # Ask which version to run
    print("\nWhich version would you like to run?")
    print("1. Animated GUI Version (Recommended)")
    print("2. Command Line Version")
    
    choice = input("Enter your choice (1/2): ").strip()
    
    if choice == "1":
        print("\nLaunching Animated GUI Version...")
        subprocess.call([sys.executable, "scripts/animated_gui_new.py"])
    elif choice == "2":
        print("\nLaunching Command Line Version...")
        subprocess.call([sys.executable, "scripts/main.py"])
    else:
        print("Invalid choice. Please run the script again and select 1 or 2.")

if __name__ == "__main__":
    main()