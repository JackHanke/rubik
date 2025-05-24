import os
import numpy as np
import cv2
import mediapipe as mp

from src.detect import detect_cube, fetch_colors, cube_dict_to_cube_str


def main():
    # Start webcam video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Error: Could not open webcam.")
    print("Press 'q' to quit.")

    scale = 250
    offset_x = 1000
    offset_y = 525

    faces_seen = 0

    default_str = '????y????????b????????r????????g????????o????????w????'

    default_cube_dict = {
        'y':'????y????', 
        'b':'????b????', 
        'r':'????r????', 
        'g':'????g????', 
        'o':'????o????', 
        'w':'????w????', 
    }
    cube_dict = default_cube_dict.copy()


    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        ## draw guidelines
        RED = (0, 0, 255)
        YELLOW = (0, 255, 255)
        GREEN = (0, 255, 0)
        BLUE = (255, 0, 0)
        # 
        unit_hex_points = [
            (0,1),
            (-np.sqrt(3)/2, 0.5),
            (-np.sqrt(3)/2, -0.5),
            (0,-1),
            (np.sqrt(3)/2, -0.5),
            (np.sqrt(3)/2, 0.5),
        ]
        # 
        unit_facelet_points = [
            [
                (0.8, 0),    # 0
                (0.70, 20),  # 1
                # (0.65, 40),  # 2
                # (0.70, -20), # 3
                # (0.5, 0),    # 4
                # (0.4, 30),   # 5
                # (0.65, -40), # 6
                # (0.4, -30),  # 7
                # (0.2, 0),    # 8
            ]
        ]
        # 
        unit_bounding_box_points = [
            (1,1),
            (1,-1),
            (-1,-1),
            (-1,1),
        ]

        hex_points = [(round(scale*point[0]+offset_x), round(scale*point[1]+offset_y)) for point in unit_hex_points]
        bounding_box_points = [(round(scale*point[0]+offset_x), round(scale*point[1]+offset_y)) for point in unit_bounding_box_points]
        facelet_points = []
        for theta in [120]:
        # for theta in [0, 120]:
            for face in unit_facelet_points:
                scaled_face = []
                for point in face:
                    
                    # print(mag*np.cos(theta), mag*np.sin(theta))
                    scaled_face.append(
                        (
                            round((scale*(point[0]*np.cos(np.deg2rad(point[1] + theta - 90)))+offset_x)), 
                            round((scale*(point[0]*np.sin(np.deg2rad(point[1] + theta - 90)))+offset_y))
                        )
                    )
                facelet_points.append(scaled_face)

        # get bounding box sub_frame
        # sub_frame = frame[scale+offset_y:scale+offset_y][-scale+offset_x:scale+offset_x]
        sub_frame = frame
        
        # detect cube
        status_color = detect_cube(sub_frame=sub_frame)

        # img = img = np.zeros((200, 500, 3), np.uint8)
        cv2.polylines(frame, np.array([hex_points]), True, status_color, 5)
        # cv2.circle(frame, (offset_x, offset_y), 5, status_color, 10)
        # cv2.polylines(frame, np.array([bounding_box_points]), True, GREEN, 5)
        for face in facelet_points:
            for coords in face:
                cv2.circle(img=frame, center=coords, radius=5, color=BLUE, thickness=1)

        # Display prediction on the frame
        cube_str = cube_dict_to_cube_str(cube_dict=cube_dict)
        cv2.putText(frame, f"cube_str: {cube_str}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, RED, 2)
        
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
        elif key == ord('t'): # NOTE debug feature, assumes rubiks cube detected
            cube_dict = fetch_colors(frame=frame, facelet_points=facelet_points, cube_dict=cube_dict)
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
