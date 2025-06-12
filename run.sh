#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Python virtual environment not found. Creating one..."
    
    # Check if install script exists and run it
    if [ -f "install_py_venv.sh" ]; then
        bash ./install_py_venv.sh
    else
        echo "Error: install_py_venv.sh not found!"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment!"
    exit 1
fi

# Run Flask application in background
python3 run.py &

# Store the PID of the Flask process
FLASK_PID=$!

# Wait for Flask to start
echo "Waiting for Flask server to start..."
sleep 5

# Check if Flask process is still running
if kill -0 $FLASK_PID 2>/dev/null; then
    # Check system and open browser accordingly
    if command -v firefox &> /dev/null; then
        # For Kylin OS with Firefox
        firefox --kiosk http://127.0.0.1:5000
    elif command -v xdg-open &> /dev/null; then
        # Generic Linux open
        xdg-open http://127.0.0.1:5000
    else
        echo "Please open http://127.0.0.1:5000 in your browser"
    fi
else
    echo "Error: Flask server failed to start!"
    exit 1
fi

# Keep script running until user interrupts
wait $FLASK_PID