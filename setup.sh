#!/bin/bash

# Exit on error
set -e

echo "Setting up Switch File Manager NSZ GUI..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed. Please install pip3 and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Install Qt dependencies
echo "Installing Qt dependencies..."
pip install PySide6 qt-material

# Run the application
echo "Starting Switch File Manager NSZ GUI..."
python nsz-qt.py

# Deactivate virtual environment when done
deactivate 