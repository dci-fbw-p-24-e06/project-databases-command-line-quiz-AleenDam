#!/bin/bash

# Display welcome message
echo "====================================="
echo "  Starting Python Quiz Application   "
echo "====================================="

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the project directory
cd "$SCRIPT_DIR"

# Activate the virtual environment
echo "Activating virtual environment..."
source env/bin/activate

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    echo "Make sure the 'env' directory exists and is a valid virtual environment."
    exit 1
fi

echo "Virtual environment activated successfully!"
echo "Starting the application..."
echo "====================================="

# Run the application
python run.py

# Deactivate the virtual environment when done
deactivate

echo "====================================="
echo "Application closed. Environment deactivated."
echo "====================================="