import numpy as np
import cv2

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
def identify_point_colors(frame: np.array, point:tuple):
    hsv_pixel_values = frame[point[1]][point[0]]
    # find color
    pixel_color = '?'
    for key, (upper, lower) in color_dict_HSV.items():
        if inrange(candidate=hsv_pixel_values, upper=upper, lower=lower):
            try:
                pixel_color = cube_from_color[key]
            except KeyError:
                pass

    return pixel_color

# frame face colors make face string
def make_face_str(face_num:int, seen: int):
    # yah ik this is bad but I can't figure out better
    face_str = ''
    # face_num == 0 is top face
    
    if face_num == 0 and seen == 0:
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
    if face_num == 1 and seen == 0:
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
    if face_num == 2 and seen == 0:
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

# 
def make_axis_str(points: list, seen: int):
    axis_str = ''

    if seen == 0:
        for i in [0,1,2,3,4,5,6,7,8,20,23,26,19,22,25,18,21,24,17,16,15,14,13,12,11,10,9]:
            axis_str += points[i]

    elif seen == 1:
        for i in [9,10,11,12,13,14,15,16,17,24,21,18,25,22,19,26,23,20,0,1,2,3,4,5,6,7,8]:
            axis_str += points[i]

    return axis_str


# given 
def fetch_colors(
        frame: np.array, 
        facelet_points: list, 
        cube_str:str, 
        # cube_dict:dict, 
        seen: int
    ):
    # 
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    point_letters = []
    for point_num, point in enumerate(facelet_points):
        point_letter = identify_point_colors(frame=hsv_frame, point=point)
        point_letters.append(point_letter)

    axis_str = make_axis_str(points=point_letters, seen=seen)

    if seen == 0:
        cube_str = axis_str + cube_str[27:]
    elif seen == 1:
        cube_str = cube_str[:27] + axis_str

    print(f'Cube Str: {cube_str}')

    return cube_str, seen + 1

#
def detect_cube(sub_frame: np.array):
    RED = (0, 0, 255)
    return RED


