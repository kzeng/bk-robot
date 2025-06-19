import cv2

def get_camera_resolutions():
    # Test 6 cameras (from index 0 to 5)
    for i in range(6):
        print(f"\nTesting Camera {i}:")
        cap = cv2.VideoCapture(i)
        
        if not cap.isOpened():
            print(f"Could not open camera {i}")
            continue
            
        # Common resolutions to test
        resolutions = [
            (640, 480),
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1920, 1080),
            (2560, 1440),
            (3840, 2160)
        ]
        
        print("Supported resolutions:")
        for res in resolutions:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
            
            actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            
            if actual_width == res[0] and actual_height == res[1]:
                print(f"✓ {actual_width}x{actual_height}")
            
        # Get current resolution
        current_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        current_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Current resolution: {current_width}x{current_height}")
        
        cap.release()

if __name__ == "__main__":
    get_camera_resolutions()
