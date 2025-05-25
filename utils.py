import numpy as np

# define a hexagon outline for cube
def make_hex_points(scale:float, offset_x:int, offset_y:int):
    unit_hex_points = [
        (0,1),
        (-np.sqrt(3)/2, 0.5),
        (-np.sqrt(3)/2, -0.5),
        (0,-1),
        (np.sqrt(3)/2, -0.5),
        (np.sqrt(3)/2, 0.5),
    ]
    hex_points = [(round(scale*point[0]+offset_x), round(scale*point[1]+offset_y)) for point in unit_hex_points]
    return hex_points

# define a bounding box around hexagon
def make_bounding_box_points(scale:float, offset_x:int, offset_y:int):
    unit_bounding_box_points = [
        (1,1),
        (1,-1),
        (-1,-1),
        (-1,1),
    ]

    bounding_box_points = [(round(scale*point[0]+offset_x), round(scale*point[1]+offset_y)) for point in unit_bounding_box_points]
    return bounding_box_points

# define points of individual stickers (facelets)
def make_facelet_points(scale:float, offset_x:int, offset_y:int):
    # side of top face
    unit_facelet_points = [
        [
            (0.8, 0),    # 0
            (0.70, 20),  # 1
            (0.70, 40),  # 2
            (0.70, -20), # 3
            (0.5, 0),    # 4
            (0.4, 30),   # 5
            (0.70, -40), # 6
            (0.4, -30),  # 7
            (0.2, 0),    # 8
        ]
    ]
    facelet_points = []
    # rotate face three times
    for theta in [0, 120, 240]:
        for face in unit_facelet_points:
            scaled_face = []
            for point in face:
                scaled_coords = (
                        round((scale*(point[0]*np.cos(np.deg2rad(point[1] + theta - 90)))+offset_x)), 
                        round((scale*(point[0]*np.sin(np.deg2rad(point[1] + theta - 90)))+offset_y))
                    )
                facelet_points.append(scaled_coords)
    return facelet_points

