#!/bin/bash
# Setup script for nano-stochastic-model on Linux/Mac
# This script creates a virtual environment and installs dependencies

echo "==============================================================="
echo "Nano-Particulate Stochastic Model - Setup Script"
echo "==============================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "Python found:"
python3 --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "Virtual environment created successfully"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully"
echo ""

# Install package in development mode
echo "Installing package in development mode..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install package"
    exit 1
fi
echo ""

# Run tests
echo "Running tests to verify installation..."
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "WARNING: Some tests failed"
else
    echo "All tests passed!"
fi
echo ""

echo "==============================================================="
echo "Setup complete!"
echo "==============================================================="
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run examples:"
echo "  cd examples"
echo "  python example_basic_simulation.py"
echo "  python example_gillespie_simulation.py"
echo ""
echo "To run tests:"
echo "  pytest tests/ -v"
echo ""
