import cv2
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import matplotlib.patches as patches
import re


def classify_color(hsv_val):
    h, s, v = hsv_val

    # Red (usually needs two ranges to wrap around 0°)
    if 10 <= h <= 16 and s >= 150 and v >= 70:
        return "red"


    # Blue
    elif 95 <= h <= 125 and s >= 40 and v >= 110:
        return "blue"

    # Green
    elif 40 <= h <= 80 and s >= 50 and v >= 50:
        return "green"

    # Yellow
    elif 28 <= h <= 36 and s >= 100 and v >= 100:
        return "yellow"

    # Orange
    elif 23 <= h <= 29 and s >= 150 and v >= 100:
        return "orange"

    # White
    elif 25 <= h <= 35 and s <= 40 and v >= 200:
        return "white"




def get_color_mask(hsv):
    masks = []

    # Red
    masks.append(cv2.inRange(hsv, np.array([10, 150, 70]), np.array([16, 255, 255])))

    # Blue
    masks.append(cv2.inRange(hsv, np.array([95, 40, 110]), np.array([125, 255, 255])))

    # Green
    masks.append(cv2.inRange(hsv, np.array([40, 50, 50]), np.array([80, 255, 255])))

    # Yellow
    masks.append(cv2.inRange(hsv, np.array([28, 100, 100]), np.array([36, 255, 255])))

    # Orange
    masks.append(cv2.inRange(hsv, np.array([23, 150, 100]), np.array([29, 255, 255])))

    # White
    masks.append(cv2.inRange(hsv, np.array([25, 10, 200]), np.array([35, 40, 255])))

    full_mask = masks[0]
    for m in masks[1:]:
        full_mask = cv2.bitwise_or(full_mask, m)

    return full_mask


def extract_contours(img, hsv):
    hsv_mask = get_color_mask(hsv)
    contours, _ = cv2.findContours(hsv_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_overlay = img.copy()

    all_contours_info = []
    contour_index = 1

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 10000 < area < 30000:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = cnt[0][0]

            # Draw contour outline
            cv2.drawContours(contour_overlay, [cnt], -1, (0, 255, 0), 2)

            # ✅ Add text annotation with object number
            cv2.putText(
                contour_overlay,
                str(contour_index),
                (cX - 10, cY + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
                cv2.LINE_AA
            )

            info = {
                "contour": cnt,
                "centroid": (cX, cY),
                "area": area
            }

            all_contours_info.append(info)

            contour_index += 1

    total_objects = contour_index - 1
    print(f"Total objects detected: {total_objects}")

    return hsv_mask, contour_overlay, all_contours_info, total_objects



def identify_true_center_tile(contours_info):
    centroids = np.array([info["centroid"] for info in contours_info])
    if len(centroids) != 9:
        print("Warning: Expected 9 tiles for center identification")
        return None

    mean_centroid = np.mean(centroids, axis=0)
    distances = [np.linalg.norm(np.array(info["centroid"]) - mean_centroid) for info in contours_info]
    center_index = np.argmin(distances)
    return contours_info[center_index]


def build_faces(hsv, contours_info):
    true_center = identify_true_center_tile(contours_info)
    if true_center is None:
        return []

    center_centroid = np.array(true_center["centroid"])
    distances = []

    for other_info in contours_info:
        if np.array_equal(center_centroid, np.array(other_info["centroid"])):
            continue
        dist = np.linalg.norm(center_centroid - np.array(other_info["centroid"]))
        distances.append((dist, other_info))

    distances.sort(key=lambda x: x[0])
    closest_8 = [d[1] for d in distances[:8]]

    face = {
        "center": true_center,
        "neighbors": closest_8
    }
    return [face]


def save_faces_json(cube_faces, hsv, filename="rubiks_cube_faces.json"):
    cube_faces_serializable = []

    for face in cube_faces:
        cnt = face["center"]["contour"]
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        mean_hsv_center = cv2.mean(hsv, mask=mask)[:3]
        color_center = classify_color(mean_hsv_center)

        neighbors_serialized = []
        for n in face["neighbors"]:
            cnt_n = n["contour"]
            mask_n = np.zeros(hsv.shape[:2], dtype=np.uint8)
            cv2.drawContours(mask_n, [cnt_n], -1, 255, -1)
            mean_hsv_n = cv2.mean(hsv, mask=mask_n)[:3]
            color_n = classify_color(mean_hsv_n)

            neighbors_serialized.append({
                "centroid": n["centroid"],
                "area": n["area"],
                "color": {
                    "label": color_n,
                    "mean_hsv": [float(round(ch, 2)) for ch in mean_hsv_n]
                }
            })

        cube_faces_serializable.append({
            "center": {
                "centroid": face["center"]["centroid"],
                "area": face["center"]["area"],
                "color": color_center,
                "mean_hsv": [float(round(ch, 2)) for ch in mean_hsv_center]
            },
            "neighbors": neighbors_serialized
        })

    with open(filename, "w") as f:
        json.dump(cube_faces_serializable, f, indent=4)


def save_simplified_faces_json(cube_faces, hsv, filename="rubiks_cube_simplified.json"):
    simplified_data = []

    for face in cube_faces:
        cnt_center = face["center"]["contour"]
        mask_center = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask_center, [cnt_center], -1, 255, -1)
        mean_hsv_center = cv2.mean(hsv, mask=mask_center)[:3]
        color_center = classify_color(mean_hsv_center)

        neighbors_list = []
        for neighbor in face["neighbors"]:
            cnt_n = neighbor["contour"]
            mask_n = np.zeros(hsv.shape[:2], dtype=np.uint8)
            cv2.drawContours(mask_n, [cnt_n], -1, 255, -1)
            mean_hsv_n = cv2.mean(hsv, mask=mask_n)[:3]
            color_n = classify_color(mean_hsv_n)

            neighbors_list.append({
                "centroid": list(neighbor["centroid"]),
                "color": color_n
            })

        simplified_data.append({
            "center": {
                "centroid": list(face["center"]["centroid"]),
                "color": color_center
            },
            "neighbors": neighbors_list
        })

    with open(filename, "w") as f:
        json.dump(simplified_data, f, indent=4)


def visualize_results(hsv_mask, contour_overlay):
    overlay_rgb = cv2.cvtColor(contour_overlay, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(10, 8))
    plt.imshow(hsv_mask, cmap='gray')
    plt.title("Binary Mask")
    plt.axis('off')
    plt.show()

    plt.figure(figsize=(10, 8))
    plt.imshow(overlay_rgb)
    plt.title("Numbered Contours")
    plt.axis('off')
    plt.show()


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
    print(f"Detected {total_objects} total shapes.")

    cube_faces = build_faces(hsv, all_contours_info)
    save_faces_json(cube_faces, hsv)
    save_simplified_faces_json(cube_faces, hsv)
    visualize_results(hsv_mask, contour_overlay)

# Define color map
color_map = {
    "red": "#d50000",
    "orange": "#ff6d00",
    "yellow": "#ffeb3b",
    "green": "#388e3c",
    "blue": "#2962ff",
    "white": "#f5f5f5",
    "unknown": "#888888"
}

# Normalization function
def normalize(val, min_val, max_val):
    return (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5

# Function to plot cube faces
def plot_rubiks_cube_faces(json_file="rubiks_cube_simplified.json"):
    with open(json_file, "r") as f:
        cube_face_data = json.load(f)

    for idx, face in enumerate(cube_face_data):
        tiles = [face["center"]] + face["neighbors"]

        positions = [tile["centroid"] for tile in tiles]
        colors = [tile["color"] if isinstance(tile["color"], str) else tile["color"].get("label", "unknown") for tile in tiles]

        xs = [pos[0] for pos in positions]
        ys = [pos[1] for pos in positions]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        norm_xs = [normalize(x, min_x, max_x) for x in xs]
        norm_ys = [normalize(y, min_y, max_y) for y in ys]

        # Create plot
        fig, ax = plt.subplots(figsize=(6, 6))
        margin = 0.1
        ax.set_xlim(-margin, 1 + margin)
        ax.set_ylim(-margin, 1 + margin)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"Rubik's Cube Face {idx + 1}")

        for x, y, c in zip(norm_xs, norm_ys, colors):
            circle = patches.Circle(
                (x, 1 - y),  # Flip y-axis
                0.07,
                facecolor=color_map.get(c, "#888888"),
                edgecolor='black',
                lw=2
            )
            ax.add_patch(circle)
            ax.text(x, 1 - y, c[0].upper(), ha='center', va='center', fontsize=10, color='black')

        plt.show()

def process_frame(frame, frame_idx, output_dir, saved_colors):
    img = frame
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_mask, contour_overlay, all_contours_info, total_objects = extract_contours(img, hsv)
    print(f"Frame {frame_idx}: Detected {total_objects} total shapes.")

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
            print(f"Frame {frame_idx}: Center color '{color_center}' already saved, skipping.")
            return
        else:
            saved_colors.add(color_center)
            print(f"Frame {frame_idx}: Saving frame with new center color '{color_center}'.")

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
        print(f"Frame {frame_idx}: Skipping saving because detected shapes != 9")


def process_video_frames(video_path, step=10, output_dir="output_frames"):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file at {video_path}")
        return

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames in video: {frame_count}")

    frame_idx = 0
    processed_count = 0
    saved_colors = set()  # Track saved center colors

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step == 0:
            print(f"Processing frame {frame_idx}")
            process_frame(frame, frame_idx, output_dir, saved_colors)
            processed_count += 1

        frame_idx += 1

    cap.release()
    print(f"Processing complete. Processed {processed_count} frames. Outputs saved to '{output_dir}'.")

def build_grid(face):
    tiles = face["neighbors"] + [face["center"]]
    tiles_sorted_y = sorted(tiles, key=lambda t: t["centroid"][1])
    rows = [tiles_sorted_y[i:i+3] for i in range(0, 9, 3)]
    grid = [sorted(row, key=lambda t: t["centroid"][0]) for row in rows]
    return grid

def rotate_clockwise(grid):
    size = len(grid)
    return [
        [grid[size - 1 - col][row] for col in range(size)]
        for row in range(size)
    ]

def rotate_counterclockwise(grid):
    size = len(grid)
    return [
        [grid[col][size - 1 - row] for col in range(size)]
        for row in range(size)
    ]

def extract_number(filename):
    match = re.search(r'frame_(\d+)_', filename)
    return int(match.group(1)) if match else -1

def orientation():
    folder = 'output_frames'
    files = [f for f in os.listdir(folder) if f.endswith('.json')]
    files_sorted = sorted(files, key=extract_number)

    all_colors = []

    for file_index, filename in enumerate(files_sorted):
        filepath = os.path.join(folder, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)

        face = data[0] if isinstance(data, list) else data
        grid = build_grid(face)
        grid = rotate_clockwise(grid)

        # DONT NEED TO USE FOR VIDEO 1
        # if file_index == 4:  # 5th face (top)
        #     grid = rotate_clockwise(grid)
        # elif file_index == 5:  # 6th face (bottom)
        #     grid = rotate_counterclockwise(grid)

        # Collect all color initials lowercase for this grid
        all_colors.extend(tile['color'][0].lower() for row in grid for tile in row)

    # Join all color initials into one big string
    big_color_string = ''.join(all_colors)
    return big_color_string

def reorder_faces_for_solver(color_string):
    if len(color_string) != 54:
        raise ValueError("Color string must be 54 characters.")

    # Your scan order: F, R, B, L, U, D
    F = color_string[0:9]
    R = color_string[9:18]
    B = color_string[18:27]
    L = color_string[27:36]
    U = color_string[36:45]
    D = color_string[45:54]

    # Desired solver order: U, R, F, D, L, B
    return U + R + F + D + L + B

def draw_rubiks_cube(facelets):
        if len(facelets) != 54:
            raise ValueError("Input string must have 54 characters.")

        # Mapping from face index to position in the net (row, col)
        face_positions = {
            'U': (0, 1),
            'L': (1, 0),
            'F': (1, 1),
            'R': (1, 2),
            'B': (1, 3),
            'D': (2, 1),
        }

        # Order of faces in input
        face_order = ['U', 'R', 'F', 'D', 'L', 'B']

        # Color map
        color_map = {
            'w': 'white',
            'y': 'yellow',
            'r': 'red',
            'o': 'orange',
            'b': 'blue',
            'g': 'green'
        }

        # Create empty 9x12 grid (each face 3x3, 4 faces wide, 3 faces high)
        grid = np.full((9, 12), '', dtype=object)

        for i, face in enumerate(face_order):
            row_off, col_off = face_positions[face]
            row_off *= 3
            col_off *= 3
            face_data = facelets[i * 9:(i + 1) * 9]
            for j in range(3):
                for k in range(3):
                    color_char = face_data[j * 3 + k]
                    grid[row_off + j][col_off + k] = color_map.get(color_char, 'black')

        # Plotting
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xticks([])
        ax.set_yticks([])
        for i in range(9):
            for j in range(12):
                if grid[i][j] != '':
                    square = plt.Rectangle((j, 8 - i), 1, 1, facecolor=grid[i][j], edgecolor='black')
                    ax.add_patch(square)

        ax.set_xlim(0, 12)
        ax.set_ylim(0, 9)
        ax.set_aspect('equal')
        plt.show()



if __name__ == "__main__":
    video_file_path = "test_vids/config_1/cube.MOV"
    process_video_frames(video_file_path)

    cube = reorder_faces_for_solver(orientation())
    print(cube)

    draw_rubiks_cube(cube)

    from rubik_solver import utils
    print(len(cube))
    utils.solve(cube, 'Kociemba')
    
