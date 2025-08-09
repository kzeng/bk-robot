#!/bin/bash
# when reboot auto-start firefox browser, open http://127.0.0.1:5000
# firefox must full screen

# Wait for network connection
while ! ping -c 1 -W 1 127.0.0.1; do
    sleep 1
done

# Wait for Flask server to be ready
while ! curl -s http://127.0.0.1:5000 >/dev/null; do
    sleep 1
done

# Launch Firefox in full screen kiosk mode
/usr/bin/firefox-esr --kiosk http://127.0.0.1:5000

