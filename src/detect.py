
import os
import re
import cv2
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from .cube_string import build_grid

# given hsv values, discretize into the 6 colors of the cube
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


# 
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


# get contours from image
def extract_contours(img, hsv):
    hsv_mask = get_color_mask(hsv)
    contours, _ = cv2.findContours(hsv_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # NOTE render contours on image
    contour_overlay = img 

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

            # draw contour outline
            cv2.drawContours(contour_overlay, [cnt], -1, (0, 255, 0), 2)

            # add text annotation with object number
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

    # if total_objects >= 9: print(f"Total objects detected: {total_objects}")

    return hsv_mask, contour_overlay, all_contours_info, total_objects


# 
def identify_true_center_tile(contours_info):
    centroids = np.array([info["centroid"] for info in contours_info])
    if len(centroids) != 9:
        print("Warning: Expected 9 tiles for center identification")
        return None

    mean_centroid = np.mean(centroids, axis=0)
    distances = [np.linalg.norm(np.array(info["centroid"]) - mean_centroid) for info in contours_info]
    center_index = np.argmin(distances)
    return contours_info[center_index]


# 
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


# detect a side in a given frame
def detect_side(frame: np.array, saved_colors: set):
    img = frame
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hsv_mask, contour_overlay, all_contours_info, total_objects = extract_contours(img, hsv)

    # only proceed if exactly 9 shapes detected
    if total_objects == 9:
        # determine cube_faces from contour information
        cube_faces = build_faces(hsv, all_contours_info)
        # if nothing build, status is TODO
        if not cube_faces:
            return

        # Get center tile color of first face
        first_face = cube_faces[0]
        cnt_center = first_face["center"]["contour"]
        mask_center = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask_center, [cnt_center], -1, 255, -1)
        mean_hsv_center = cv2.mean(hsv, mask=mask_center)[:3]
        color_center = classify_color(mean_hsv_center)

        print(f'Color center: {color_center}')

        if color_center in saved_colors:
            return
        else:
            saved_colors.add(color_center)


        grid = build_grid(face=first_face)
        print(f'Grid: {grid}')
