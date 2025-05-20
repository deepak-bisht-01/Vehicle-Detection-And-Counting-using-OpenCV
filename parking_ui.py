# parking_ui.py
# Contains UI-related functions for the parking system

import cv2
import numpy as np
import time

def create_parking_map(occupancy_data, MAP_WIDTH=400, MAP_HEIGHT=500, width=107, height=48):
    """
    Creates an enhanced visualization of the parking map
    
    Args:
        occupancy_data: List of tuples (position_index, is_free, position)
        MAP_WIDTH: Width of the map
        MAP_HEIGHT: Height of the map
        width: Width of parking spot in original video
        height: Height of parking spot in original video
        
    Returns:
        Numpy array with the parking map visualization
    """
    # Create a gradient background for more visual appeal
    gradient_bg = np.zeros((MAP_HEIGHT, MAP_WIDTH, 3), dtype=np.uint8)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            # Create a subtle gradient background
            blue = int(40 + (y/MAP_HEIGHT) * 20)
            green = int(40 + (y/MAP_HEIGHT) * 10)
            red = int(40 + (y/MAP_HEIGHT) * 5)
            gradient_bg[y, x] = (blue, green, red)
    
    map_canvas = gradient_bg.copy()
    
    # Draw a border and header area for the map
    cv2.rectangle(map_canvas, (0, 0), (MAP_WIDTH, MAP_HEIGHT), (100, 100, 100), 3)
    cv2.rectangle(map_canvas, (0, 0), (MAP_WIDTH, 60), (60, 60, 70), -1)
    
    # Draw title with shadow effect
    title = "PARKING MAP"
    # Shadow
    cv2.putText(map_canvas, title, (MAP_WIDTH//2 - 83, 38), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # Text
    cv2.putText(map_canvas, title, (MAP_WIDTH//2 - 85, 36), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Extract positions for scaling if available
    if occupancy_data and len(occupancy_data) > 0:
        min_x = min(pos[0] for _, _, pos in occupancy_data)
        max_x = max(pos[0] for _, _, pos in occupancy_data)
        min_y = min(pos[1] for _, _, pos in occupancy_data)
        max_y = max(pos[1] for _, _, pos in occupancy_data)
        
        # Calculate scaling factor to fit in our map
        scale_x = (MAP_WIDTH - 80) / max(1, (max_x - min_x + width))
        scale_y = (MAP_HEIGHT - 200) / max(1, (max_y - min_y + height))
        scale = min(scale_x, scale_y) * 0.85  # Keep some margin
        
        # Draw layout indicators - resembling parking lot lines
        center_x = MAP_WIDTH // 2
        parking_area_start_y = 80
        parking_area_height = MAP_HEIGHT - 200
        
        # Draw parking area outlines (showing lanes)
        cv2.rectangle(map_canvas, (40, parking_area_start_y), 
                     (MAP_WIDTH-40, parking_area_start_y + parking_area_height), 
                     (120, 120, 120), 2)
        
        # Draw center line for two-way traffic
        cv2.line(map_canvas, (center_x, parking_area_start_y), 
                (center_x, parking_area_start_y + parking_area_height), 
                (200, 200, 200), 1)
        
        # Add dashed lines to represent parking area divisions
        for y in range(parking_area_start_y, parking_area_start_y + parking_area_height, 20):
            for x in range(45, MAP_WIDTH-45, 10):
                if x != center_x-5 and x != center_x+5:  # Skip near the center line
                    cv2.line(map_canvas, (x, y), (x+5, y), (100, 100, 100), 1)
        
        # Draw each parking spot with 3D effect
        for i, (pos_idx, is_free, orig_pos) in enumerate(occupancy_data):
            # Scale and shift coordinates to fit in our map
            map_x = int(40 + (orig_pos[0] - min_x) * scale)
            map_y = int(80 + (orig_pos[1] - min_y) * scale)
            map_w = int(width * scale)
            map_h = int(height * scale)
            
            # Ensure the spot is within map boundaries
            if map_x + map_w > MAP_WIDTH - 10:
                continue
            
            if is_free:
                # Green gradient for free spots
                color1 = (0, 180, 0)  # Darker green
                color2 = (120, 255, 120)  # Lighter green
            else:
                # Red gradient for occupied spots
                color1 = (0, 0, 180)  # Darker red
                color2 = (120, 120, 255)  # Lighter red
            
            # Draw parking slot with 3D effect
            # Main rectangle
            cv2.rectangle(map_canvas, (map_x, map_y), (map_x + map_w, map_y + map_h), color1, -1)
            
            # Highlight edge for 3D effect
            highlight_offset = 3
            # Create lighter top-left edge
            points = np.array([[map_x, map_y], 
                              [map_x + map_w, map_y],
                              [map_x + map_w - highlight_offset, map_y + highlight_offset],
                              [map_x + highlight_offset, map_y + highlight_offset]], np.int32)
            cv2.fillPoly(map_canvas, [points], color2)
            
            points = np.array([[map_x, map_y], 
                              [map_x, map_y + map_h],
                              [map_x + highlight_offset, map_y + map_h - highlight_offset],
                              [map_x + highlight_offset, map_y + highlight_offset]], np.int32)
            cv2.fillPoly(map_canvas, [points], color2)
            
            # Draw border
            cv2.rectangle(map_canvas, (map_x, map_y), (map_x + map_w, map_y + map_h), (255, 255, 255), 1)
            
            # Add car icon for occupied spots
            if not is_free:
                # Simple car shape
                car_center_x = map_x + map_w // 2
                car_center_y = map_y + map_h // 2
                car_width = int(map_w * 0.6)
                car_height = int(map_h * 0.6)
                
                # Car body
                cv2.rectangle(map_canvas, 
                             (car_center_x - car_width//2, car_center_y - car_height//2),
                             (car_center_x + car_width//2, car_center_y + car_height//2),
                             (0, 0, 0), 1)
                
                # Car windows (simple line)
                window_y = car_center_y - car_height//4
                cv2.line(map_canvas, 
                        (car_center_x - car_width//4, window_y),
                        (car_center_x + car_width//4, window_y),
                        (0, 0, 0), 1)
                
                # Car wheels
                wheel_radius = max(1, int(car_height * 0.15))
                # Left wheels
                cv2.circle(map_canvas, 
                          (car_center_x - car_width//3, car_center_y + car_height//3),
                          wheel_radius, (0, 0, 0), 1)
                # Right wheels
                cv2.circle(map_canvas, 
                          (car_center_x + car_width//3, car_center_y + car_height//3),
                          wheel_radius, (0, 0, 0), 1)
            
            # Add spot number (only for some spots to avoid clutter)
            if i % 5 == 0:
                cv2.putText(map_canvas, f"{pos_idx+1}", 
                           (map_x + map_w//2 - 5, map_y + map_h//2 + 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # Draw statistics box with glossy effect
    free_count = sum(1 for _, is_free, _ in occupancy_data if is_free)
    total_count = len(occupancy_data)
    
    # Calculate occupancy percentage
    occupancy_percent = 0 if total_count == 0 else int((total_count - free_count) / total_count * 100)
    
    # Draw statistics panel
    stat_y = MAP_HEIGHT - 120
    
    # Main panel background with gradient
    for y in range(stat_y, stat_y+110):
        alpha = (y - stat_y) / 110  # Gradient factor
        color = (int(20 + 10 * alpha), int(20 + 10 * alpha), int(30 + 10 * alpha))
        cv2.line(map_canvas, (10, y), (MAP_WIDTH-10, y), color, 1)
    
    # Panel border with gloss effect
    cv2.rectangle(map_canvas, (10, stat_y), (MAP_WIDTH-10, stat_y+110), (100, 100, 120), 1)
    # Top gloss
    cv2.line(map_canvas, (11, stat_y+1), (MAP_WIDTH-11, stat_y+1), (150, 150, 170), 1)
    
    # Information text
    cv2.putText(map_canvas, "PARKING STATUS", (MAP_WIDTH//2 - 80, stat_y + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 220), 1)
    
    # Available spaces with icon
    cv2.rectangle(map_canvas, (30, stat_y + 35), (45, stat_y + 50), (0, 200, 0), -1)
    cv2.rectangle(map_canvas, (30, stat_y + 35), (45, stat_y + 50), (255, 255, 255), 1)
    cv2.putText(map_canvas, f"Available: {free_count}", (55, stat_y + 47), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 1)
    
    # Occupied spaces with icon
    cv2.rectangle(map_canvas, (30, stat_y + 60), (45, stat_y + 75), (0, 0, 200), -1)
    cv2.rectangle(map_canvas, (30, stat_y + 60), (45, stat_y + 75), (255, 255, 255), 1)
    cv2.putText(map_canvas, f"Occupied: {total_count - free_count}", (55, stat_y + 72), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 1)
    
    # Total spaces
    cv2.putText(map_canvas, f"Total Spaces: {total_count}", (30, stat_y + 95), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    # Occupancy percentage with visual indicator
    bar_length = 150
    bar_height = 12
    bar_x = MAP_WIDTH - bar_length - 30
    bar_y = stat_y + 60
    
    # Draw percentage text
    cv2.putText(map_canvas, f"Occupancy: {occupancy_percent}%", 
               (bar_x, bar_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    
    # Draw empty bar
    cv2.rectangle(map_canvas, (bar_x, bar_y), (bar_x + bar_length, bar_y + bar_height), 
                 (80, 80, 80), -1)
    cv2.rectangle(map_canvas, (bar_x, bar_y), (bar_x + bar_length, bar_y + bar_height), 
                 (150, 150, 150), 1)
    
    # Draw filled bar
    filled_length = int(bar_length * occupancy_percent / 100)
    
    # Calculate color based on occupancy (green to red gradient)
    bar_color = (0, 0, 200)  # Default red
    if occupancy_percent < 50:
        # Green to yellow gradient
        green = 200
        red = int(200 * occupancy_percent / 50)
        bar_color = (0, green, red)
    else:
        # Yellow to red gradient
        red = 200
        green = int(200 * (100 - occupancy_percent) / 50)
        bar_color = (0, green, red)
        
    cv2.rectangle(map_canvas, (bar_x, bar_y), (bar_x + filled_length, bar_y + bar_height), 
                 bar_color, -1)
    
    return map_canvas

def create_enhanced_ui(video_frame, parking_map, WINDOW_WIDTH=1200, WINDOW_HEIGHT=700, 
                    VIDEO_WIDTH=700, VIDEO_HEIGHT=500, MAP_WIDTH=400, MAP_HEIGHT=500):
    """
    Creates an enhanced UI layout combining video feed and parking map
    
    Args:
        video_frame: The processed video frame
        parking_map: The generated parking map visualization
        WINDOW_WIDTH, WINDOW_HEIGHT: Dimensions of the main window
        VIDEO_WIDTH, VIDEO_HEIGHT: Dimensions for the video section
        MAP_WIDTH, MAP_HEIGHT: Dimensions for the map section
        
    Returns:
        Numpy array with the combined UI visualization
    """
    # Create a base canvas with gradient
    ui_canvas = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)
    
    # Apply gradient background
    for y in range(WINDOW_HEIGHT):
        alpha = y / WINDOW_HEIGHT  # Gradient factor
        blue = int(15 + 10 * alpha)
        green = int(15 + 5 * alpha)
        red = int(15 + 5 * alpha)
        cv2.line(ui_canvas, (0, y), (WINDOW_WIDTH, y), (blue, green, red), 1)
    
    # Header panel
    header_height = 60
    # Gradient header
    for y in range(header_height):
        alpha = y / header_height  # Gradient factor
        color = (int(50 + 20 * (1-alpha)), int(50 + 20 * (1-alpha)), int(70 + 30 * (1-alpha)))
        cv2.line(ui_canvas, (0, y), (WINDOW_WIDTH, y), color, 1)
    
    # Bottom edge highlight for 3D effect
    cv2.line(ui_canvas, (0, header_height), (WINDOW_WIDTH, header_height), (100, 100, 120), 2)
    cv2.line(ui_canvas, (0, header_height+2), (WINDOW_WIDTH, header_height+2), (30, 30, 40), 1)
    
    # Add title with shadow effect
    title = "Smart Parking Detection System"
    # Shadow
    cv2.putText(ui_canvas, title, (WINDOW_WIDTH//2 - 198, 42), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    # Text
    cv2.putText(ui_canvas, title, (WINDOW_WIDTH//2 - 200, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 200, 255), 2)
    
    # Video frame area with border
    video_x, video_y = 50, 100
    # Draw border with 3D effect
    cv2.rectangle(ui_canvas, (video_x-3, video_y-3), 
                 (video_x+VIDEO_WIDTH+3, video_y+VIDEO_HEIGHT+3), 
                 (100, 100, 120), 1)
    cv2.rectangle(ui_canvas, (video_x-2, video_y-2), 
                 (video_x+VIDEO_WIDTH+2, video_y+VIDEO_HEIGHT+2), 
                 (50, 50, 60), 1)
    
    # Place video frame
    ui_canvas[video_y:video_y+VIDEO_HEIGHT, video_x:video_x+VIDEO_WIDTH] = video_frame
    
    # Add label for video
    label_y = video_y + VIDEO_HEIGHT + 15
    cv2.putText(ui_canvas, "Live Camera Feed", (video_x + VIDEO_WIDTH//2 - 80, label_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 200), 1)
    
    # Map area with border
    map_x = VIDEO_WIDTH + 70
    map_y = (WINDOW_HEIGHT - MAP_HEIGHT) // 2
    
    # Draw border with 3D effect
    cv2.rectangle(ui_canvas, (map_x-3, map_y-3), 
                 (map_x+MAP_WIDTH+3, map_y+MAP_HEIGHT+3), 
                 (100, 100, 120), 1)
    cv2.rectangle(ui_canvas, (map_x-2, map_y-2), 
                 (map_x+MAP_WIDTH+2, map_y+MAP_HEIGHT+2), 
                 (50, 50, 60), 1)
    
    # Place the parking map
    ui_canvas[map_y:map_y+MAP_HEIGHT, map_x:map_x+MAP_WIDTH] = parking_map
    
    # Add separator line between video and map
    separator_x = VIDEO_WIDTH + 50
    cv2.line(ui_canvas, (separator_x, 80), (separator_x, WINDOW_HEIGHT-20), (100, 100, 120), 1)
    cv2.line(ui_canvas, (separator_x+1, 80), (separator_x+1, WINDOW_HEIGHT-20), (30, 30, 40), 1)
    
    # Add footer with system information
    footer_y = WINDOW_HEIGHT - 30
    cv2.putText(ui_canvas, "Parking Detection System v2.0", (20, footer_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 170), 1)
    
    cv2.putText(ui_canvas, "Press 'Q' to exit", (WINDOW_WIDTH - 150, footer_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 170), 1)
    
    return ui_canvas
