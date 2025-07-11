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

# Split version into components
MAJOR=$(echo "$PYTHON_VERSION" | cut -d '.' -f 1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d '.' -f 2)
PATCH=$(echo "$PYTHON_VERSION" | cut -d '.' -f 3)

# Check for minimum required version (3.6)
if [ $MAJOR -eq 3 ] && [ $MINOR -lt 6 ]; then
    echo "Error: Python version must be 3.6 or higher"
    exit 1
fi

# 1. Create virtual environment
echo -e "\nCreating virtual environment..."
python3 -m venv venv

# 2. Activate virtual environment and set pip source
echo -e "\nActivating virtual environment..."
source venv/bin/activate

echo -e "\nSetting pip source to Huawei Mirror..."
pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple

# 3. Install Python packages
echo -e "\nInstalling required Python packages..."
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
    python-engineio \
    python-socketio \
    simple-websocket \
    SQLAlchemy \
    psutil \
    playsound \
    requests \
    websocket-client

echo -e "\nInstallation completed successfully!"
echo -e "To activate the virtual environment in the future, run: source venv/bin/activate"


# 4. Check if apt-get is available and prompt to install v4l-utils
if command -v apt-get >/dev/null 2>&1; then
    echo -e "\nDetected apt-get package manager."
    read -p "Do you want to install 'v4l-utils' using apt-get? [Y/n]: " yn
    yn=${yn:-Y}
    if [[ "$yn" =~ ^[Yy]$ ]]; then
        sudo apt-get update
        sudo apt-get install -y v4l-utils
    else
        echo "Skipping installation of v4l-utils."
    fi
fi