import os
import numpy as np
import cv2
import mediapipe as mp
from rubik_solver import utils

from src.detect import detect_cube, fetch_colors, cube_dict_to_cube_str
from utils import make_hex_points, make_bounding_box_points, make_facelet_points

## useful colors
RED = (0, 0, 255)
YELLOW = (0, 255, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)

def main():
    # Start webcam video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Error: Could not open webcam.")
    print("Press 'q' to quit.")

    scale = 250
    offset_x = 1000
    offset_y = 525

    seen = 0

    default_str = '????y????????b????????r????????g????????o????????w????'
    cube_str = default_str

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break
        
        # 
        hex_points = make_hex_points(scale=scale, offset_x=offset_x, offset_y=offset_y)
        bounding_box_points = make_bounding_box_points(scale=scale, offset_x=offset_x, offset_y=offset_y)
        facelet_points = make_facelet_points(scale=scale, offset_x=offset_x, offset_y=offset_y)

        # get bounding box sub_frame
        sub_frame = frame
        # sub_frame = frame[scale+offset_y:scale+offset_y][-scale+offset_x:scale+offset_x]
        
        # detect cube
        status_color = detect_cube(sub_frame=sub_frame)

        cv2.polylines(frame, np.array([hex_points]), True, status_color, 5)
        cv2.circle(frame, (offset_x, offset_y), 5, status_color, 10)
        # cv2.polylines(frame, np.array([bounding_box_points]), True, GREEN, 5)
        for point in facelet_points:
            cv2.circle(img=frame, center=point, radius=5, color=BLUE, thickness=2)

        # Display prediction on the frame
        # cube_str = cube_dict_to_cube_str(cube_dict=cube_dict)
        cv2.putText(frame, f"cube_str: {cube_str[:27]} | {cube_str[27:]}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)

        # solve cube if seen two axes and no unknown colors
        if seen == 2 and '?' not in cube_str:
            sol_str = utils.solve(cube_str, 'Kociemba')
            cv2.putText(frame, f"Solution: {sol_str}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)
            seen = 0
        
        # Show the video with predictions
        cv2.imshow("CubeSolver", frame)

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit on 'q'
            break
        elif key == ord('w'):
            scale *= 1.1
        elif key == ord('s'):
            scale *= 0.9
        elif key == ord('d'):
            offset_x -= 10
        elif key == ord('a'):
            offset_x += 10
        elif key == ord('c'): # NOTE debug feature, assumes rubiks cube detected
            cube_str, seen = fetch_colors(
                frame=frame, 
                facelet_points=facelet_points, 
                cube_str=cube_str, 
                seen=seen
            )
        elif key == ord(' '):
            if input_frame is not None:
                img_path = os.path.join("images", input("Specify image filename to save as: "))
                if "exit" in img_path:
                    continue
                cv2.imwrite(img_path, frame)
                print(f"Saved hand ROI to {img_path}.")
            else:
                print("No hand ROI to save.")

    # Release resources and destory the window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
