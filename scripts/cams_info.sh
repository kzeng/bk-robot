# use v4l2-utils to get camera info

# v4l2-ctl --list-devices
# v4l2-ctl --list-formats-ext


# get current camera list
current_cameras=$(v4l2-ctl --list-devices | grep -Eo '^[^:]+')

echo "Current cameras:"
echo "$current_cameras"

# get the first camera supported resolutions
echo "Supported resolutions for each camera:"
while read -r camera; do
    echo "Camera: $camera"
    device=$(v4l2-ctl --list-devices | grep -A 1 "^$camera" | tail -n 1 | xargs)
    if [ -n "$device" ]; then
        echo "Device: $device"
        v4l2-ctl --device="$device" --list-formats-ext | grep -E 'Size:|Width:|Height:' | sed 's/Size: //; s/Width: //; s/Height: //'
    else
        echo "Device not found for camera: $camera"
    fi
    echo
done <<< "$current_cameras" 


# get the first camera settings parameters 
# brightness, contrast, saturation, sharpness, white balance, exposure, focus, gain, iris, zoom, backlight compensation, hue
echo "Camera settings for each camera:"
while read -r camera; do
    echo "Camera: $camera"
    device=$(v4l2-ctl --list-devices | grep -A 1 "^$camera" | tail -n 1 | xargs)
    if [ -n "$device" ]; then
        echo "Device: $device"
        v4l2-ctl --device="$device" --get-ctrls | grep -E 'Control:|Type:|Value:|Default:' | sed 's/Control: //; s/Type: //; s/Value: //; s/Default: //'
    else
        echo "Device not found for camera: $camera"
    fi
    echo
done <<< "$current_cameras" 




# # get the first camera supported formats
# echo "Supported formats for each camera:"
# while read -r camera; do
#     echo "Camera: $camera"
#     device=$(v4l2-ctl --list-devices | grep -A 1 "^$camera" | tail -n 1 | xargs)
#     if [ -n "$device" ]; then
#         echo "Device: $device"
#         v4l2-ctl --device="$device" --list-formats | grep -E 'Format:|Pixel Format:' | sed 's/Format: //; s/Pixel Format: //'
#     else
#         echo "Device not found for camera: $camera"
#     fi
#     echo
# done <<< "$current_cameras" 



# # get the first camera supported capabilities
# echo "Supported capabilities for each camera:"
# while read -r camera; do
#     echo "Camera: $camera"
#     device=$(v4l2-ctl --list-devices | grep -A 1 "^$camera" | tail -n 1 | xargs)
#     if [ -n "$device" ]; then
#         echo "Device: $device"
#         v4l2-ctl --device="$device" --all | grep -E 'Capabilities:|Device Capabilities:|Driver Info:' | sed 's/Capabilities: //; s/Device Capabilities: //; s/Driver Info: //'
#     else
#         echo "Device not found for camera: $camera"
#     fi
#     echo
# done <<< "$current_cameras" 

