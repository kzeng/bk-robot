
# use opencv to capture picture

# the following is stream link for the camera
# rtsp://admin@192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?


import cv2
import numpy as np


def capture_image_from_rtsp(rtsp_url):
    # Open a connection to the RTSP stream
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return None

    # Read a frame from the stream
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame from video stream.")
        return None

    # Release the video capture object
    cap.release()

    return frame

def main():
    rtsp_url = "rtsp://admin@192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?"
    frame = capture_image_from_rtsp(rtsp_url)
    cv2.imwrite("captured_image.jpg", frame)
    print("Image captured and saved as 'captured_image.jpg'.")

if __name__ == "__main__":
    main()

