import time, keyboard, os, random

DIRPATH = os.path.dirname(__file__) # Required to run program in Python3 terminal.
BLANK = ' '
SIGN = '$'
CLR = "\033[2J"
CUR = '\033[A\033[F' # Move the cursor up by one. Not Windows Terminal compatible.
W_WID = 110 # <,
W_HEI = 30 # These are based on the Windows Terminal window at default size.
INFO_HEI=3
WGC = 10 # WINDOW GUIDE CUSHION, the breathing room between the sprite the window follows and the edge of the window.

# Helpful in debugging information.
SPACES = ' ' * 50
LINES = '\n' * 50

def grid_patcher(array:list,map=False):
    """
    Makes arrays rectangular, that is, filled with arrays of all the same length.
    """
    assert len(array) > 0, "Error: Empty array put in."
    max_length = 0
    if map:
        max_length = W_WID
        while len(array) < W_HEI:
            array.insert(0,[BLANK])
    #the length of output_map is the extent of y
    for y in range(0,len(array)):
        if len(array[y]) > max_length:
            max_length = len(array[y])
    #make all columns the same length
    for row in array:
        for s in range(0,max_length - len(row)):
            try: 
                row.append(BLANK)
            except:
                try:
                    row = row + BLANK
                except:
                    print("Error: Row is neither of type list nor string.")
        
    return array

class Game():
    """
    Creates an empty map and empty sprite list. Fill these using map.set_path(path) 
    and objs.get_sprites(path).
    """
    def __init__(self):
        self.map = Map()
        self.objs = Objs()
        self.quit = False

    def run_map(self):
        """Combine the map and the objs and begin the main game loop."""
        assert len(self.objs.sprites) > 0, "Error: No sprites found."
        self.set_output_map() # Put objs into the map based on the input map.
        self.objs.get_mobile_objs() # Compile a list of moveable objs.
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
        """This is what loops for every game tick. It is run by the run_map method."""
        self.s_time = time.time()
        self.movement()
        if self.frames % 10 == 0 and self.frames < 500:
            self.map.w_corner[0] += 1
        self.map.print_all()
        self.run_fps()

    def run_fps(self):
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
            self.move_player(-1)
        if keyboard.is_pressed("d"):
            self.move_player(1)
        if keyboard.is_pressed("w"):
            self.move_player(0,-1)
        if keyboard.is_pressed("s"):
            self.move_player(0,1)
        if keyboard.is_pressed("q"):
            self.quit = True

        # UPDATE: Add leftright movement for goombas
        self.move_lr()
        self.map.in_to_out() # Reset the output map 
        self.set_output_map() # Remap the sprites

    def move_player(self,xdir = 0,ydir = 0):
        """Moves all user-commanded sprites at their given speeds. xdir and ydir must be -1, 0, or 1."""
        for i in self.objs.mobile_objs:
            if self.objs.objs[i].movement == "user":
                obj = self.objs.objs[i]
                if self.can_move(obj,move_y=ydir,move_x=xdir):
                    self.map.set_xy(obj.originx,obj.originy,BLANK,"i") # Clear the space the sprite is at
                    obj.originy += obj.yspeed * ydir
                    obj.originx += obj.xspeed * xdir
                    self.map.set_xy(obj.originx,obj.originy,obj.char,"i") # Set the new coord
                    
    def move_lr(self):
        for i in self.objs.mobile_objs:
            if self.objs.objs[i].movement == "leftright":
                obj = self.objs.objs[i]
                if obj.facing == "right":
                    if self.can_move(obj,move_x=1):
                        self.map.set_xy(obj.originx,obj.originy,BLANK,"i") # Clear the space the sprite is at
                        obj.originx += obj.xspeed
                        self.map.set_xy(obj.originx,obj.originy,obj.char,"i") # Set the new coord
                    else:
                        obj.facing = "left"
                elif obj.facing == "left":
                    if self.can_move(obj,move_x=-1):
                        self.map.set_xy(obj.originx,obj.originy,BLANK,"i") # Clear the space the sprite is at
                        obj.originx -= obj.xspeed
                        self.map.set_xy(obj.originx,obj.originy,obj.char,"i") # Set the new coord
                    else:
                        obj.facing = "right"


    def set_output_map(self):
        """This is necessary to create the Map's Output Map"""
        for obj in self.objs.objs:
            obj.array = grid_patcher(obj.array) # Sprites must be rectangular
            if obj.char != '': # Make sure they have a map char
            # GO through each char in the map by ROW, then COLUMN
                for mapy in range(0,len(self.map.output_map)):
                    for mapx in range(0,len(self.map.output_map[mapy])):
                        # Check if a obj's map char is present on the map.
                        if self.map.get_xy(mapx,mapy,obj.char,"o"):
                            obj.set_origin(mapx,mapy)
                            self.map.output_map[mapy][mapx] = BLANK
                            # If it is, replace an area around that point with the sprite array.
                            for obj_y in range(obj.topleft()[0],obj.bottomright()[0] + 1):
                                for obj_x in range(obj.topleft()[1],obj.bottomright()[1] + 1):
                                    # Only change the char if it has not already been changed
                                    char_to_use = obj.get_char(obj_x,obj_y)
                                    if char_to_use != BLANK or (obj.get_char(obj_x-1,obj_y) != BLANK and obj.get_char(obj_x+1,obj_y) != BLANK):
                                        xpos = mapx + obj_x - (obj.bottomright()[1] // 2)
                                        ypos = mapy + obj_y - obj.bottomright()[0]
                                        if ypos >= 0 and xpos >= 0:
                                            self.map.set_xy(xpos, ypos, char_to_use,"o")
        self.map.set_collision(self.objs)
    
    def can_move(self, obj, move_x = 0, move_y = 0):
        """Check if there are any characters in the area that the obj would take up."""
        assert (move_x >= -1 and move_x <= 1 and move_y >= -1 and move_x <= 1), "move_y and move_x can only be -1, 0, or 1."
        for y in range((move_y*obj.yspeed) + obj.originy - obj.bottomright()[0],(move_y*obj.yspeed) + obj.originy + 1):
            for x in range(move_x + obj.originx - (obj.bottomright()[1] // 2),move_x + obj.originx + obj.bottomright()[1]):
                try: 
                    if self.map.collision_map[y][x] != BLANK and self.map.collision_map[y][x] != obj.char:
                        return False
                except:
                    return False
        return True

class Map():
    """Three arrays are stored in a Map object: the user input map, the output map, and a collision map.
    Set the map path upon initialization"""

    def __init__(self):
        self.path = ""
        self.input_map = [] # The input_map will always be exactly what is in the map file.
        self.output_map = [] # Set using the set_output_map function in the GameObject class.
        self.collision_map = [] # Same as the input_map, with each char thickened to the width of its sprite.
        self.w_corner = [0,0] # These are the map coordinates of the top-left-most item shown in the window. X,Y

    def set_collision(self,objs):
        self.in_to_col()
        assert len(self.output_map) > 0, "Error: Output map has not been created"
        for obj in objs.objs:
            if len(obj.char) > 0:
                length = len(obj.array[0]) # Get the width of a sprite
                # ERROR: width is not consistent. Sprites aren't 
                for y in range(len(self.output_map)):
                    for x in range(len(self.output_map[y])):
                        if self.input_map[y][x] == obj.char:
                            if obj.geometry == "line":
                                for x2 in range(length):
                                    self.set_xy(x-(length//2)+x2 + 1,y,obj.char,"c") # place sprite char on collision map
                            elif obj.geometry == "all":
                                for y2 in range(len(obj.array)):
                                    for x2 in range(len(obj.array[0])):
                                        xpos = x + x2 - (obj.bottomright()[1] // 2)
                                        ypos = y + y2 - obj.bottomright()[0]
                                        if ypos >= 0 and xpos >= 0:
                                            self.set_xy(xpos, ypos, obj.char,"c")

    def set_path(self,path=""):
        if len(path)>0:
            self.path = path
        self.store_map()
        self.input_map = grid_patcher(self.input_map,True)
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
            
    def print_all(self):
        row_and_hei = self.w_corner[1] + W_HEI + 1 - INFO_HEI # Addition is expensive, so we only do two assignments instead.
        item_and_wid = self.w_corner[0] + W_WID + 1 # <-'
        print(CUR * W_HEI)
        for row in range(self.w_corner[1],row_and_hei):
            # UPDATE: Add check to see if it's any different from the new char
            [ print(item,end="") for item in self.output_map[row][self.w_corner[0]:item_and_wid] ]
            print()
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

class Objs():
    def __init__(self):
        self.path = ""
        self.objs = [] # Stores objects. Each includes a sprites key
        self.sprites = dict() # {img:array}
        self.mobile_objs = [] # a list of indices in sprites

    def get_mobile_objs(self):
        for i in range(len(self.objs)):
            if self.objs[i].movement != None or self.objs[i].gravity != None:
                self.mobile_objs.append(i)

    def get_sprites(self,path=""):
        if len(path)>0:
            self.path = path
        curr_img = None
        curr_array = []
        self.path = DIRPATH + "\\" + self.path # Adds parent directory of running program
        with open(self.path, 'r',encoding='utf-8') as file:
            currentline = file.readline()[:-1] # Removes the \n
            while(currentline):
                if len(currentline) > 0: #No blank lines
                    if currentline[0] == SIGN and currentline[-1] == SIGN: # Begins and ends with SIGN
                        if curr_img != None: # If this is not the first sprite name

                            self.sprites[curr_img] = curr_array
                            curr_array = []

                        curr_img = currentline[1:-1] # Remove SIGNs
                    else:
                        curr_array.append(currentline)
                currentline = file.readline()[:-1] # Removes the \n

    def new(self,img="", char = "", coords = [0,0], movement = None, geometry = "all",xspeed = 1,yspeed = 1,health =1,facing='right',gravity=None):
        """Creates an Obj and adds it to the objs list."""
        obj = self.Obj(img, char, coords, movement, geometry,xspeed,yspeed,health,facing,gravity)
        obj.array = self.sprites[img]
        self.objs.append(obj)

    class Obj():
        """A Sprite is simply just an image."""
        def __init__(self,img="", char = "", coords = [0,0], movement = None, geometry = "all",xspeed = 1,yspeed = 1,health =1,facing='right',gravity=None):
            if len(img) == 0:
                self.img = [char]
            else:
                self.img = img
            self.array = [] # Must be set through Objs function new()
            self.originx = coords[0]
            self.originy = coords[1]
            self.top_left = [0,0]
            self.bot_right = [0,0]
            self.geometry = geometry # Options of: None, line, or all.
            self.movement = movement # Options of: None, random, leftright, updown, wasd, arrows
            # UPDATE: Moving objects that share a sprite will choose only one as mobile.
            self.char = char
            self.xspeed = xspeed
            self.yspeed = yspeed
            self.health = health
            self.facing = facing # Options of: up,down,left,right
            self.gravity = gravity # Options of :None,up,down,left,right

        def set_origin(self,x,y):
            self.originx = x
            self.originy = y
    
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