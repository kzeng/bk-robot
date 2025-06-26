#!/bin/bash
# filepath: install_v4l.sh

# Set error handling
set -e

echo "Starting installation process..."

# 1. Ask about v4l-utils installation
read -p "Do you want to install v4l-utils? (y/n) " answer
if [[ $answer == "y" ]] || [[ $answer == "Y" ]]; then
    echo "Installing v4l-utils..."
    sudo apt-get update && sudo apt-get install -y v4l-utils
else
    echo "Skipping v4l-utils installation"
fi

# 2. Ask about ffmpeg installation
read -p "Do you want to install ffmpeg? (y/n) " answer
if [[ $answer == "y" ]] || [[ $answer == "Y" ]]; then
    echo "Installing ffmpeg..."
    sudo apt-get update && sudo apt-get install -y ffmpeg
else
    echo "Skipping ffmpeg installation"
fi

echo "Installation completed successfully!"


