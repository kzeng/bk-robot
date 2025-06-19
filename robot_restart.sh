#!/bin/bash

# Function to start the robot service
start_robot() {
    ./robot_start.sh "$@"
}

# Check if robot process is running
if pgrep -f "python run.py" > /dev/null; then
    echo "Found running robot process, killing it..."
    pkill -f "python run.py"
    sleep 2
fi

# Start the robot service with any passed arguments
start_robot "$@"
