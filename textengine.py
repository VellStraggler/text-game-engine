import time, keyboard, os, random
from playsound import playsound

DIRPATH = os.path.dirname(__file__)
# Required to run program in Python3 terminal.
BLANK = ' '
SIGN = '$'
CLR = "\033[2J"
CUR = '\033[A\033[F'
# Move the cursor up by one. Not Windows Terminal compatible.
W_WID = 110
W_HEI = 30
# These are based on the Windows Terminal window at default size.
# UPDATE: add function to detect window dimensions/set them.
INFO_HEI=3
WGC_X = 20
WGC_Y = WGC_X//2
# WINDOW GUIDE CUSHION, the breathing room between the sprite between
# the window follows and the edge of the window.

# Helpful in debugging information.
SPACES = ' ' * 50
LINES = '\n' * 50
BAD_CHARS = "⚫"

def grid_patcher(array:list,map=False):
    """Makes arrays rectangular, that they are filled with arrays of
     uniform length."""
    assert len(array) > 0, "Error: Empty array put in."
    max_length = 0
    if map:
        max_length = W_WID
        while len(array) < W_HEI:
            array.insert(0,[BLANK])
    # The length of output_map is the extent of y.
    for y in range(0,len(array)):
        if len(array[y]) > max_length:
            max_length = len(array[y])
    # Makes all columns the same length.
    for row in array:
        for s in range(0,max_length - len(row)):
            if type(row) == type(list()): 
                row.append(BLANK)
            elif type(row) == type(str()):
                row = row + BLANK
            else:
                assert False, "Only strings and lists can be in the array"
    return array

class Game():
    """
    Creates an empty map and empty sprite list.
    Fill these using map.set_path(path) and objs.get_sprites(path).
    """
    def __init__(self):
        self.map = Map()
        self.objs = Objs()
        self.quit = False

        self.frames = 0
        self.f_time = 0
        self.fpss = []
        self.start_time = 0
        self.waiting = 0
        self.waitmax = .01

    def run_map(self):
        """Combine the map and the objs and begin the main game loop."""
        assert len(self.objs.sprites) > 0, "Error: No sprites found."
        self.set_output_map()
        # Put objs into the map based on the input map.
        self.objs.get_mobile_objs() # Compile a list of moveable objs.
        print(CLR)
        self.map.print_all()
        self.start_time = time.time()
        while(not self.quit):
            self.game_loop()
        #total = self.frames/(time.time()-self.start_time)
        #print(f"Game Over. Average FPS: {total:.3f}")
        print(f"{SPACES}Game Over!")
        input("Press ENTER to exit.\n")

    def game_loop(self):
        """This is what loops for every game tick.
        It is run by the run_map method."""
        # Update Frame
        self.wait()
        self.move()
        self.map.print_all()
        #self.run_fps()
        # Lag Frame
        #self.wait()
        #self.map.print_all()
        #self.run_fps()
    
    def wait(self):
        self.loop_time = time.time()
        while(self.waiting<self.waitmax):
            self.waiting = time.time() - self.loop_time
        self.waiting = 0

    def run_fps(self):
        self.frames += 1
        self.f_time = time.time()
        print("FPS:",1/(self.f_time-self.loop_time))
        self.fpss.append(self.f_time)

    def debug_maps(self):
        """
        print("input")
        for y in self.map.inp_map:
            for x in y:
                print(x,end="")
            print()
        print("output")
        for a in self.map.output_map:
            for b in a:
                print(b,end="")
            print()
        """
        print("collision")
        for c in self.map.coll_map:
            for d in c:
                print(d,end="")
            print()
        print()

    def move(self):
        for i in self.objs.mobile_objs:
            obj = self.objs.objs[i]
            if obj.move == "wasd":
                if keyboard.is_pressed("a"):
                    self.move_player(obj,0-obj.xspeed)
                if keyboard.is_pressed("d"):
                    self.move_player(obj,obj.xspeed)
                if keyboard.is_pressed("w"):
                    if not obj.grav: # If no gravity then do this
                        self.move_player(obj,0,0-obj.yspeed)
                    else:
                        if not self.can_move(obj,0,1):
                        # If on top of something
                            obj.jump = obj.yspeed
                            self.move_player(obj,0,0-obj.yspeed)
                if keyboard.is_pressed("s"):
                    self.move_player(obj,0,obj.yspeed)
                if keyboard.is_pressed("q"):
                    self.quit = True
            # ALL THAT SHOULD FALL WILL FALL
            if obj.grav:
                if obj.jump != 0:
                    self.move_player(obj,0,-obj.jump)#(obj.yspeed))
                    obj.jump -= 1
                else:
                    self.move_player(obj,0,obj.yspeed)
            # DAMAGE-TAKING
            if len(obj.enemy_chars) > 0:
                for e_char in obj.enemy_chars:
                    #print(obj.topleft[0],obj.topleft[1],obj.hp)
                    if self.should_take_dmg(obj,e_char):
                        enemy = self.obj_from_char(e_char)
                        obj.hp -= enemy.dmg
            # CAMERA-MOVING
            if self.map.w_corner[1] + W_WID - WGC_X < obj.origx:
                self.map.w_corner[1] += obj.xspeed

        # UPDATE: Add leftright move for goombas
        self.move_lr()
        self.map.in_to_out() # Reset the output map 
        self.set_output_map() # Remap the sprites

        # GAME-ENDING CHECKS:
        for i in self.objs.mobile_objs:
            if self.objs.objs[i].move == "wasd":
                if self.objs.objs[i].hp <= 0:
                    self.quit = True
                elif self.objs.objs[i].origy == len(self.map.output_map) -1:
                    self.quit = True

    def obj_from_char(self,char):
        for obj in self.objs.objs:
            if obj.char == char:
                return obj

    def should_take_dmg(self,obj,e_char):
        """Check all sides of an object for enemy chars
        on the coll_map"""
        xs = obj.topleft[0]
        xf = xs+obj.bot_right_x()+1
        ys = obj.topleft[1]
        yf = ys+obj.bot_right_y()+1
        try:
            if e_char in self.map.coll_map[ys-1][xs:xf]:
                return True
            if e_char in self.map.coll_map[yf][xs:xf]:
                return True
            for y in range(ys,yf):
                if self.map.coll_map[y][xs] == e_char:
                    return True
                if e_char in self.map.coll_map[y][xf+1] == e_char:
                    return True
        except:
            pass
        return False

    def move_player(self,obj,xamt:int = 0,yamt:int = 0):
        """Moves a single object xamt and yamt amount OR LESS."""
        while xamt != 0 or yamt != 0:
            if self.can_move(obj,xamt,yamt):
                self.map.set_xy(obj.origx,obj.origy,BLANK,"i")
                # Clears the space the sprite is at.
                obj.set_origy(obj.origy+yamt)
                obj.set_origx(obj.origx+xamt)
                self.map.set_xy(obj.origx,obj.origy,obj.char,"i")
                # Sets the new coord.
                xamt,yamt = 0,0
            else:
                if xamt != 0:
                    xamt += int((xamt*-1)/(abs(xamt)))
                if yamt != 0:
                    yamt += int((yamt*-1)/(abs(yamt)))
                # This brings xamt and yamt 1 closer to 0
                # Whether they're negative or positive
                    
    def move_lr(self):
        for i in self.objs.mobile_objs:
            if self.objs.objs[i].move == "leftright":
                obj = self.objs.objs[i]
                if obj.face == "right":
                    if self.can_move(obj,move_x=1):
                        self.map.set_xy(obj.origx,obj.origy,BLANK,"i")
                        # Clear the space the sprite is at.
                        obj.set_origx(obj.origx + obj.xspeed)
                        self.map.set_xy(obj.origx,obj.origy,obj.char,"i")
                        # Set the new coord.
                    else:
                        obj.face = "left"
                elif obj.face == "left":
                    if self.can_move(obj,move_x=-1):
                        self.map.set_xy(obj.origx,obj.origy,BLANK,"i")
                        # Clear the space the sprite is at.
                        obj.set_origx(obj.origx - obj.xspeed)
                        self.map.set_xy(obj.origx,obj.origy,obj.char,"i")
                        # Set the new coord.
                    else:
                        obj.face = "right"

    def set_output_map(self):
        """This is necessary to create the Map's Output Map.
        A new object will be created for each sprite that is both
        on the map and in the sprite dictionary."""
        for obji in range(len(self.objs.objs)):
        # Goes by range so that it doesn't go through newly-added objs.
          obj = self.objs.objs[obji]
          curr_obj = obj # curr_obj is the pointer this func ops on.
          curr_obj.array = grid_patcher(curr_obj.array)
          # Sprites must be rectangular
          if curr_obj.char != '': # Make sure they have a map char
          # GO through each char in the map by ROW, then COLUMN
            for mapy in range(0,len(self.map.output_map)):
              for mapx in range(0,len(self.map.output_map[mapy])):
                # Check if a obj's map char is present on the map.
                if self.map.get_xy(mapx,mapy,curr_obj.char,"o"):
                  if curr_obj.move != None or curr_obj.grav:
                    # Objects that will never move should not have special
                    # attributes.
                    if curr_obj.get_origin() != [-1,-1]:
                    # Makes sure it's not the only obj, and has a set coord.
                        curr_obj = self.objs.copy(obji)
                  curr_obj.set_origin(mapx,mapy)
                  self.map.output_map[mapy][mapx] = BLANK
                  # If it is, replace an area around that point 
                  # with the sprite array.
                  for obj_y in range(curr_obj.bot_right_y() + 1):
                    for obj_x in range(curr_obj.bot_right_x() + 1):
                      # Only change the char if it has not 
                      # already been changed
                      char_to_use = curr_obj.get_char(obj_x,obj_y)
                      if char_to_use != BLANK or (curr_obj.get_char(obj_x-1,obj_y) != BLANK and curr_obj.get_char(obj_x+1,obj_y) != BLANK):
                        ypos = mapy + obj_y - curr_obj.bot_right_y()
                        xpos = mapx + obj_x - (curr_obj.bot_right_x() // 2)
                        if ypos >= 0 and xpos >= 0:
                          self.map.set_xy(xpos, ypos, char_to_use,"o")
        self.map.set_coll(self.objs)
    
    def can_move(self, obj, move_x = 0, move_y = 0):
        """Check if there are any characters in the
         area that the obj would take up. Takes literal change in x and y.
         Returns True if character can move in that diRECTion."""
        while (move_x != 0 or move_y != 0):
            for y in range(move_y + obj.origy - obj.bot_right_y(),move_y + obj.origy + 1):
                for x in range(move_x + obj.origx - (obj.bot_right_x() // 2),move_x + obj.origx + obj.bot_right_x() - 1):
                    try: 
                        if self.map.coll_map[y][x] != BLANK and self.map.coll_map[y][x] != obj.char:
                            return False
                    except:
                        return False
            if move_x != 0:
                move_x += int((move_x*-1)/(abs(move_x)))
            if move_y != 0:
                move_y += int((move_y*-1)/(abs(move_y)))
        return True

class Map():
    """Three arrays are stored in a Map object: the wasd input 
    map, the output map, and a coll map.
    Set the map path upon initialization"""

    def __init__(self):
        self.path = ""
        self.inp_map = [] # Map of sprite origin coords
        self.output_map = []
        # Set using the set_output_map function in the GameObject class.
        self.coll_map = []
        # Same as the inp_map, with each char
        # thickened to the width of its sprite.
        self.w_corner = [0,0] # Y,X
        # These are the map coordinates of the 
        # top-left-most item shown in the window.

    def set_coll(self,objs):
        self.in_to_col()
        assert len(self.output_map) > 0, "Error: Output map has not been created"
        for obj in objs.objs:
            if len(obj.char) > 0:
                length = len(obj.array[0]) # Get the width of a sprite
                for y in range(len(self.output_map)):
                    for x in range(len(self.output_map[y])):
                        if self.inp_map[y][x] == obj.char:
                            if obj.geom == "line":
                                for x2 in range(length):
                                    self.set_xy(x-(length//2)+x2 + 1,y,obj.char,"c")
                                    # place sprite char on coll map
                            elif obj.geom == "all":
                                for y2 in range(len(obj.array)):
                                    for x2 in range(len(obj.array[0])):
                                        ypos = y + y2 - obj.bot_right_y()
                                        xpos = x + x2 - (obj.bot_right_x() // 2)
                                        if ypos >= 0 and xpos >= 0:
                                            self.set_xy(xpos, ypos, obj.char,"c")

    def set_path(self,path=""):
        if len(path)>0:
            self.path = path
        self.store_map()
        self.inp_map = grid_patcher(self.inp_map,True)
        self.in_to_out()

    def in_to_out(self):
        if len(self.output_map) == 0:
            for y in range(len(self.inp_map)):
                self.output_map.append(self.inp_map[y][:])
        else:
            assert len(self.inp_map[-1]) == len(self.output_map[0]),"Error: maps are not the same sizes"
            for y in range(len(self.inp_map)):
                self.output_map[y] = self.inp_map[y][:]
    
    def in_to_col(self):
        if len(self.coll_map) == 0:
            for y in range(len(self.inp_map)):
                self.coll_map.append(self.inp_map[y][:])
        else:
            assert len(self.inp_map[-1]) == len(self.coll_map[0]),"Error: maps are not the same sizes"
            for y in range(len(self.inp_map)):
                self.coll_map[y] = self.inp_map[y][:]

    def store_map(self):
        """
        Stores text from file as 2D array or list: [[x1,x2,x3],[x1,x2,x3]]
        Reads from the preset path, saves to inp_map
        """
        self.path = DIRPATH + "\\" + self.path
        # Adds parent directory of running program
        with open(self.path,'r') as file:
            curr_line = file.readline() # stores first line as string
            while curr_line:
                xlist = [] # Begin a new row of items
                curr_line = curr_line[:-1] # Remove newline calls.
                for char in curr_line:
                    xlist.append(char)
                self.inp_map.append(xlist) # Add row to the inp_map
                curr_line = file.readline()
            
    def print_all(self):
        row_and_hei = self.w_corner[0] + W_HEI + 1 - INFO_HEI
        # Addition is expensive, so we only do two assignments instead.
        item_and_wid = self.w_corner[1] + W_WID + 1 # <-'
        print(CUR * W_HEI)
        for row in range(self.w_corner[0],row_and_hei):
        # UPDATE: Add check to see if it's any different from the new char
            [print(item,end="") for item in self.output_map[row][self.w_corner[1]:item_and_wid]]
            print()
        print()
            
    def set_xy(self,x,y,char,map = "o"):
        try:
            if map == "o":
                self.output_map[y][x] = char
            elif map == "c":
                self.coll_map[y][x] = char
            elif map == "i":
                self.inp_map[y][x] = char
        except:
            pass # For going out of window bounds.
    def get_xy(self,x,y,char,map = "o"):
        try:
            if map == "o":
                return self.output_map[y][x] == char
            elif map == "c":
                return self.coll_map[y][x] == char
            elif map == "i":
                return self.inp_map[y][x] == char
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
            if self.objs[i].move != None or self.objs[i].grav == True:
                self.mobile_objs.append(i)

    def get_sprites(self,path=""):
        if len(path)>0:
            self.path = path
        curr_img = None
        curr_array = []
        self.path = DIRPATH + "\\" + self.path
        # Adds parent directory of running program
        with open(self.path, 'r',encoding='utf-8') as file:
            curr_line = file.readline()[:-1] # Removes the \n
            while(curr_line):
                if len(curr_line) > 0: #No blank lines
                    if curr_line[0] == SIGN and curr_line[-1] == SIGN:
                    # Begins and ends with SIGN
                        if curr_img != None:
                        # If this is not the first sprite name

                            self.sprites[curr_img] = curr_array

                            curr_array = []
                        curr_img = curr_line[1:-1] # Remove SIGNs
                    else:
                        curr_array.append(curr_line)
                curr_line = file.readline()[:-1] # Removes the \n

    def new(self,img="", char = "", coords = [0,0], move = None,
        geom = "all", xspeed = 1,yspeed = 1,hp =1,face='right',
        grav=False,dmg = 1,enemy_chars=[]):
        """Creates an Obj and appends it to the objs list."""
        obj = self.Obj(img, char, coords, move, geom,xspeed,yspeed,
            hp,face,grav,dmg,enemy_chars)
        obj.array = self.sprites[img]
        self.objs.append(obj)

    def copy(self,obji):
        """Makes a copy of an object from its objs index and appends
         that to the objs list."""
        o = self.objs[obji]
        self.new(o.img,o.char,[o.origx,o.origy],o.move,o.geom,o.xspeed,o.yspeed,o.hp,
            o.face,o.grav,o.dmg,o.enemy_chars)
        return self.objs[-1]

    class Obj():
        """A Sprite is simply just an image."""
        def __init__(self,img="", char = "", coords = [-1,-1], move = None, 
        geom = "all",xspeed = 1,yspeed = 1,hp =1,face='right',grav=False, 
        dmg = 1,enemy_chars=[]):
            if len(img) == 0:
                self.img = [char]
            else:
                self.img = img
            self.array = [] # Must be set through Objs function new()
            self.origx = coords[0]
            self.origy = coords[1]
            self.topleft = [0,0] #STORED IN X,Y FORM
            self.bot_right = [0,0]
            self.geom = geom # Options of: None, line, or all.
            self.move = move
            # Options of: None, random, leftright, updown, wasd, arrows
            # UPDATE: Moving objects that share a sprite will
            # choose only one as mobile.
            self.char = char
            self.xspeed = xspeed
            self.yspeed = yspeed
            self.hp = hp
            self.face = face # Options of: up,down,left,right
            self.grav = grav # Boolean
            self.jump = 0 # based on yspeed
            self.dmg = dmg
            self.enemy_chars = enemy_chars

        def set_origin(self,x,y):
            self.set_origx(x)
            self.set_origy(y)

        def set_origx(self,x):
            self.origx = x
            self.topleft[0] = self.origx - len(self.array[0])//2

        def set_origy(self,y):
            self.origy = y
            self.topleft[1] = self.origy + 1 - len(self.array)

        def get_origin(self):
            return [self.origx,self.origy]
    
        def get_char(self,x:int,y:int):
            """Returns the char stored here in a sprite array."""
            try:    return self.array[y][x]
            except: return BLANK
            
        def bot_right(self):
            """Return coord vals [Y,X] of bot_right char in sprite."""
            return [len(self.array[0])-1,len(self.array)-1]
        def bot_right_x(self):
            """Get the far right x value of the object sprite"""
            return len(self.array[0]) - 1
        def bot_right_y(self):
            """Get the far right y value of the object sprite"""
            return len(self.array)-1