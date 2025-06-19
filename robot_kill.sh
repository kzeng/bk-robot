#!/bin/bash

# Check if robot process is running
if pgrep -f "python run.py" > /dev/null; then
    echo "Found running robot process, killing it..."
    pkill -f "python run.py"
    echo "Robot process killed."
else
    echo "No robot process found."
fi
