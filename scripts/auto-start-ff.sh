#!/bin/bash
# when reboot auto-start firefox browser, open http://127.0.0.1:5000
# firefox must full screen

# Launch Firefox in full screen kiosk mode
/usr/bin/firefox-esr --kiosk http://127.0.0.1:5000
