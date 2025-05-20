# parking_detection.py
# Contains parking detection functionality

import cv2
import numpy as np
import cvzone

def checkParkingSpace(imgPro, img, posList, width=107, height=48):
    """
    Checks each parking space in the image and determines if it's occupied
    
    Args:
        imgPro: Processed binary image for detection
        img: Original image to draw on
        posList: List of parking space positions
        width: Width of parking spot
        height: Height of parking spot
        
    Returns:
        spaceCounter: Number of free spaces
        occupancy_data: List of tuples (position_index, is_free, position)
    """
    spaceCounter = 0
    occupancy_data = []  # Will store (position_index, is_free, position) tuples

    for i, pos in enumerate(posList):
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        is_free = count < 900
        if is_free:
            color = (0, 255, 0)  # Green for free
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)  # Red for occupied
            thickness = 2

        # Store occupancy data
        occupancy_data.append((i, is_free, pos))
        
        # Draw on the video frame
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)

    # Display free space counter on video
    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (50, 50), scale=3,
                       thickness=5, offset=20, colorR=(0, 200, 0))
    
    return spaceCounter, occupancy_data

def processFrame(img):
    """
    Process frame for parking spot detection
    
    Args:
        img: The input frame
        
    Returns:
        imgDilate: Processed image ready for detection
    """
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
    
    return imgDilate