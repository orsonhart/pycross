#please see pygame for python 3 in moodle
import sys
if "M:/python_stuff" not in sys.path:
    sys.path.append("M:/python_stuff")

# Import required modules.
import pygame, random, os, time, datetime
import tkinter as tk
# Import functions from external files.
from objects import *
from load_files import *

# Create tkinter root.
root = tk.Tk()
root.title("Pycross")
root.resizable(False, False)

# Class for dialog window.
class MyDialog:
    def __init__(self, parent):
        top = self.top = tk.Toplevel(parent)

    # Create a window which allows the user to change their config.
    def change_config(self):
        top = self.top

        # Create variables and set default values.
        width_text = tk.StringVar()
        width_text.set(SCREEN_WIDTH)
        height_text = tk.StringVar()
        height_text.set(SCREEN_HEIGHT)

        # Create labels and entry boxes
        width_label = tk.Label(top, text="Enter width:")
        width_entry = tk.Entry(top, textvariable=width_text, justify="center")

        height_label = tk.Label(top, text="Enter height:")
        height_entry = tk.Entry(top, textvariable=height_text, justify="center")

        # Function which makes sure border is not bigger than thick border.
        def adjust_thick_border_slider(value):
            if border_slider.get() > thick_border_slider.get():
                thick_border_slider.set(border_slider.get())

        # Function which makes sure thick border is not smaller than border.
        def adjust_border_slider(value):
            if thick_border_slider.get() < border_slider.get():
                border_slider.set(thick_border_slider.get())

        # Create border label and slider and set default value.
        border_label = tk.Label(top, text="Border thickness:")
        border_slider = tk.Scale(top, from_=0, to=1, resolution=0.05, orient=tk.HORIZONTAL, command=adjust_thick_border_slider)
        border_slider.set(THIN_BORDER_MULTIPLIER)

        # Create thick border label and slider and set default value.
        thick_border_label = tk.Label(top, text="Thick border thickness:")
        thick_border_slider = tk.Scale(top, from_=0, to=1, resolution=0.05, orient=tk.HORIZONTAL, command=adjust_border_slider)
        thick_border_slider.set(THICK_BORDER_MULTIPLIER)
       
        # Executes this code when button is pressed. 
        def update_config():
            global SCREEN_WIDTH, SCREEN_HEIGHT, THIN_BORDER_MULTIPLIER, THICK_BORDER_MULTIPLIER
            # Get the input from the entry box.
            width_text = width_entry.get()
            height_text = height_entry.get()
            # Try to convert text to integers
            try:
                # Get values from window.
                width = int(width_entry.get())
                height = int(height_entry.get())
                border_size = border_slider.get()
                thick_border_size = thick_border_slider.get()
                
                # Make sure width and height are reasonable values.
                if width >= 200 and height >= 200 and width <= 1920 and height <= 1080:
                    # Write values to config.
                    write_config_file(width, height, border_size, thick_border_size)
                    # Reload config.
                    SCREEN_WIDTH, SCREEN_HEIGHT, THIN_BORDER_MULTIPLIER, THICK_BORDER_MULTIPLIER = load_config_file()
                    
                    # Rescale tkinter window, embed frame, and pygame screen.
                    root.geometry(str(SCREEN_WIDTH)+"x"+str(SCREEN_HEIGHT))
                    embed.configure(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
                    os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
                    os.environ['SDL_VIDEODRIVER'] = 'windib'
                    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

                    # If a grid exists...
                    if grid != None:
                        init_game()
                    else:
                        screen.fill(BACKGROUND_COLOR)
                        # Display the title image.
                        title = load_title_image()
                        screen.blit(title, (SCREEN_WIDTH//2 - title.get_rect().width // 2, SCREEN_HEIGHT//2 - title.get_rect().height//2))
                    # Exit dialog.
                    top.destroy()
            except:
                pass

        # Create button.
        btn = tk.Button(top, text="Confirm", command = update_config)

        # Pack all the elements into the dialog window.
        width_label.pack()
        width_entry.pack()
        height_label.pack()
        height_entry.pack()
        border_label.pack()
        border_slider.pack()
        thick_border_label.pack()
        thick_border_slider.pack()
        btn.pack()

    # Create window which allows the user to specify dimensions for a randomly generated puzzle.
    def choose_dimensions(self):
        top = self.top
        # Create variables.
        width = tk.IntVar(top)
        height = tk.IntVar(top)

        # Create list of possible values. (Multiples of 5 from 5->50)
        widths = [i*5 for i in range(1,11)]
        heights = [i*5 for i in range(1,11)]
        # Try to set the default values to the dimensions of the current grid
        try:
            width.set(grid.width)
            height.set(grid.height)
        # If there is no grid loaded, then use 10 and 10.
        except:
            width.set(10)
            height.set(10)

        # Create labels and dropdown list.
        width_label = tk.Label(top, text = "Width: ")
        width_option = tk.OptionMenu(top, width, *widths)

        height_label = tk.Label(top, text = "Height: ")
        height_option = tk.OptionMenu(top, height, *heights)

        # Generate a random grid with specified width and height.
        def create_random_grid(width, height):
            # Create empty grid.
            dummy_grid = Grid(width, height, [],[])
            # Make random puzzle more dense the bigger it is.
            chance = random.normalvariate(0.5 + (width*height)**0.5/50*0.3, 0.06)
            chance = min(chance,0.8)

            # Fill dummy grid randomly.
            dummy_grid.fill_randomly(chance)
            # Calculate the x_nums and y_nums
            x_nums, y_nums = dummy_grid.generate_nums_from_grid()

            # Return grid object.
            return Grid(width, height, x_nums, y_nums)

        # Executes this code when button is pressed.
        def set_grid_from_dimensions():
            # Set grid to randomly generated grid and exit dialog.
            global grid
            grid = create_random_grid(width.get(),height.get())
            init_game()
            top.destroy()

        # Create button.
        btn = tk.Button(top, text="Confirm", command = set_grid_from_dimensions)

        # Pack all the elements into the dialog window.
        width_label.pack()
        width_option.pack()
        height_label.pack()
        height_option.pack()
        btn.pack()

    # Create a window which allows the user to pick a file from a directory.
    def choose_file(self, directory):   
        top = self.top 

        # Get list of files from specified directory.
        files = os.listdir(os.getcwd()+"/"+directory)
        # Sort them.
        files = merge_sort(files)
        # If they are saves, then reverse list (as reverse chronologically = reverse alphabetically)
        if directory == "saves":
            files.reverse()

        # Executes this code when confirm button is pressed.
        def get_filename_from_listbox():
            global grid
            # Try to set the current grid to the grid in the file specified by the user and then close popup.
            try:
                index = listbox.curselection()[0]
                filename = listbox.get(index)
            
                grid = load_grid_from_file(os.getcwd() + "/" +directory+"/"+ filename + ".json")
                init_game()
                top.destroy()
            # If no file is selected, do nothing.
            except:
                pass

        # Executes thie code when delete button is pressed.
        def delete_file_from_list():
            # Try to delete the selected file from directory.
            try:
                index = listbox.curselection()[0]
                filename = listbox.get(index)
                os.remove(os.getcwd() + "/"+directory+"/" + filename + ".json")
                listbox.delete(index)
            # If no file is selected do nothing.
            except:
                pass

        # Create listbox and label.
        listbox = tk.Listbox(top, width=25, selectmode=tk.SINGLE)
        label = tk.Label(top, text="Choose " + directory[0:-1] + ":")
        
        # Insert every file into the listbox.
        for file in files:
            listbox.insert(tk.END, file[:-5])

        # Create confirm and delete buttons.
        choose_btn=tk.Button(top, text="Confirm", command = get_filename_from_listbox)
        delete_btn=tk.Button(top, text="Delete", command = delete_file_from_list)

        # Pack all elements into the dialog window.
        label.pack()
        listbox.pack()
        choose_btn.pack(side = tk.LEFT)
        delete_btn.pack(side = tk.RIGHT)

    # Create a window which allows the user to specify their filename.
    def choose_filename(self):
        top = self.top

        # Executes this code when confirm button pressed.
        def get_text_from_entry():
            # Try to create a grid file with the filename the user has specified.
            try:
                entry_text = entry.get()
                if entry_text != "":
                    filename = entry_text
                    make_file_from_grid(grid, os.getcwd() + "/puzzles/" + filename + ".json")
                    top.destroy()
            # If the user has specified an invalid filename, do nothing.
            except:
                pass

        # Create label, entry box, and button.
        label = tk.Label(top, text="Enter puzzle name:")
        entry = tk.Entry(top)
        btn=tk.Button(top, text="Confirm", command = get_text_from_entry)

        # Pack all elements into the dialog window.
        label.pack()
        entry.pack()
        btn.pack()

    # Creates a window which allows the user to specify dimensions for an empty grid.
    def create_empty_grid(self):
        top = self.top
        # Create variables.
        width = tk.IntVar(top)
        height = tk.IntVar(top)

        # Create list of possible values. (Multiples of 5 from 5->50)
        widths = [i*5 for i in range(1,11)]
        heights = [i*5 for i in range(1,11)]
        # Try to set the default values to the dimensions fo the current grid.
        try:
            width.set(grid.width)
            height.set(grid.height)
        # If there is no grid loaded, then use 10 and 10.
        except:
            width.set(10)
            height.set(10)

        # Create labels and dropdown lists.
        width_label = tk.Label(top, text = "Width: ")
        width_option = tk.OptionMenu(top, width, *widths)

        height_label = tk.Label(top, text = "Height: ")
        height_option = tk.OptionMenu(top, height, *heights)

        # Executes this code when button is pressed.
        def confirm_dimensions():
            # Create a new empty grid of specified dimensions.
            global grid
            new_width = width.get()
            new_height = height.get()
            x_nums, y_nums = [], []
            for _ in range(new_width):
                x_nums.append([])
            for _ in range(new_height):
                y_nums.append([])
            grid = Grid(new_width, new_height, x_nums, y_nums)
            init_game()
            # Exit dialog.
            top.destroy()

        # Create button.
        btn = tk.Button(top, text="Confirm", command = confirm_dimensions)

        # Pack all the elements into the dialog window.
        width_label.pack()
        width_option.pack()
        height_label.pack()
        height_option.pack()
        btn.pack()

# Initialise colour constants.
WHITE = (255,255,255)
DEFAULT_BACKGROUND = (99, 205, 218)
CORRECT_BACKGROUND = (80, 200, 120)
INCORRECT_BACKGROUND = (224, 76, 60)
BACKGROUND_COLOR = DEFAULT_BACKGROUND
BLACK = (0,0,0)

# Load user config from JSON file.
SCREEN_WIDTH, SCREEN_HEIGHT, THIN_BORDER_MULTIPLIER, THICK_BORDER_MULTIPLIER = load_config_file()

# Initialise global variables.
grid = None
max_volume = 0.15
puzzle_check_time = 0
background_reset_timer = 0
paint_state = 0

# Constants used per grid for drawing to screen.
GRID_WIDTH = None
GRID_HEIGHT = None
CLUES_WIDTH = None
CLUES_HEIGHT = None
MAX_CELL_WIDTH = None
MAX_CELL_HEIGHT = None
CELL_SIZE = None
THICK_BORDER = None
THIN_BORDER = None
LEFT_WHITESPACE = None
TOP_WHITESPACE = None

# Load all sprites.
empty_cell = pygame.image.load("empty_cell.png")
filled_cell = pygame.image.load("filled_cell.png")
marked_cell = pygame.image.load("marked_cell.png")
selected_overlay = pygame.image.load("selected_overlay.png")

# Loads and scales title image based on the window dimensions.
def load_title_image():
    # Load title image.
    title = pygame.image.load("title.png")

    # Determine factor to scale title image by.
    title_width = title.get_rect().width
    title_height = title.get_rect().height

    # Calculate a horizontal and vertical scale factor to fit the screen
    # and choose the smaller of the two.
    if SCREEN_HEIGHT/title_height < SCREEN_WIDTH / title_width:
        title_scale_factor = SCREEN_HEIGHT/title_height
    else:
        title_scale_factor = SCREEN_WIDTH/title_width

    # Scale title image.
    title = pygame.transform.rotozoom(title, 0, title_scale_factor)

    return title

title = load_title_image()

# Create a tkinter frame for pygame to run it and embed it in the Tk window.
embed = tk.Frame(root, width=9999, height=9999)
os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
os.environ['SDL_VIDEODRIVER'] = 'windib'
embed.configure(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
embed.pack()

# These functions are called by the menu bar.
def choose_puzzle_from_file():
    # Create new window allowing the user to choose a puzzle.
    d = MyDialog(root)
    d.choose_file("puzzles")
    # Pause main program whilst user chooses puzzle.
    root.wait_window(d.top)

def generate_random_puzzle():
    # Create new window allowing the user to choose dimensions of a random puzzle.
    d = MyDialog(root)
    d.choose_dimensions()
    # Pause main program whilst user chooses puzzle.
    root.wait_window(d.top)

def new_canvas():
    # Create new window allowing the user to choose dimensions of a blank canvas.
    d = MyDialog(root)
    d.create_empty_grid()
    # Pause main program whilst user chooses puzzle. 
    root.wait_window(d.top)

def save_pattern():
    # Create new window allowing the user to choose the name of their new puzzle.
    d = MyDialog(root)
    d.choose_filename()
    # Pause main program whilst user chooses puzzle.
    root.wait_window(d.top)

def choose_save_from_file():
    # Create new window allowing the user to choose a save to load.
    d = MyDialog(root)
    d.choose_file("saves")
    # Pause main program whilst user chooses puzzle.
    root.wait_window(d.top)

def change_config():
    # Create new window allowing the user to change their config.
    d = MyDialog(root)
    d.change_config()
    # Pause main program whilst user updates config.
    root.wait_window(d.top)

def save_progress():
    # Create a new save with the name as the current time.
    filename = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    make_save_from_grid(grid, os.getcwd() + "/saves/" + filename + ".json")

def solve_puzzle():
    # If there is a grid...
    if grid != None:
        # Solve the puzzle.
        grid.solve()

def undo_move():
    # If there is anything in the undo stack...
    if len(undo_stack.data) > 0:
        # Pop the most recent move from the undo stack.
        y,x,old_state,new_state = undo_stack.pop()
        # Undo move.
        grid.data[y][x].state = old_state
        # Add undone move to redo stack.
        redo_stack.push((y,x,new_state,old_state))

def redo_move():
    # If there is anything in the redo stack...
    if len(redo_stack.data) > 0:
        # Pop the most recent move from the redo stack.
        y,x,old_state,new_state = redo_stack.pop()
        # Redo move.
        grid.data[y][x].state = old_state
        # Add redone move to the undo stack.
        undo_stack.push((y,x,new_state,old_state))

def toggle_mute(menu):
    # If the music is currently playing...
    if menu.entrycget(1, "label") == "Mute Music":
        # Change the label on the menu.
        menu.entryconfigure(1, label="Unmute Music")
        # Set volume to 0.
        pygame.mixer.music.set_volume(0)
    else:
        # Change the label on the menu.
        menu.entryconfigure(1, label="Mute Music")
        # Unmute music.
        pygame.mixer.music.set_volume(max_volume)

def check_solution():
    global BACKGROUND_COLOR, puzzle_check_time, background_reset_timer
    # If there is a grid and it has clues.
    if grid != None and CLUES_HEIGHT > 0:
        # Store the time that the check was made.
        puzzle_check_time = time.time()
        # If the grid is complete...
        if grid.is_complete():
            # Set the background colour to green.
            BACKGROUND_COLOR = CORRECT_BACKGROUND
            draw_grid_outlines(screen)
            # Play sound effect.
            correct_sound.play()
            # Set timer so background returns to normal after 3.5 seconds.
            background_reset_timer = 3.5
        else:
            # Set the background colour to red.
            BACKGROUND_COLOR = INCORRECT_BACKGROUND
            draw_grid_outlines(screen)
            # Play sound effect.
            incorrect_sound.play()
            # Set timer so background returns to normal after 1 second.
            background_reset_timer = 1

# This function does nothing.
def donothing():
    pass

# Create menu bar.
menubar = tk.Menu(root)
# Create play menu
playmenu = tk.Menu(menubar, tearoff=0)
playmenu.add_command(label="Choose Puzzle from File", command=choose_puzzle_from_file, accelerator="F1")
playmenu.add_command(label="Generate Random Puzzle", command=generate_random_puzzle, accelerator = "F2")
playmenu.add_command(label="Continue from Save", command=choose_save_from_file, accelerator="F3")
menubar.add_cascade(label="Play", menu=playmenu)

# Create create menu.
createmenu = tk.Menu(menubar, tearoff=0)
createmenu.add_command(label="New Canvas", command=new_canvas, accelerator="F9")
createmenu.add_command(label="Save Pattern", command=save_pattern, accelerator = "F10")
menubar.add_cascade(label="Create", menu=createmenu)

# Create puzzle menu.
puzzlemenu = tk.Menu(menubar, tearoff=0)
puzzlemenu.add_command(label="Undo Move", command=undo_move, accelerator="Z")
puzzlemenu.add_command(label="Redo Move", command=redo_move, accelerator="R")
puzzlemenu.add_command(label="Check Solution", command=check_solution, accelerator="Enter")
puzzlemenu.add_command(label="Save Progress", command=save_progress, accelerator="F5")
puzzlemenu.add_command(label="Solve Puzzle", command=solve_puzzle, accelerator="F12")
menubar.add_cascade(label="Puzzle", menu=puzzlemenu)

# Create setting menu.
settingsmenu = tk.Menu(menubar, tearoff=0)
settingsmenu.add_command(label="Change Config", command=change_config)
settingsmenu.add_command(label="Mute Music", command= lambda: toggle_mute(settingsmenu), accelerator="M")
menubar.add_cascade(label="Settings", menu=settingsmenu)

# Add menubar to tkinter window.
root.config(menu=menubar)

# Create surface object and set it's caption.
screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
screen.fill(BACKGROUND_COLOR)
# Display the title image.
screen.blit(title, (SCREEN_WIDTH//2 - title.get_rect().width // 2, SCREEN_HEIGHT//2 - title.get_rect().height//2))

# Grid, Screen Height, Screen Width -> all information.
def set_global_variables(grid):
    global GRID_WIDTH, GRID_HEIGHT, CLUES_WIDTH, CLUES_HEIGHT, MAX_CELL_WIDTH, MAX_CELL_HEIGHT, CELL_SIZE, THICK_BORDER, THIN_BORDER, LEFT_WHITESPACE, TOP_WHITESPACE
    
    GRID_WIDTH = grid.width
    GRID_HEIGHT = grid.height

    CLUES_WIDTH = len(max(grid.y_clues,key=len))
    CLUES_HEIGHT = len(max(grid.x_clues,key=len))
    
    MAX_CELL_WIDTH = SCREEN_WIDTH / ((GRID_WIDTH + CLUES_WIDTH) + (GRID_WIDTH/5 + 2)*THICK_BORDER_MULTIPLIER + (GRID_WIDTH/5)*4*THIN_BORDER_MULTIPLIER)
    MAX_CELL_HEIGHT = SCREEN_HEIGHT / ((GRID_HEIGHT + CLUES_HEIGHT) + (GRID_HEIGHT/5 + 2)*THICK_BORDER_MULTIPLIER + (GRID_HEIGHT/5)*4*THIN_BORDER_MULTIPLIER)         

    CELL_SIZE = int(min(MAX_CELL_WIDTH,MAX_CELL_HEIGHT))
    THICK_BORDER = int(CELL_SIZE*THICK_BORDER_MULTIPLIER)
    THIN_BORDER = int(CELL_SIZE*THIN_BORDER_MULTIPLIER)

    LEFT_WHITESPACE = (SCREEN_WIDTH - (CLUES_WIDTH+GRID_WIDTH)*CELL_SIZE - (GRID_WIDTH/5+2)*THICK_BORDER - (GRID_WIDTH/5*4)*THIN_BORDER)//2
    TOP_WHITESPACE = (SCREEN_HEIGHT - (CLUES_HEIGHT+GRID_HEIGHT)*CELL_SIZE - (GRID_HEIGHT/5+2)*THICK_BORDER - (GRID_HEIGHT/5*4)*THIN_BORDER)//2

# Draw outlines of grid.
def draw_grid_outlines(screen):
    # Clear the screen.
    screen.fill(BACKGROUND_COLOR)

    # Draw Horizontal End Bar if there are clues.
    if CLUES_HEIGHT > 0:
        pygame.draw.rect(screen,BLACK,(
        LEFT_WHITESPACE + THICK_BORDER+CLUES_WIDTH*CELL_SIZE,
        TOP_WHITESPACE,
        GRID_WIDTH*CELL_SIZE+(GRID_WIDTH/5+1)*THICK_BORDER+(GRID_WIDTH/5*4)*THIN_BORDER,
        THICK_BORDER
        ))

    for y in range(GRID_HEIGHT+1):
        # Draw Horizontal THICK Borders.
        if y%5 == 0:
            pygame.draw.rect(screen,BLACK,(
                LEFT_WHITESPACE + THICK_BORDER,
                TOP_WHITESPACE + THICK_BORDER + CLUES_HEIGHT*CELL_SIZE + (y/5)*(THICK_BORDER+4*THIN_BORDER+5*CELL_SIZE),
                CLUES_WIDTH*CELL_SIZE + GRID_WIDTH*CELL_SIZE + (GRID_WIDTH/5+1)*THICK_BORDER + (GRID_WIDTH/5*4)*THIN_BORDER,
                THICK_BORDER
            ))

        # Draw Horizontal THIN Borders.
        else:
            pygame.draw.rect(screen,BLACK,(
                LEFT_WHITESPACE + THICK_BORDER,
                TOP_WHITESPACE + THICK_BORDER + CLUES_HEIGHT*CELL_SIZE + (y//5+1)*THICK_BORDER + (y-1-y//5)*THIN_BORDER + (y*CELL_SIZE),
                CLUES_WIDTH*CELL_SIZE + GRID_WIDTH*CELL_SIZE + (GRID_WIDTH/5+1)*THICK_BORDER + (GRID_WIDTH/5*4)*THIN_BORDER,
                THIN_BORDER
            ))

    # Draw Vertical End Bar if there are clues.
    if CLUES_WIDTH > 0:
        pygame.draw.rect(screen,BLACK,(
            LEFT_WHITESPACE,
            TOP_WHITESPACE + THICK_BORDER+CLUES_HEIGHT*CELL_SIZE,
            THICK_BORDER,
            GRID_HEIGHT*CELL_SIZE+(GRID_HEIGHT/5+1)*THICK_BORDER+(GRID_HEIGHT/5*4)*THIN_BORDER
        ))
        
    for x in range(GRID_WIDTH+1):
        # Draw Vertical THICK Borders.
        if x%5 == 0 and THICK_BORDER!=0:
            pygame.draw.rect(screen,BLACK,(
                LEFT_WHITESPACE + THICK_BORDER+CLUES_WIDTH*CELL_SIZE+(x/5)*(THICK_BORDER+4*THIN_BORDER+5*CELL_SIZE),
                TOP_WHITESPACE+THICK_BORDER,
                THICK_BORDER,
                CLUES_HEIGHT*CELL_SIZE+(GRID_HEIGHT/5+1)*THICK_BORDER + (GRID_HEIGHT/5*4)*THIN_BORDER + GRID_HEIGHT*CELL_SIZE
            ))

        # Draw Vertical THIN Borders.
        elif(THIN_BORDER!=0):
            pygame.draw.rect(screen,BLACK,(
                LEFT_WHITESPACE + THICK_BORDER+CLUES_WIDTH*CELL_SIZE+(x//5+1)*THICK_BORDER+(x-1-x//5)*THIN_BORDER + (x*CELL_SIZE),
                TOP_WHITESPACE+THICK_BORDER,
                THIN_BORDER,
                CLUES_HEIGHT*CELL_SIZE+(GRID_HEIGHT/5+1)*THICK_BORDER + (GRID_HEIGHT/5*4)*THIN_BORDER + GRID_HEIGHT*CELL_SIZE
            ))

# Resize sprites to the size of a cell.
def resize_sprites(CELL_SIZE):
    global empty_cell, filled_cell, marked_cell, selected_overlay, clue_image
    
    empty_cell = pygame.transform.smoothscale(empty_cell,(CELL_SIZE, CELL_SIZE))
    filled_cell = pygame.transform.smoothscale(filled_cell,(CELL_SIZE, CELL_SIZE))
    marked_cell = pygame.transform.smoothscale(marked_cell,(CELL_SIZE, CELL_SIZE))
    selected_overlay = pygame.transform.smoothscale(selected_overlay,(CELL_SIZE, CELL_SIZE))

# Set image and hitbox of each cell object.
def set_cell_attributes():
    # For each cell in the grid...
    for y, row in enumerate(grid.data):
        for x, cell in enumerate(row):
            # Set the image and hitbox of the sprite.
            cell.image = empty_cell
            cell.rect = cell.image.get_rect()
            cell.rect.x = LEFT_WHITESPACE + THICK_BORDER+CLUES_WIDTH*CELL_SIZE+(x//5+1)*THICK_BORDER+(x-x//5)*THIN_BORDER+x*CELL_SIZE
            cell.rect.y = TOP_WHITESPACE + THICK_BORDER+CLUES_HEIGHT*CELL_SIZE+(y//5+1)*THICK_BORDER+(y-y//5)*THIN_BORDER+y*CELL_SIZE

            # Extend the hitbox of the sprite if it is not ahead of a thick border.
            if not((x+1)%5==0):
                cell.rect.width += THIN_BORDER
            if not((y+1)%5==0):
                cell.rect.height += THIN_BORDER

# Set hitbox of each clue object:
def set_clue_attributes():
    # For each clue in the horizontal clues...
    for x, clues in enumerate(grid.x_clues):
        # (Loop backwards through the clues list because the hitboxes are given from closest to grid to furthest from grid.)
        for y, clue in enumerate(clues[::-1]):
            # Set the hitbox of the cell.
            clue.rect = pygame.Rect(
                        LEFT_WHITESPACE+THICK_BORDER+CLUES_WIDTH*CELL_SIZE+(x//5+1)*THICK_BORDER+(x-x//5)*THIN_BORDER+x*CELL_SIZE,
                        TOP_WHITESPACE+THICK_BORDER+CELL_SIZE*CLUES_HEIGHT-(y+1)*CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE)

    # For each clue in the vertical clues...
    for y, clues in enumerate(grid.y_clues):
        # (Loop backwards through the clues list because the hitboxes are given from closest to grid to furthest from grid.)
        for x, clue in enumerate(clues[::-1]):
            # Set the hitbox of the cell.
            clue.rect = pygame.Rect(
                        LEFT_WHITESPACE+THICK_BORDER+CLUES_WIDTH*CELL_SIZE-(x+1)*CELL_SIZE,
                        TOP_WHITESPACE+THICK_BORDER+CLUES_HEIGHT*CELL_SIZE+(y//5+1)*THICK_BORDER+(y-y//5)*THIN_BORDER+y*CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE)

# Initialise a pygame font.
pygame.font.init()
# Set mixer paramters so that audio doesn't delay when muting/unmuting.
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)


# Load sounds.
incorrect_sound = pygame.mixer.Sound('incorrect_solution.ogg')
correct_sound = pygame.mixer.Sound('correct_solution.ogg')
pygame.mixer.music.load('soundtrack.ogg')

# Set volume of music.
pygame.mixer.music.set_volume(max_volume)
# Make music repeat.
pygame.mixer.music.play(-1)

# Create stack objects.
undo_stack = Stack()
redo_stack = Stack()

# This procedure
def init_game():
    global BACKGROUND_COLOR
    BACKGROUND_COLOR = DEFAULT_BACKGROUND
    set_global_variables(grid)
    draw_grid_outlines(screen)
    resize_sprites(CELL_SIZE)
    set_cell_attributes()
    set_clue_attributes()
    global font
    font = pygame.font.SysFont("centurygothic", int(CELL_SIZE*0.95), bold=False)

# GAME LOOP:
running = True
while(running):
    # Reset mouse click flags.
    left_button_pressed = False
    right_button_pressed = False

    events = pygame.event.get()

    for event in events:  
        # Set mouse click flags.
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                left_button_pressed = True
            elif event.button == 3:
                right_button_pressed = True
        # Call functions from button presses.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                choose_puzzle_from_file()
                
            elif event.key == pygame.K_F2:
                generate_random_puzzle()

            elif event.key == pygame.K_F3:
                choose_save_from_file()

            elif event.key == pygame.K_F5:
                save_progress()

            elif event.key == pygame.K_F9:
                new_canvas()

            elif event.key == pygame.K_F10:
                save_pattern()

            elif event.key == pygame.K_F12:
                solve_puzzle()

            elif event.key == pygame.K_m:
                toggle_mute(settingsmenu)

            elif event.key == pygame.K_RETURN:
                check_solution()

            elif event.key == pygame.K_z:
                undo_move()

            elif event.key == pygame.K_r:
                redo_move()
    
    # Change cell image based on mouse pos.
    highlighted_row = None
    highlighted_column = None 

    # If there is a grid...
    if grid != None:
        # Reset background if has been changed after specified time.
        if time.time() - puzzle_check_time > background_reset_timer:
            BACKGROUND_COLOR = DEFAULT_BACKGROUND
            draw_grid_outlines(screen)

    # Loop through every cell in the grid:
        for y, row in enumerate(grid.data):
            for x, cell in enumerate(row):
                # Set highlighted row and column based on mouse pos.
                if cell.rect.collidepoint(pygame.mouse.get_pos()):
                    highlighted_row = y
                    highlighted_column = x

                    # Set paint state when mouse is clicked
                    if left_button_pressed == True:
                        if cell.state == 1:
                            paint_state = 0
                        else:
                            paint_state = 1

                    if right_button_pressed == True:
                        if cell.state == 2:
                            paint_state = 0
                        else:
                            paint_state = 2

                    # While mouse is held, paint with paint state.
                    if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                        if cell.state != paint_state:
                            undo_stack.push((y,x,cell.state,paint_state))
                            cell.state = paint_state
                        
                # Update image based on state
                if cell.state == 0:
                    cell.image = empty_cell
                elif cell.state == 1:
                    cell.image = filled_cell
                elif cell.state == 2:
                    cell.image = marked_cell


        # Highlight all cells in the row and column of the selected cell.
        # If a row and column has been selected.
        if highlighted_row != None: 
            # For each cell in the column...
            for cell in grid.data[highlighted_row]:
                # Overlay transparency.
                cell.image = cell.image.copy()
                cell.image.blit(selected_overlay,(0,0))
            # For each cell in the row...
            for row in grid.data:
                # Overlay transparency.
                row[highlighted_column].image = row[highlighted_column].image.copy()
                row[highlighted_column].image.blit(selected_overlay,(0,0))
                
        # Draw Cells
        for row in grid.data:
            for cell in row:
                screen.blit(cell.image,cell.rect)

        # Draw clue text
        for clues in grid.x_clues + grid.y_clues:
            # For every clue..
            for clue in clues:
                # Redraw the background behind the clue.
                pygame.draw.rect(screen, BACKGROUND_COLOR, clue.rect)
                # If the mouse is overlaying the clue
                if clue.rect.collidepoint(pygame.mouse.get_pos()):
                    # Highlight the clue.
                    screen.blit(selected_overlay, clue.rect)
                    # If the user has clicked:
                    if left_button_pressed == True:
                        # Change the marked status of the clue.
                        clue.marked = not clue.marked

                # Make a text object with the clue value
                clue_text = font.render(str(clue.value),True,BLACK)

                if clue.marked == True:
                    # Make the clue text transparent.
                    alpha_img = pygame.Surface(clue_text.get_size(),pygame.SRCALPHA)
                    alpha_img.fill((255,255,255,90))
                    clue_text.blit(alpha_img, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

                # Position and draw the text to the screen.
                clue_text_rect = clue_text.get_rect()
                clue_text_rect.center = clue.rect.center
                screen.blit(clue_text,clue_text_rect)
    
    # Update the pygame display.
    pygame.display.update()
    # Try to update the tkinter window.
    try:
        root.update()
    # If it cannot be updated, then it has been closed...
    except:
        # so exit the game loop.
        running = False
# Quit pygame once the tkinter window has been closed.
pygame.quit()
