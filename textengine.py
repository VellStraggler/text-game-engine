import time, keyboard, os

DIRPATH = os.path.dirname(__file__) #Required to run program in Python3 terminal

# Helpful in debugging information.
many_space = ' ' * 50
many_line = '\n' * 50

def grid_patcher(array:list):
    """
    TO BE USED ON MAP AND SPRITE ARRAYS.
    Adds spaces until the array is rectangular, then returns the list
    patched with spaces.
    """
    #find longest y:
    longest_y = 0
    #the length of output_map is the extent of y
    for y in range(0,len(array)):
        if len(array[y]) > longest_y:
            longest_y = len(array[y])
    #make all columns the same length
    for row in array:
        for s in range(0,longest_y - len(row)):
            row.append(" ")
    return array

def can_be_read(filename:str):
    """Boolean function, check if file can be opened"""
    try:
        with open(filename,'r') as file:
            return True
    except: return False

class GameObject():
    """Initialization creates a map and a sprite list"""
    def __init__(self):
        self.map = Map()
        self.sprites = Sprites()

    def run_map(self):
        """Combine the map and the sprites and begin the main game loop."""
        assert len(self.sprites.sprites) > 0, "Error: No sprites found."
        self.draw_map()
        quit = False
        # Begin the printing loop.
        # For now, game will be running within a terminal.
        frames = 0
        while(not quit):
            s_time = time.time()
            self.map.print_all()
            frames += 1
            f_time = round(1/(time.time() - s_time),3)
            print("FPS:",f_time)
            if keyboard.is_pressed("q"):
                quit = True
        print("Game Over.")
        input("Press ENTER to exit")

    def draw_map(self):
        for sprite in self.sprites.sprites:
            if sprite.input_char != '': # Make sure they have a map char
            # GO through each char in the map by ROW, then COLUMN
                for mapy in range(0,len(self.map.output_map)):
                    for mapx in range(0,len(self.map.output_map[mapy])):
                        # Check if a sprite's map character is present on the map.
                        if self.map.output_map[mapy][mapx] == sprite.input_char:
                            self.map.output_map[mapy][mapx] = " "
                            # If it is, replace an area around that point with the sprite array.
                            for spritey in range(sprite.topleft()[0],sprite.bottomright()[0] + 1):
                                for spritex in range(sprite.topleft()[1],sprite.bottomright()[1] + 1):
                                    # Only change the character if it has not already been changed
                                    char_to_use = sprite.char(spritex,spritey)
                                    if char_to_use != " " or (sprite.char(spritex-1,spritey) != " " and sprite.char(spritex+1,spritey) != " "):
                                        xpos = mapx + spritex - (sprite.bottomright()[1] // 2)
                                        ypos = mapy + spritey - sprite.bottomright()[0]
                                        if ypos >= 0 and xpos >= 0:
                                            self.map.set_x_y(xpos, ypos, char_to_use)

class Map():
    """Three arrays are stored in a Map object: the user input map, the output map, and a collision map.
    Set the map path upon initialization"""

    def __init__(self):
        self.path = ""
        self.input_map = [] # The input_map will always be exactly what is in the map file.
        self.output_map = [] # Requires data from the input map as well as sprites
        self.collision_map = [] # Requires data from the output map

    def translate(self):
        self.store_map()
        self.output_map = grid_patcher(self.input_map)

    def store_map(self):
        """
        Stores text from file as 2D array or list: [[x1,x2,x3],[x1,x2,x3]]
        Reads from the preset path, saves to input_map
        """
        self.path = DIRPATH + "\\" + self.path # Adds parent directory of running program
        with open(self.path,'r') as file:
            currentline = file.readline() # stores first line as string
            while currentline:
                xlist = [] # Begin a new row of items
                currentline = currentline[:-1] # Remove newline calls.
                for char in currentline:
                    xlist.append(char)
                self.input_map.append(xlist) # Add row to the input_map
                currentline = file.readline()
            
    def print_all(self):                     # \/ leaves space for variables
        for i in range(len(self.output_map)+4):
            print('\033[A\033[F') # This moves the cursor up one.
        for yrow in self.output_map:
            for yitem in yrow:
                # UPDATE: Add check to see if it's any different from the new character
                print(yitem,end="")
            print() # Off to next line
        print()
            
    def set_x_y(self,x,y,character):
        try:
            self.output_map[y][x] = character
        except:
            pass # For going out of window bounds.

class Sprites():
    def __init__(self):
        self.path = ""
        self.sprites = []
    def get_sprites(self):
        sp_name = ""
        sp_array = []
        self.path = DIRPATH + "\\" + self.path # Adds parent directory of running program
        with open(self.path, 'r',encoding='utf-8') as file:
            currentline = file.readline()[:-1] # Removes the \n
            while(currentline):
                if len(currentline) > 0: #No blank lines
                    if currentline[0] == '$' and currentline[-1] == currentline[0]: # Begins and ends with "$"
                        if sp_name != "": # If this is not the first sprite name
                            self.sprites.append(self.Sprite(name = sp_name,array = sp_array))
                            # Adds a newly created sprite with name and array values to the sprites list ^
                            sp_array = []
                        sp_name = currentline[1:-1] # Removes the $'s
                    else:
                        sp_array.append(currentline)
                currentline = file.readline()[:-1] # Removes the \n
    def new(self,name = "", input_char = "", coords = [-1,-1], movement = False, geometry = "default"):
        """Every spritename possible has already been made from the given spritesheet. This just changes
        data."""
        assert type(self.sprites) == type(list())
        for sprite in self.sprites:
            if sprite.name == name: # Only the sprite name and array cannot change
                sprite.input_char = input_char
                sprite.movement = movement
                sprite.geometry = geometry
                sprite.set_origin(coords[0],coords[1])

    
    class Sprite():
        def __init__(self,name="", input_char = "", coords = [-1,-1], array = [], movement = False, geometry = "default"):
            self.name = name
            self.array = array # Array will be found from the sprite sheet text doc.
            self.originx = coords[0]
            self.originy = coords[1]
            self.geometry = geometry
            self.movement = movement
            self.input_char = input_char 

        def set_origin(self,x,y):
            self.originx = x
            self.originy = y
        def set_xy_char(self,x,y,newchar):
            """Change a character at a given coordinate."""
            try:    self.array[y,x] = newchar
            except: pass
        def char(self,x:int,y:int):
            """Returns the character stored here in a sprite array."""
            try:    return self.array[y][x]
            except: return " "
        def topleft(self):
            """Return coordinate values [x,y] of topleft character in sprite."""
            return [0,0]
        def bottomright(self):
            """Return coordinate values [x,y] of bottomright character in sprite."""
            return [len(self.array)-1,len(self.array[len(self.array)-1])-1]