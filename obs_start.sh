#!/bin/bash

# Function to check if OBS is running
is_obs_running() {
    pgrep -x "obs" >/dev/null 2>&1
}

# if on macOS, use '/Applications/OBS.app/Contents/MacOS/obs --startvirtualcam --minimize-to-tray'
if [ "$(uname)" == "Darwin" ]; then
    obs_command="/Applications/OBS.app/Contents/MacOS/obs --startvirtualcam --minimize-to-tray"
else
    obs_command="obs --startvirtualcam --minimize-to-tray"
fi

# Main monitoring loop
while true; do
    if ! is_obs_running; then
        echo "$(date): OBS not running, starting it..."
        $obs_command >/dev/null 2>&1 &
        
        # Wait a moment for OBS to start
        sleep 5
        
        # Verify it started successfully
        if is_obs_running; then
            echo "$(date): OBS started successfully (PID: $(pgrep -x "obs"))"
        else
            echo "$(date): Failed to start OBS"
        fi
    fi
    
    # Check every 30 seconds
    sleep 30
done
