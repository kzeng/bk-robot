#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Check if background mode is requested
if [ "$1" == "-b" ] || [ "$1" == "--background" ]; then
    echo "Starting robot service in background mode..."
    python run.py > app/logs/app.log 2>&1 &
else
    echo "Starting robot service in foreground mode..."
    python run.py 2>&1 | tee -a app/logs/app.log
fi
