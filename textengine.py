import time, keyboard, os, random

DIRPATH = os.path.dirname(__file__) #Required to run program in Python3 terminal
BLANK = ' '
SIGN = '$'
CLR = "\033[2J"

# Helpful in debugging information.
many_space = ' ' * 50
many_line = '\n' * 50

def grid_patcher(array:list):
    """
    Makes arrays rectangular, that is, filled with arrays of all the same length.
    """
    assert len(array) > 0, "Error: Empty array put in"
    max_height = 0
    #the length of output_map is the extent of y
    for y in range(0,len(array)):
        if len(array[y]) > max_height:
            max_height = len(array[y])
    #make all columns the same length
    for row in array:
        for s in range(0,max_height - len(row)):
            try: 
                row.append(BLANK)
            except:
                try:
                    row = row + BLANK
                except:
                    print("Error: Row is neither of type list nor string.")
    return array

def can_be_read(filename:str):
    """Boolean function, check if file can be opened"""
    try:
        with open(filename,'r') as file:
            return True
    except: return False

class GameObject():
    """
    Initialization creates a map and a sprite list.
    GameObject functions are those that require the map and the sprites.
    """
    def __init__(self):
        self.map = Map()
        self.sprites = Sprites()
        self.quit = False

    def run_map(self):
        """Combine the map and the sprites and begin the main game loop."""
        assert len(self.sprites.sprites) > 0, "Error: No sprites found."
        self.set_output_map() # Put sprites into the map based on the input map.
        self.sprites.get_msprites() # Compile a list of moveable sprites.
        self.frames = 0
        self.f_time = 0
        self.fpss = []
        print(CLR)
        self.map.print_all()
        while(not self.quit):
            self.game_loop()
        total = sum(self.fpss)/self.frames
        print(f"Game Over. Average FPS: {total:.3f}")
        input("Press ENTER to exit. ")

    def game_loop(self):
        self.s_time = time.time()
        self.movement()
        self.map.print_all()
        self.show_fps()
    def show_fps(self):
        self.frames += 1
        try: self.f_time = round(1/(time.time() - self.s_time),3)
        except: pass
        print("FPS:",self.f_time)
        self.fpss.append(self.f_time)

    def debug_maps(self):
        print("input")
        for y in self.map.input_map:
            for x in y:
                print(x,end="")
            print()
        print("output")
        for a in self.map.output_map:
            for b in a:
                print(b,end="")
            print()
        print("collision")
        for c in self.map.collision_map:
            for d in c:
                print(d,end="")
            print()
        print()

    def movement(self):
        if keyboard.is_pressed("a"):
            self.moveplayer(-1)
        if keyboard.is_pressed("d"):
            self.moveplayer(1)
        if keyboard.is_pressed("w"):
            self.moveplayer(0,-1)
        if keyboard.is_pressed("s"):
            self.moveplayer(0,1)
        if keyboard.is_pressed("q"):
            self.quit = True

    def moveplayer(self,xdir = 0,ydir = 0):
        """Moves all user-commanded sprites at their given speeds. xdir and ydir must be -1, 0, or 1."""
        for i in self.sprites.msprites:
            sprite = self.sprites.sprites[i]
            if self.can_move(sprite,move_y=ydir,move_x=xdir):
                self.map.set_xy(sprite.originx,sprite.originy,BLANK,"i") # Clear the space the sprite is at
                sprite.originy += sprite.yspeed * ydir
                sprite.originx += sprite.xspeed * xdir
                self.map.set_xy(sprite.originx,sprite.originy,sprite.char,"i") # Set the new coord
                self.map.in_to_out() # Reset the output map 
                self.set_output_map() # Remap the sprites

    def set_output_map(self):
        """This is necessary to create the Map's Output Map"""
        for sprite in self.sprites.sprites:
            sprite.array = grid_patcher(sprite.array) # Sprites must be rectangular
            if sprite.char != '': # Make sure they have a map char
            # GO through each char in the map by ROW, then COLUMN
                for mapy in range(0,len(self.map.output_map)):
                    for mapx in range(0,len(self.map.output_map[mapy])):
                        # Check if a sprite's map char is present on the map.
                        if self.map.get_xy(mapx,mapy,sprite.char,"o"):
                            sprite.set_origin(mapx,mapy)
                            self.map.output_map[mapy][mapx] = BLANK
                            # If it is, replace an area around that point with the sprite array.
                            for spritey in range(sprite.topleft()[0],sprite.bottomright()[0] + 1):
                                for spritex in range(sprite.topleft()[1],sprite.bottomright()[1] + 1):
                                    # Only change the char if it has not already been changed
                                    char_to_use = sprite.get_char(spritex,spritey)
                                    if char_to_use != BLANK or (sprite.get_char(spritex-1,spritey) != BLANK and sprite.get_char(spritex+1,spritey) != BLANK):
                                        xpos = mapx + spritex - (sprite.bottomright()[1] // 2)
                                        ypos = mapy + spritey - sprite.bottomright()[0]
                                        if ypos >= 0 and xpos >= 0:
                                            self.map.set_xy(xpos, ypos, char_to_use,"o")
        self.map.set_collision(self.sprites)
    
    def can_move(self, sprite, move_x = 0, move_y = 0):
        """Check if there are any characters in the area that the sprite would take up."""
        assert (move_x >= -1 and move_x <= 1 and move_y >= -1 and move_x <= 1), "move_y and move_x can only be -1, 0, or 1."
        for y in range((move_y*sprite.yspeed) + sprite.originy - sprite.bottomright()[0],(move_y*sprite.yspeed) + sprite.originy + 1):
            for x in range(move_x + sprite.originx - (sprite.bottomright()[1] // 2),move_x + sprite.originx + sprite.bottomright()[1]):
                if self.map.collision_map[y][x] != BLANK and self.map.collision_map[y][x] != sprite.char:
                    return False
        return True

class Map():
    """Three arrays are stored in a Map object: the user input map, the output map, and a collision map.
    Set the map path upon initialization"""

    def __init__(self):
        self.path = ""
        self.input_map = [] # The input_map will always be exactly what is in the map file.
        self.output_map = [] # set using the set_output_map function in the GameObject class.
        self.collision_map = [] # same as the input_map, with each char thickened to the width of its sprite

    def set_collision(self,sprites):
        self.in_to_col()
        assert len(self.output_map) > 0, "Error: Output map has not been created"
        for sprite in sprites.sprites:
            if len(sprite.char) > 0:
                length = len(sprite.array[0]) # Get the width of a sprite
                # ERROR: width is not consistent. Sprites aren't 
                for y in range(len(self.output_map)):
                    for x in range(len(self.output_map[y])):
                        if self.input_map[y][x] == sprite.char:
                            if sprite.geometry == "line":
                                for x2 in range(length):
                                    self.set_xy(x-(length//2)+x2 + 1,y,sprite.char,"c") # place sprite char on collision map
                            elif sprite.geometry == "all":
                                for y2 in range(len(sprite.array)):
                                    for x2 in range(len(sprite.array[0])):
                                        xpos = x + x2 - (sprite.bottomright()[1] // 2)
                                        ypos = y + y2 - sprite.bottomright()[0]
                                        if ypos >= 0 and xpos >= 0:
                                            self.set_xy(xpos, ypos, sprite.char,"c")

    def translate(self):
        self.store_map()
        self.input_map = grid_patcher(self.input_map)
        self.in_to_out()

    def in_to_out(self):
        if len(self.output_map) == 0:
            for y in range(len(self.input_map)):
                self.output_map.append(self.input_map[y][:])
        else:
            assert len(self.input_map[-1]) == len(self.output_map[0]), "Error: maps are not the same sizes"
            for y in range(len(self.input_map)):
                self.output_map[y] = self.input_map[y][:]
    
    def in_to_col(self):
        if len(self.collision_map) == 0:
            for y in range(len(self.input_map)):
                self.collision_map.append(self.input_map[y][:])
        else:
            assert len(self.input_map[-1]) == len(self.collision_map[0]), "Error: maps are not the same sizes"
            for y in range(len(self.input_map)):
                self.collision_map[y] = self.input_map[y][:]

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
        for i in range(len(self.output_map)+3):
            print('\033[A\033[F') # This moves the cursor up one. NOT WINDOWS COMPATIBLE
        for yrow in self.output_map: 
            """SET THIS TO OUTPUT MAP NORMALLY"""
            for yitem in yrow:
                # UPDATE: Add check to see if it's any different from the new char
                print(yitem,end="")
            print() # Off to next line
        print()
            
    def set_xy(self,x,y,char,map = "o"):
        try:
            if map == "o":
                self.output_map[y][x] = char
            elif map == "c":
                self.collision_map[y][x] = char
            elif map == "i":
                self.input_map[y][x] = char
        except:
            pass # For going out of window bounds.
    def get_xy(self,x,y,char,map = "o"):
        try:
            if map == "o":
                return self.output_map[y][x] == char
            elif map == "c":
                return self.collision_map[y][x] == char
            elif map == "i":
                return self.input_map[y][x] == char
        except:
            return False # For going out of window bounds.

class Sprites():
    def __init__(self):
        self.path = ""
        self.sprites = []
        self.msprites = [] # a list of indices from sprites

    def get_msprites(self):
        for i in range(len(self.sprites)):
            if self.sprites[i].movement:
                self.msprites.append(i)

    def get_sprites(self):
        curr_img = ""
        curr_array = []
        self.path = DIRPATH + "\\" + self.path # Adds parent directory of running program
        with open(self.path, 'r',encoding='utf-8') as file:
            currentline = file.readline()[:-1] # Removes the \n
            while(currentline):
                if len(currentline) > 0: #No blank lines
                    if currentline[0] == SIGN and currentline[-1] == SIGN: # Begins and ends with SIGN
                        if curr_img != "": # If this is not the first sprite name
                            self.sprites.append(self.Sprite(img = curr_img,array = curr_array))
                            # Adds a newly created sprite with name and array values to the sprites list ^
                            curr_array = []
                        curr_img = currentline[1:-1] # Remove SIGNs
                    else:
                        curr_array.append(currentline)
                currentline = file.readline()[:-1] # Removes the \n
                
    def new(self,img = "", char = "", coords = [-1,-1], movement = False, geometry = "default"):
        """Every spritename possible has already been made from the given spritesheet. This just changes
        data."""
        assert type(self.sprites) == type(list())
        for sprite in self.sprites:
            if sprite.img == img: # Only the sprite name and array cannot change
                sprite.char = char
                sprite.movement = movement
                sprite.geometry = geometry
                sprite.set_origin(coords[0],coords[1])

    
    class Sprite():
        """A Sprite is simply just an image."""
        #You don't need to have the sprite array stored here, just the look-up name.
        def __init__(self,img="", char = "", coords = [-1,-1], array = [], movement = False, geometry = "none"):
            self.img = img
            self.array = array # Array will be found from the sprite sheet text doc.
            self.originx = coords[0]
            self.originy = coords[1]
            self.top_left = [0,0]
            self.bot_right = [0,0]
            self.geometry = geometry # none, line, or all
            self.movement = movement
            self.char = char
            self.xspeed = 1
            self.yspeed = 1

        def set_origin(self,x,y):
            self.originx = x
            self.originy = y
        def set_xy_char(self,x,y,newchar):
            """Change a char at a given coordinate."""
            try:    self.array[y,x] = newchar
            except: pass
        def get_char(self,x:int,y:int):
            """Returns the char stored here in a sprite array."""
            try:    return self.array[y][x]
            except: return BLANK
        def topleft(self):
            """Return coordinate values [x,y] of topleft char in sprite."""
            return [0,0]
        def bottomright(self):
            """Return coordinate values [x,y] of bottomright char in sprite."""
            return [len(self.array)-1,len(self.array[len(self.array)-1])-1]