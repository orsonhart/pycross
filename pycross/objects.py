import random
import solver
import pygame

class Grid:
    def __init__(self, width, height, x_nums, y_nums):
        # width, height: integers.
        # x_clues, y_clues: list of lists of integers.
        self.width = width
        self.height = height

        # Generate a grid.
        self.data = self._generate_grid(width,height)
        
        # Generate lists of clues objects.
        self.x_clues = self._generate_clues(x_nums)
        self.y_clues = self._generate_clues(y_nums)

    # Populate the grid randomly, each cell having the same chance to be filled.
    def fill_randomly(self, chance):
        # Iterate through every cell.
        for row in self.data:
            for cell in row:
                cell.state = 0
                # Set as filled if random number between 0 and 1 is less than chance.
                if random.random() < chance:
                    cell.state = 1
        
    # Create an grid populated with unmarked cells.
    def _generate_grid(self, width, height):
        data = []
        for _ in range(height):
            data.append([]*width) 
        
        for y in range(height):
            for x in range(width):
                data[y].append(Cell(x,y))
                
        return data

    # Convert a list of lists of integers to clues with matching values.
    def _generate_clues(self, nums_list):
        clues_list = []
        for i in range(len(nums_list)):
            clues_list.append([])
            for j in range(len(nums_list[i])):
                clues_list[i].append(Clue(nums_list[i][j]))
                
        return clues_list

    # Check if the grid is complete.
    def is_complete(self):
        # For each column...
        for i in range(self.width):
            col = [row[i] for row in self.data]
            # If the block pattern does not match the clues then it is not complete.
            if self._get_block_pattern(col) != [clue.value for clue in self.x_clues[i]]:
                return False

        # For each row...
        for i in range(self.height):
            row = self.data[i]
            # If the block pattern does not match the clues then it is not complete.
            if self._get_block_pattern(row) != [clue.value for clue in self.y_clues[i]]:
                return False

        return True

    # Calculate the block pattern of a line of cells.
    # This returns the values of clues which describe the line.
    def _get_block_pattern(self, line):
        block_pattern = []
        
        # For every cell in the line.
        for i in range(len(line)):
            # If the cell is included...
            if line[i].state == 1:
                # If the cell is the first in the line...
                if i == 0:
                    # Create a new clue.
                    block_pattern.append(1)
                else:
                    # If the cell before is also included...
                    if line[i-1].state == 1:
                        # Increment final clue.
                        block_pattern[-1] += 1
                    else:
                        # Create a new clue
                        block_pattern.append(1)

        return block_pattern

    # Convert the values of the clues to a list of lists of integers.
    # Used to save to JSON file as clue objects are not-hashable.
    def get_nums_from_clues(self):
        x_nums = []
        y_nums = []
        # For each set of clues...
        for clues in self.x_clues:
            nums = []
            # For each clue...
            for clue in clues:
                # Append the value of the clue.
                nums.append(clue.value)
            # Append the list of values of clues of a line.
            x_nums.append(nums)

        # For each set of clues...
        for clues in self.y_clues:
            nums = []
            # For each clue...
            for clue in clues:
                # Append the value of the clue.
                nums.append(clue.value)
            # Append the list of values of clues of a line.
            y_nums.append(nums)
        return x_nums, y_nums

    # Solves the grid.
    def solve(self):
        # Convert the clues to integers for processing.
        x_nums, y_nums = self.get_nums_from_clues()
        # Try to solve the puzzle
        try:
            # Use solving algorithm to create a grid of 1s and 2s.
            ans = solver.solve_grid(self.width, self.height, x_nums, y_nums)
            solution, only = ans[0], ans[1]
            # Iterate through each number in the solution.
            for y, row in enumerate(solution):
                for x, cell in enumerate(row):
                    # If cell is included in solution, mark it as included in the grid.
                    if cell == 1:
                        self.data[y][x].state = 1
                    # IF cell is not included in solution, mark it as excluded in the grid.
                    else:
                        self.data[y][x].state = 2
            # If it is the only solution...
            if only:
                print("only")
            else:
                print("not only")
        # If puzzle cannot be solved then the puzzle is impossible.
        except IndexError:
            print("IMPOSSIBLE PUZZLE")

    # Convert the included cells within the grid into numbers which represent the values
    # of clues which describe the pattern.
    def generate_nums_from_grid(self):
        x_nums = []
        y_nums = []
        # For each column...
        for i in range(self.width):
            col = [row[i] for row in self.data]
            # Add the block pattern of the column to the x_nums.
            x_nums.append(self._get_block_pattern(col))

        # For each row...
        for i in range(self.height):
            row = self.data[i]
            # Add the block pattern of the row to the y_nums.
            y_nums.append(self._get_block_pattern(row))

        return x_nums, y_nums

# Inherits rect property from pygame Sprite class.
class Clue(pygame.sprite.Sprite):
    # Initialise clue.
    def __init__(self, value, marked=False):
        self.value = value
        self.marked = False
        self.rect = None

    def __repr__(self):
        return str(self.value)

# Inherits image and rect properties from pygame Sprite class.
class Cell(pygame.sprite.Sprite):
    # Initialise cell.
    def __init__(self, x, y, state=0):
        self.x = x
        self.y = y
        self.state = state
        self.image = None
        self.rect = None

    def __repr__(self):
        return str(self.state)
        
class Stack():
    # Initialise stack.
    def __init__(self, data=None):
        if data == None:
            self.data = []
        else:
            self.data = data

    # Add item to top of stack.
    def push(self, item):
        self.data.append(item)

    # Remove item from top of stack and return it.
    def pop(self):
        if len(self.data) > 0:
            item = self.data[-1]
            del self.data[-1]
            return item
        else:
            return None