

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