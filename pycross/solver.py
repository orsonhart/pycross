# Import required modules.
import copy

def permutations(values, row):
    # If there are clues..
    if len(values) > 0:
        current, other = values[0], values[1:]
        # For i in number of free spaces of movement...
        for i in range(len(row)-sum(other)-len(other)-current+1):
            # If there are no excluded cells in this range...
            if 2 not in row[i:i+current]:
                # If it is not the last value...
                if other:
                    # Yield the calculated permutation followed by every possible permutation of the remaining clues
                    for j in permutations(other, row[i+current+1:]):
                        yield [2]*(i) + [1]*current + [2] + j
                else:
                    # Yield the calculated permutation
                    yield [2]*(i) + [1]*current 
    else:
        # Yield nothing.
        yield []

def solve_row(values, row):
    valid_permutations = []
    # Find every permutation of the clues.
    for permutation in permutations(values, row):
        # Fill permutation if incomplete.
        permutation += [2]*(len(row)-len(permutation))
        invalid = False
        # If the permutation of clues does not match the current row..
        for fixed, possible in zip(row, permutation):
            if fixed>0 and fixed != possible:
                # then it is invalid.
                invalid = True
                break
        # If permutation is not invalid, add it to a list of valid permutations.
        if not invalid:
            valid_permutations.append(permutation)

    # Consider the first valid permutation as a template.
    new_row = valid_permutations[0]
    # Change the template so that it contains only included or excluded cells which agree with every 
    # generated valid permutation
    for permutation in valid_permutations[1:]:
        new_row = [fixed if fixed == possible else 0 for fixed, possible in zip(new_row,permutation)]
        
    # Return the cells which can be deduced.
    return new_row            

def solve(row_values, col_values, grid, unique=True):
    changed = True
    # Repeat until nothing more can be deduced.
    while changed:
        changed = False
        # Update each row using the solve_row() procedure.
        for y, row_value in enumerate(row_values):
            row = solve_row(row_value, grid[y])
            if grid[y] != row:
                changed = True
                grid[y] = row

        # Update each column using the solve_col() procedure.
        for x, col_value in enumerate(col_values):
            col = solve_row(col_value, [row[x] for row in grid])
            if [row[x] for row in grid] != col:
                changed = True
                for y, cell in enumerate(col):
                    grid[y][x] = cell
        
    only_solution = True
    # Iterate through every cell in the grid.
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == 0:
                # Enters here if there are multiple solutions.
                only_solution = False
                # Create a copy of the grid.
                grid_copy = copy.deepcopy(grid)
                # Mark the empty cell as included.
                grid_copy[y][x] = 1
                # Try to solve it under these new conditions.
                try:
                    return solve(row_values, col_values, grid_copy, unique=False)
                # If that turns out to be impossible, backtrack and mark the included cell as excluded.
                except IndexError:
                    grid[y][x] = 2
    # If the grid is solved, return the grid.
    if only_solution == True:
        return (grid,unique)
    # If grid cant be solved, raise an error.
    raise IndexError

# Convert grid object attributes to correct form for solving.
def solve_grid(width, height, x_nums, y_nums):
    grid = [[0]*width for i in range(height)]
    ans = solve(y_nums, x_nums, grid)
    return ans