import json
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

## various plotting functions

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

# plot contour mask over hsv image
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


# Normalization function
def normalize(val, min_val, max_val):
    return (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5


# plot cube faces from json file
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

# draw rubiks cube net from facelets
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

