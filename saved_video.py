# system imports
import os
import cv2
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from rubik_solver import utils

# local imports
from src.detect import *
from src.serialize import *
from src.cube_string import *
from src.plotting_functions import *

# define color map
color_map = {
    "red": "#d50000",
    "orange": "#ff6d00",
    "yellow": "#ffeb3b",
    "green": "#388e3c",
    "blue": "#2962ff",
    "white": "#f5f5f5",
    "unknown": "#888888"
}


# given video on disk at video_path, obtain cube info and save to json
def main(video_path, target_frame=10):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return

    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print(f"Error: Could not read frame {target_frame} from {video_path}")
        return

    img = frame
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_mask, contour_overlay, all_contours_info, total_objects = extract_contours(img, hsv)
    # print(f"Detected {total_objects} total shapes.")

    cube_faces = build_faces(hsv, all_contours_info)
    save_faces_json(cube_faces, hsv)
    save_simplified_faces_json(cube_faces, hsv)
    visualize_results(hsv_mask, contour_overlay)


#
def process_frame(frame, frame_idx, output_dir, saved_colors):
    img = frame
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_mask, contour_overlay, all_contours_info, total_objects = extract_contours(img, hsv)
    # print(f"Frame {frame_idx}: Detected {total_objects} total shapes.")

    # Only proceed if exactly 9 shapes detected
    if total_objects == 9:
        cube_faces = build_faces(hsv, all_contours_info)
        if not cube_faces:
            print(f"Frame {frame_idx}: No cube faces built, skipping.")
            return

        # Get center tile color of first face
        cnt_center = cube_faces[0]["center"]["contour"]
        mask_center = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask_center, [cnt_center], -1, 255, -1)
        mean_hsv_center = cv2.mean(hsv, mask=mask_center)[:3]
        color_center = classify_color(mean_hsv_center)

        if color_center in saved_colors:
            # print(f"Frame {frame_idx}: Center color '{color_center}' already saved, skipping.")
            return
        else:
            saved_colors.add(color_center)
            # print(f"Frame {frame_idx}: Saving frame with new center color '{color_center}'.")

        # Save contour overlay image
        contour_img_path = os.path.join(output_dir, f"frame_{frame_idx:04d}_contours.png")
        cv2.imwrite(contour_img_path, contour_overlay)

        # Save JSON files
        json_path = os.path.join(output_dir, f"frame_{frame_idx:04d}_rubiks_cube_simplified.json")
        save_simplified_faces_json(cube_faces, hsv, filename=json_path)

        # Plot and save cube face visualization (same as before)...
        with open(json_path, "r") as f:
            cube_face_data = json.load(f)

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"Rubik's Cube Face Visualization - Frame {frame_idx}")

        if cube_face_data:
            face = cube_face_data[0]
            tiles = [face["center"]] + face["neighbors"]
            positions = [tile["centroid"] for tile in tiles]
            colors = [tile["color"] for tile in tiles]

            xs = [pos[0] for pos in positions]
            ys = [pos[1] for pos in positions]

            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

            norm_xs = [(x - min_x) / (max_x - min_x) if max_x != min_x else 0.5 for x in xs]
            norm_ys = [(y - min_y) / (max_y - min_y) if max_y != min_y else 0.5 for y in ys]

            margin = 0.1
            ax.set_xlim(-margin, 1 + margin)
            ax.set_ylim(-margin, 1 + margin)

            for x, y, c in zip(norm_xs, norm_ys, colors):
                circle = patches.Circle(
                    (x, 1 - y),
                    0.07,
                    facecolor=color_map.get(c, "#888888"),
                    edgecolor='black',
                    lw=2
                )
                ax.add_patch(circle)
                ax.text(x, 1 - y, c[0].upper(), ha='center', va='center', fontsize=10, color='black')

        face_img_path = os.path.join(output_dir, f"frame_{frame_idx:04d}_rubiks_cube_face.png")
        fig.savefig(face_img_path)
        plt.close(fig)
    else:
        # print(f"Frame {frame_idx}: Skipping saving because detected shapes != 9")
        pass


# process video frames of video at video_path, analyzing every step frames, save search data at output_dir
def process_video_frames(video_path: str, step: int = 10, output_dir: str = "output_frames"):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # print(f"Total frames in video: {frame_count}")

    frame_idx = 0
    processed_count = 0
    saved_colors = set()  # Track saved center colors

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step == 0:
            # print(f"Processing frame {frame_idx}")
            process_frame(frame, frame_idx, output_dir, saved_colors)
            processed_count += 1

        frame_idx += 1

    cap.release()
    # print(f"Processing complete. Processed {processed_count} frames. Outputs saved to '{output_dir}'.")


if __name__ == "__main__":
    os.system('clear')
    # path of video of cube
    video_file_path = "test_vids/config_1/cube.MOV"
    # print(f'Solving cube from video at: {video_file_path}')

    # process video frames
    process_video_frames(video_path=video_file_path)

    # format cube string for Kociemba solver
    cube_str = frame_data_to_string()

    BLUE = '\033[94m'
    ENDC = '\033[0m'

    # compute optimal instructions
    instructions = utils.solve(cube_str, 'Kociemba')[1:-1]
    print('-'*50)
    print(f'\nInstructions: {BLUE}{instructions}{ENDC}\n')
    print('-'*50)
