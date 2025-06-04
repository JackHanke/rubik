import os
import re
import json

## functions for constructing cube string for rubik_solver cube string

# 
def rotate_clockwise(grid):
    size = len(grid)
    return [
        [grid[size - 1 - col][row] for col in range(size)]
        for row in range(size)
    ]

# 
def rotate_counterclockwise(grid):
    size = len(grid)
    return [
        [grid[col][size - 1 - row] for col in range(size)]
        for row in range(size)
    ]

'''
entries of grid represent: 

0 1 2
3 4 5
6 7 8

'''

def build_grid(face):
    tiles = face["neighbors"] + [face["center"]]
    tiles_sorted_y = sorted(tiles, key=lambda t: t["centroid"][1])
    rows = [tiles_sorted_y[i:i+3] for i in range(0, 9, 3)]
    grid = [sorted(row, key=lambda t: t["centroid"][0]) for row in rows]
    grid = rotate_clockwise(grid)
    return grid


#
def extract_number(filename):
    match = re.search(r'frame_(\d+)_', filename)
    return int(match.group(1)) if match else -1


# take grids with arbitrary centers and orientation, in the order produced by cube rotations: y y y y x' x x and returns fixed cube string specified by README
# NOTE there are better ways to do this but this is the only one I could figure out
def grids_and_orientation_to_str(grids: list, orientation_list: list[str]):
    cube_str = ''

    if orientation_list == ['r', 'y']:
        cube_str += ''.join([grids[1][i] for i in [2,5,8,1,4,7,0,3,6]])
        cube_str += ''.join([grids[4][i] for i in [2,5,8,1,4,7,0,3,6]])
        cube_str += ''.join([grids[0][i] for i in [2,5,8,1,4,7,0,3,6]])
        cube_str += ''.join([grids[5][i] for i in [2,5,8,1,4,7,0,3,6]])
        cube_str += ''.join([grids[2][i] for i in [6,3,0,7,4,1,8,5,2]])
        cube_str += ''.join([grids[3][i] for i in [2,5,8,1,4,7,0,3,6]])
    elif orientation_list == ['o', 'y']:
        pass
    elif orientation_list == ['b', 'o']:
        pass

    # TODO the other 23 cases 

    return cube_str

# map saved frame data in output_frames to fixed orientation cube string
def frame_data_to_string():
    folder = 'output_frames'
    files = [f for f in os.listdir(folder) if f.endswith('.json')]
    files_sorted = sorted(files, key=extract_number)

    # get orientation list, which contains a list of two center colors
    orientation_list, grids = [], []
    for file_index, filename in enumerate(files_sorted):
        # 
        filepath = os.path.join(folder, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        #
        if file_index < 2:
            color_first_letter = data[0]['center']['color'][0]
            orientation_list.append(color_first_letter)

        # 
        face = data[0] if isinstance(data, list) else data

        # build the grid, rotate clockwise to align with relative orientation
        grid = build_grid(face)

        # turn maleable 
        g = [val['color'][0] for row in grid for val in row ]
        grids.append(g)

    # Join all color initials into one big string
    cube_str = grids_and_orientation_to_str(grids=grids, orientation_list=orientation_list)

    return cube_str

# 
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
