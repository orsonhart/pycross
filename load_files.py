# Import required modules.
import json
from objects import *
import os
import tkinter as tk

# Takes a list and merge sorts it.
def merge_sort(input_list):
    if len(input_list) > 1:
        # Split the input list into two lists.
        mid = len(input_list)//2
        left_list, right_list = input_list[:mid], input_list[mid:]
        # Return the merge of two sorted sub lists.
        return merge(merge_sort(left_list),merge_sort(right_list))
    
    # If the list has length 1 (ergo it is already sorted) then return the list.
    else:
        return input_list

# Takes two sorted list and merges them.
def merge(list1, list2):
    # Create an empty list which the input lists will merge into.
    merged_list = []

    # Whilst both lists have data in them...
    while len(list1)>0 and len(list2)>0:
        # Remove the smallest item from the front of either list
        # and append it to the merged list.
        if list1[0].lower() < list2[0].lower():
            merged_list.append(list1[0])
            list1.pop(0)
        else:
            merged_list.append(list2[0])
            list2.pop(0)
            
    # Once one list is empty, append the rest of the other list to the merged list.
    if len(list1) == 0:
        merged_list += list2        
    else:
        merged_list += list1

    # Return the merged list.
    return merged_list

# Write user specified configuration to file.
def write_config_file(width, height, border_size, thick_border_size, filename= "config.json"):
    # Create dictionary from parameters.
    grid_dict = {"screen_width":width,
                "screen_height":height,
                "border_size":border_size,
                "thick_border_size":thick_border_size}
    
    # Write the information to a json file.
    with open(filename, "w") as file:
        json.dump(grid_dict, file)
                
# Return user configuration parameters.
def load_config_file(filename = "config.json"):

    # Load json file to dictionary.
    with open(filename, "r") as file:
        config = json.loads(file.read())

    # Error checking:
    # If either border is set to 0, set to "default" value.
    if config["thick_border_size"] <= 0:
        config["thick_border_size"] = 0.2
    if config["border_size"] <= 0:
        config["border_size"] = 0.1

    # Make sure thick border is not greater than 1.
    if config["thick_border_size"] > 1:
        config["thick_border_size"] = 1
    # Make sure thin border is not greater than 0.5.
    if config["border_size"] > 0.5:
        config["border_size"] = 0.5
    
    # Ensure thick border is not thinner than normal border.
    if config["thick_border_size"] < config["border_size"]:
        config["thick_border_size"] = config["border_size"]
    
    # Return the parameters.
    return config["screen_width"], config["screen_height"], config["border_size"], config["thick_border_size"]

# Load a grid from a file.
def load_grid_from_file(filename):
    # Load json file to dictionary.
    with open(filename, "r") as file:
        grid_info = json.loads(file.read())

    # Error checking:
    x_sum = 0
    y_sum = 0
    # Calculate sum of horizontal clues.
    for nums in grid_info["x_nums"]:
        for num in nums:
            x_sum += num

    # Calculate sum of vertical clues.
    for nums in grid_info["y_nums"]:
        for num in nums:
            y_sum += num

    # If sum of horizontal and vertical clues are not the same...
    if x_sum != y_sum:
        # Throw an error.
        print("Invalid Grid")
        raise Exception("Invalid Grid")
    
    # Create a grid object from the dictionary.
    grid = Grid(
        grid_info["width"],
        grid_info["height"],
        grid_info["x_nums"],
        grid_info["y_nums"]
    )

    # If the file contains grid data:
    if "data_nums" in grid_info:
        # Convert the numbers to cells with corresponding states and populate
        # a 2-dimensional list with the cells.
        data_nums = grid_info["data_nums"]
        data = []
        for row in range(grid.height):
            data.append([])
            for col in range(grid.width):
                data[row].append(Cell(col, row, data_nums[row][col]))
        # Assign the data to the grid.
        grid.data = data

    # Return the grid object.
    return grid

# Make a puzzle file from the grid state.
def make_file_from_grid(grid, filename):
    # Get the numbers of the clues which would represent the current grid state.
    generated_x_nums, generated_y_nums = grid.generate_nums_from_grid()

    # Create a dictionary which stores all the information about the grid.
    grid_dict = {"width":grid.width,
                "height":grid.height,
                "x_nums":generated_x_nums,
                "y_nums":generated_y_nums}

    # Write the information to a json file.
    with open(filename, "w") as file:
        json.dump(grid_dict, file)

# Make a save from the grid state.
def make_save_from_grid(grid, filename):
    # Convert the clue objects to numbers (Clue objects are unhashable).
    x_nums, y_nums = grid.get_nums_from_clues()
    
    # Convert the cell objects to numbers (Cell objects are unhashable).
    data_nums = []
    for row in range(grid.height):
        data_nums.append([])
        for col in range(grid.width):
            data_nums[row].append(grid.data[row][col].state)

    # Create a dictionary which stores all the information about the save.
    grid_dict = {"width":grid.width,
                "height":grid.height,
                "x_nums":x_nums,
                "y_nums":y_nums,
                "data_nums":data_nums}

    # Write the information to a json file.
    with open(filename, "w") as file:
        json.dump(grid_dict, file)