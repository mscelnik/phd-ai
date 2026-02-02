@echo off
REM Setup script for nano-stochastic-model on Windows
REM This script creates a virtual environment and installs dependencies

echo ===============================================================
echo Nano-Particulate Stochastic Model - Setup Script
echo ===============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Install package in development mode
echo Installing package in development mode...
pip install -e .
if errorlevel 1 (
    echo ERROR: Failed to install package
    pause
    exit /b 1
)
echo.

REM Run tests
echo Running tests to verify installation...
pytest tests/ -v
if errorlevel 1 (
    echo WARNING: Some tests failed
    echo This might be okay depending on your system
) else (
    echo All tests passed!
)
echo.

echo ===============================================================
echo Setup complete!
echo ===============================================================
echo.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate
echo.
echo To run examples:
echo   cd examples
echo   python example_basic_simulation.py
echo   python example_gillespie_simulation.py
echo.
echo To run tests:
echo   pytest tests/ -v
echo.
pause
