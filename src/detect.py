import numpy as np
import cv2

def cube_dict_to_cube_str(cube_dict: dict):
    return_str = ''
    for side_str in cube_dict.values():
        return_str += side_str
    return return_str

# is candidate pixel in range of hsv values
def inrange(candidate: list, upper: list, lower: list):
    return candidate[0] <= upper[0] and \
    candidate[0] >= lower[0] and \
    candidate[1] <= upper[1] and \
    candidate[1] >= lower[1] and \
    candidate[2] <= upper[2] and \
    candidate[2] >= lower[2]

# 
def identify_face_colors(frame: np.array, face: list):
    face_colors = []
    for point in face:
        hsv_pixel_values = hsv_frame[point[1]][point[0]]
        # find color
        pixel_color = None
        for key, (upper, lower) in color_dict_HSV.items():
            if inrange(candidate=hsv_pixel_values, upper=upper, lower=lower):
                try:
                    pixel_color = cube_from_color[key]
                except KeyError:
                    break
                face_colors.append(pixel_color)
                break

    return face_colors

# frame face colors make face string
def make_face_str(face_num: int):
    # yah ik this is bad but I can't figure out better

    face_str = ''
    # face_num == 0 is top face
    if face_num == 0:
        face_str += face_colors[0]
        face_str += face_colors[1]
        face_str += face_colors[2]
        face_str += face_colors[3]
        face_str += face_colors[4]
        face_str += face_colors[5]
        face_str += face_colors[6]
        face_str += face_colors[7]
        face_str += face_colors[8]

    # face_num == 1 is right face
    if face_num == 1:
        face_str += face_colors[0]
        face_str += face_colors[1]
        face_str += face_colors[2]
        face_str += face_colors[3]
        face_str += face_colors[4]
        face_str += face_colors[5]
        face_str += face_colors[6]
        face_str += face_colors[7]
        face_str += face_colors[8]

    # face_num == 2 is left face
    if face_num == 2:
        face_str += face_colors[0]
        face_str += face_colors[1]
        face_str += face_colors[2]
        face_str += face_colors[3]
        face_str += face_colors[4]
        face_str += face_colors[5]
        face_str += face_colors[6]
        face_str += face_colors[7]
        face_str += face_colors[8]

    return face_str

# given 
def fetch_colors(frame: np.array, facelet_points: list, cube_dict:dict):
    # from https://stackoverflow.com/questions/36817133/identifying-the-range-of-a-color-in-hsv-using-opencv
    color_dict_HSV = {
        'black': [[180, 255, 30], [0, 0, 0]],
        'white': [[180, 18, 255], [0, 0, 231]],
        'red1': [[180, 255, 255], [159, 50, 70]],
        'red2': [[9, 255, 255], [0, 50, 70]],
        'green': [[89, 255, 255], [36, 50, 70]],
        'blue': [[128, 255, 255], [90, 50, 70]],
        'yellow': [[35, 255, 255], [25, 50, 70]],
        'purple': [[158, 255, 255], [129, 50, 70]],
        'orange': [[24, 255, 255], [10, 50, 70]],
        'gray': [[180, 18, 230], [0, 0, 40]]
    }

    cube_from_color = {
        'white': 'w',
        'gray': 'w',
        'red1': 'r',
        'red2': 'r',
        'green': 'g',
        'blue': 'b',
        'yellow': 'y',
        'orange': 'o',
    }

    # 
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    for face_num, face in enumerate(facelet_points):
        face_colors = identify_face_colors(frame=frame, face=face)
        # check if all 9 faces are identified
        try:
            assert len(face_colors) == 9
        # otherwise, return cube dicitonary unchanged
        except AssertionError:
            return cube_dict

        # print(face_colors)
        center_color_letter = face_colors[4]
        
        face_str = make_face_str(face_num=face_num)

        cube_dict[center_color_letter] = face_str

        # 
        print(cube_dict)


    return cube_dict

#
def detect_cube(sub_frame: np.array):
    RED = (0, 0, 255)
    return RED


