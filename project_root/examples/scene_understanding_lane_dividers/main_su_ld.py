import cv2
import numpy as np
import random
import os

def detect_and_draw_lines(image_path):
    """
    Detects and draws lines on an image using the Hough Line Transform.
    Args:
        image_path (str): The path to the input image file.
    Returns:
        None
    This function performs the following steps:
    1. Loads the original image in grayscale.
    2. Applies Canny Edge Detection (or uses the original image if it's already binary).
    3. Uses the Hough Line Transform to detect lines in the edge-detected image.
    4. Converts the grayscale image back to BGR to draw colored lines.
    5. Draws the detected lines on the original image in random colors.
    6. Displays the image with the detected lines.
    Note:
        - If the image cannot be loaded, an error message is printed and the function returns.
        - If no lines are detected, a message is printed indicating that no lines were found.
    """        
    #1. This is the distance resolution of the accumulator in pixels. It refers to how finely you want to search for lines in terms of distance. A value of 1 means the distance resolution is 1 pixel.
    # Increasing the value will reduce the resolution and could lead to missed details, while decreasing it increases computational complexity.
    
    #2. This parameter specifies the precision of the distance measurement in the accumulator. A value of 1 means that the distance resolution is 1 pixel.
    
    
    #3. This parameter specifies the precision of the angle measurement in the accumulator. np.pi / 180 converts degrees to radians, setting the angle resolution to 1 degree.
    # Threshold (threshold=100):
    
    # 4. threshold=100: This is the threshold for the number of intersections in the Hough accumulator to detect a line.
    # It means that, to consider a line as detected, it must have at least 100 points (votes) that fall along it. Lowering this value makes the detection more sensitive, meaning even faint lines are detected, while higher values detect only strong, prominent lines.

    #5. minLineLength=50: This parameter specifies the minimum length of a line that should be detected, in pixels.
    # If a line segment is shorter than minLineLength, it is discarded. This helps eliminate small noise-like segments and only keeps meaningful, longer lines. Increasing this value can help avoid detecting small, spurious line segments.    


    #6. maxLineGap=10: This parameter is the maximum allowed gap between line segments to treat them as a single line.
    # If two points on the same line have a gap less than maxLineGap, they will be connected into a single line. This is useful for bridging breaks in detected lines. Increasing this value will combine more segments into longer lines, while lowering it will treat them as


    ### How to Fine-tune These Parameters:
    # threshold: The higher the threshold, the fewer lines are detected. You may need to lower it if you see that many valid lines are missing, or raise it if too many false detections are appearing.

    # minLineLength: If your lines are breaking into smaller segments, try lowering minLineLength. If you only care about prominent lines, increase it.

    # maxLineGap: If lines are detected as multiple separate segments, try increasing maxLineGap to bridge them.


    
    # Load the original image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Error: Unable to load the image.")
        return
    
        
    # Apply Canny Edge Detection
    # Use the original image as edges directly if it's binary
    edges = image    # plot the edges image    
    
    # Use Hough Line Transform to detect lines
    min_dist_between_lines_meters = 0.45
    min_line_length_meters = 25              
    max_gap_between_lines_meters = 55
    
    pixl_2_m_ratio = 0.18
    
    min_dist_between_lines_pixels = round(min_dist_between_lines_meters / pixl_2_m_ratio)
    
    rho_dist_pxls = min_dist_between_lines_pixels
    angle_res = np.pi / 180 # * 45.10   #np.pi / 180
    votes_threshold= 200  #threshold=100:
    minLineLength_pxls=round(min_line_length_meters/pixl_2_m_ratio)   #minLineLength=50:
    maxLineGap_pxls = round(max_gap_between_lines_meters/pixl_2_m_ratio) #maxLineGap=10:
    
    lines = cv2.HoughLinesP(edges, rho=rho_dist_pxls, theta=angle_res, threshold=votes_threshold, minLineLength=minLineLength_pxls, maxLineGap=maxLineGap_pxls)
 
    # print number of lines found
    if lines is not None:
        print(f"Number of lines detected: {len(lines)}")
    else:
        print("No lines detected.")
        
    # Convert the grayscale image back to BGR to draw colored lines    
    color_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Draw the lines on the original image in random colors
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            cv2.line(color_image, (x1, y1), (x2, y2), color, 2)
    # else:
    #     print("No lines detected.")

    # Show the image with the detected lines
    # Rescale the image for display
    scale_percent = 100  # percent of original size
    width = int(color_image.shape[1] * scale_percent / 100)
    height = int(color_image.shape[0] * scale_percent / 100)
    dim = (width, height)
    
    # Resize image
    resized_image = cv2.resize(color_image, dim, interpolation=cv2.INTER_AREA)
    
    # Show the resized image with detected lines
    cv2.imshow('Detected Lines', resized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # define iamges directory
    images_dir = '/home/thh3/data/lane_dividers_intersection/'
    
    # read images list from directory with prefix 'dashed_'
    images_list = os.listdir(images_dir)
    dashed_line_images_list = [img for img in images_list if 'dashed_' in img]    
    continuous_line_images_list = [img for img in images_list if 'continuous_' in img]
    
    
            
    # detect and draw lines for continuous lines images
    for img in continuous_line_images_list:
        image_path = os.path.join(images_dir, img)
        detect_and_draw_lines(image_path)
        # pause until user press any key
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        
    # detect and draw lines for dashed lines images
    for img in dashed_line_images_list:
        image_path = os.path.join(images_dir, img)
        detect_and_draw_lines(image_path)
        # pause until user press any key
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        
    print("All images are processed.")
        
        
        
        
        
        
        

