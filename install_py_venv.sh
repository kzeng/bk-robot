#!/bin/bash
# filepath: install_py_venv.sh

# Set error handling
set -e

echo "Starting installation process..."

# 0. Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
PYTHON_PATH=$(which python3)

echo "Found Python $PYTHON_VERSION at $PYTHON_PATH"

if (( $(echo "$PYTHON_VERSION 3.6" | awk '{print ($1 < $2)}') )); then
    echo "Error: Python version must be 3.6 or higher"
    exit 1
fi

# 1. Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# 2. Activate virtual environment and set pip source
echo "Activating virtual environment..."
source venv/bin/activate

echo "Setting pip source to Huawei Mirror..."
pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple

# 3. Install Python packages
echo "Installing required Python packages..."
pip install \
    python-dotenv \
    Flask \
    Flask-Migrate \
    Flask-SocketIO \
    Flask-SQLAlchemy \
    loguru \
    obs-websocket-py \
    opencv-python \
    pillow \
    pyserial \
    python-dotenv \
    python-engineio \
    python-socketio \
    simple-websocket \
    SQLAlchemy \
    websocket-client


echo "Installation completed successfully!"
echo "To activate the virtual environment in the future, run: source venv/bin/activate"