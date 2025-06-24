@echo off
:: Windows batch script for setting up Python virtual environment

echo Starting installation process...

:: 0. Check Python version
echo Checking Python version...
for /f "tokens=*" %%a in ('python --version 2^>^&1 ^| findstr /r "[0-9]\.[0-9]\.[0-9]"') do set PYTHON_VERSION=%%a
for /f "tokens=*" %%a in ('where python ^| findstr /v "AppData"') do set PYTHON_PATH=%%a

echo Found %PYTHON_VERSION% at %PYTHON_PATH%

:: Extract version components
for /f "tokens=1-3 delims=." %%a in ("%PYTHON_VERSION:~7%") do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)

:: Check for minimum required version (3.6)
if %MAJOR% == 3 if %MINOR% lss 6 (
    echo Error: Python version must be 3.6 or higher
    exit /b 1
)

:: 1. Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: 2. Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: 3. Set pip source and update pip first
echo Setting pip source to Huawei Mirror and updating pip...
python -m pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple
python -m pip install --upgrade pip

:: 4. Install Python packages
echo Installing required Python packages...
python -m pip install ^
    python-dotenv ^
    Flask ^
    Flask-Migrate ^
    Flask-SocketIO ^
    Flask-SQLAlchemy ^
    loguru ^
    obs-websocket-py ^
    opencv-python ^
    pillow ^
    pyserial ^
    python-engineio ^
    python-socketio ^
    simple-websocket ^
    SQLAlchemy ^
    websocket-client

echo Installation completed successfully!
echo To activate the virtual environment in the future, run: call venv\Scripts\activate.bat