# main.py
# Main application file for the Smart Parking Detection System

import cv2
import pickle
import numpy as np
import time

# Import modules
from config import *
from parking_detection import checkParkingSpace, processFrame
from parking_ui import create_parking_map, create_enhanced_ui

def main():
    """Main function to run the Smart Parking Detection System"""
    
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    # Load parking positions
    try:
        with open(POSITIONS_FILE, 'rb') as f:
            posList = pickle.load(f)
    except:
        posList = []
        print("Warning: No parking positions file found. Detection will not work.")

    # Create main window
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Main loop
    while True:
        # Reset video if it ends
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        success, img = cap.read()
        if not success:
            print("Error reading video feed")
            break
            
        # Process frame for parking detection
        imgDilate = processFrame(img)

        # Check parking spaces and get occupancy data
        free_spaces, occupancy_data = checkParkingSpace(imgDilate, img, posList, 
                                                        PARKING_SPOT_WIDTH, PARKING_SPOT_HEIGHT)
        
        # Create the enhanced parking map
        parking_map = create_parking_map(occupancy_data, MAP_WIDTH, MAP_HEIGHT, 
                                        PARKING_SPOT_WIDTH, PARKING_SPOT_HEIGHT)
        
        # Resize the processed video frame to fit our UI
        img_resized = cv2.resize(img, (VIDEO_WIDTH, VIDEO_HEIGHT))
        
        # Create enhanced UI
        ui_canvas = create_enhanced_ui(img_resized, parking_map, WINDOW_WIDTH, WINDOW_HEIGHT,
                                    VIDEO_WIDTH, VIDEO_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
        
        # Show the combined UI
        cv2.imshow(WINDOW_NAME, ui_canvas)
        
        # Exit if 'q' is pressed
        key = cv2.waitKey(10)
        if key == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()