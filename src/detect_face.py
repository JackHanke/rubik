# NOTE old functions that may be useful idk

# 
def cube_dict_to_cube_str(cube_dict: dict):
    return_str = ''
    for side_str in cube_dict.values():
        return_str += side_str
    return return_str

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

def fetch_colors():
    for face_num, face in enumerate(facelet_points):
        face_colors = identify_face_colors(frame=hsv_frame, face=face)
        # check if all 9 faces are identified
        try:
            assert len(face_colors) == 9
        # otherwise, return cube dicitonary unchanged
        except AssertionError:
            return cube_dict, seen

        # print(face_colors)
        center_color_letter = face_colors[4]
        
        face_str = make_face_str(face_num=face_num)

        cube_dict[center_color_letter] = face_str

        # 
        print(cube_dict)



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