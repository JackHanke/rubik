import cv2
import json
import numpy as np

from .detect import classify_color

# 
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

# 
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

