import cv2
import os
import time
from dotenv import load_dotenv

def get_max_resolution(cap):
    """Detect maximum supported resolution for a camera"""
    # Test common resolutions in descending order
    resolutions = [
        (3840, 2160),  # 4K
        (2560, 1440),  # 1440p
        (1920, 1080),  # 1080p
        (1280, 720),   # 720p
        (640, 480)     # 480p
    ]
    
    for width, height in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Allow time for settings to take effect
        time.sleep(0.1)
        
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if actual_width >= width and actual_height >= height:
            return (width, height)
    
    return (640, 480)  # Fallback to minimum

def test_camera_params(camera_url):
    """Test and report camera parameters"""
    print(f"\nTesting camera: {camera_url}")
    
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print(f"Failed to open camera: {camera_url}")
        return None
    
    try:
        # Get maximum supported resolution
        max_width, max_height = get_max_resolution(cap)
        print(f"Maximum supported resolution: {max_width}x{max_height}")
        
        # Get current resolution
        current_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        current_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Current resolution: {current_width}x{current_height}")
        
        # Get other parameters
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"FPS: {fps:.2f}")
        
        return {
            'url': camera_url,
            'max_resolution': (max_width, max_height),
            'current_resolution': (current_width, current_height),
            'fps': fps
        }
    finally:
        cap.release()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get camera URLs from environment
    camera_urls = os.getenv('CAMERA_URLS', '').split(',')
    if not camera_urls or not camera_urls[0]:
        print("No camera URLs found in .env file")
        exit(1)
    
    print("IP Camera Parameters Test")
    print("=" * 40)
    
    results = []
    for url in camera_urls:
        url = url.strip()
        if url:
            result = test_camera_params(url)
            if result:
                results.append(result)
    
    print("\nTest Summary:")
    print("=" * 40)
    for result in results:
        print(f"\nCamera: {result['url']}")
        print(f"Max Resolution: {result['max_resolution'][0]}x{result['max_resolution'][1]}")
        print(f"Current Resolution: {result['current_resolution'][0]}x{result['current_resolution'][1]}")
        print(f"FPS: {result['fps']:.2f}")
