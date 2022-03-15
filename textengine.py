import time, keyboard, os, random
from multiprocessing.pool import ThreadPool
from numpy import newaxis
from playsound import playsound

DIRPATH = os.path.dirname(__file__)
# Required to run program in Python3 terminal.
BLANK = ' '
SIGN = '$'
CLR = "\033[2J"
CUR = '\033[A\033[F'
ZER = '\033[H'
RIT = '\033[1C'
MAX_TICK = 16
# Move the cursor up by one. Not Windows Terminal compatible.
W_WID = 110
W_HEI = 30
# Based on the Windows Terminal window at default size.
# UPDATE: add function to detect window dimensions/set them.
INFO_HEI=3
WGC_X = W_WID//2 - 5
WGC_Y = W_HEI//2 - 5
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
    # The length of out_map is the extent of y.
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

FLIP_CHARS = {'\\':'/','/':'\\','[':']',']':'[','{':'}','}':'{','<':'>',
    '>':'<','(':')',')':'(','◐':'◑','◑':'◐','↙':'↘','↘':'↙','כ':'c',
    'c':'כ','◭':'◮','◮':'◭','╱':'╲','╲':'╱','↖':'↗','↗':'↖','⌋':'⌊',
    '⌊':'⌋'}
# Dictionary of chars (keys) and their opposites (values)

class Game():
    """
    Creates an empty map and empty sprite list.
    Fill these using map.set_path(path) and objs.get_sprites(path).
    """
    def __init__(self):
        self.map = Map()
        self.objs = Objs()
        self.quit = False
        self.camera_follow = []
        self.theme = ""

        self.frames = 0
        self.tick = 0
        self.f_time = 0
        self.fpss = []
        self.start_time = 0
        self.waiting = 0
        self.game_speed = 0
        self.total = 0

        self.pool = ThreadPool(processes=1)

    def run_game(self):
        """Combine the map and the objs and begin the main game loop."""
        self.init_map()
        self.play_theme()
        while(not self.quit):
            self.game_loop()
        self.end_game()

    def init_map(self):
        """All that comes before the main game_loop"""
        self.create_map()
        self.objs.set_live_objs()
        print(CLR)
        self.start_time = time.time()

    def end_game(self):
        """All the comes after the main game_loop"""
        self.pool.terminate()
        self.pool.join()
        self.total = self.frames/(time.time()-self.start_time)
        print(f"{SPACES}Game Over!\nAverage FPS: {self.total:.3f}")
        scores = []
        for obj in self.objs.objs:
            if obj.move == "wasd":
                scores.append('Player 1: ' + str(obj.score))
            elif obj.move =="dirs":
                scores.append('Player 2: ' + str(obj.score))
        print(f"Scores: {scores}")
        input("Press ENTER to exit.\n")

    def game_loop(self):
        """This is what loops for every game tick.
        It is run by the run_game method."""
        self.wait()
        self.move()
        self.map.print_all()
        #self.debug_maps()
        self.run_fps()
    
    def wait(self):
        self.loop_time = time.time()
        while(self.waiting<self.game_speed):
            self.waiting = time.time() - self.loop_time
        self.waiting = 0

    def run_fps(self):
        self.frames += 1
        self.tick = (self.tick + 1)%MAX_TICK
        self.f_time = time.time()
        print("FPS:",1/(self.f_time-self.loop_time))
        self.fpss.append(self.f_time)

    def debug_maps(self):
        print("input")
        for y in self.map.inp_map:
            for x in y:
                print(x,end="")
            print()
        print("output")
        for a in self.map.out_map:
            for b in a:
                print(b,end="")
            print()
        print("collision")
        for c in self.map.geom_map:
            for d in c:
                print(d,end="")
            print()
        print()

    def play_theme(self):
        self.pool.apply_async(self.theme_loop)
    def theme_loop(self):
        """Add this function to thread 2."""
        if len(self.theme) > 0:
            while True:
                playsound(self.theme)
        else:
            time.sleep(1)

    def move(self):
        if keyboard.is_pressed("q"):
            self.quit = True
        if keyboard.is_pressed("p"):
            keyboard.wait("p")
        self.objs.set_live_objs()
        for i in self.objs.live_objs:
            obj = self.objs.objs[i]
            # PLAYER MOVEMENT
            if obj.move == "wasd":
                if keyboard.is_pressed("w"):    self.move_up(obj)
                if keyboard.is_pressed("e"):    obj.rotate_right()
                if keyboard.is_pressed("a"):    self.move_left(obj)
                if keyboard.is_pressed("s"):    self.move_down(obj)
                if keyboard.is_pressed("d"):    self.move_right(obj)
            elif obj.move == "dirs":
                if keyboard.is_pressed("up arrow"): self.move_up(obj)
                if keyboard.is_pressed("/"):    obj.rotate_right()
                if keyboard.is_pressed("left arrow"):self.move_left(obj)
                if keyboard.is_pressed("down arrow"):self.move_down(obj)
                if keyboard.is_pressed("right arrow"):self.move_right(obj)
            elif self.objs.objs[i].move == "leftright":
                if self.map.w_corner[1] + W_WID + WGC_X > self.objs.objs[i].origx > self.map.w_corner[1] -WGC_X:
                    obj = self.objs.objs[i]
                    if obj.face_right:
                        if self.can_move(obj,move_x=obj.xspeed):
                            self.move_right(obj)
                        else:
                            obj.flip_sprite()
                    else:
                        if self.can_move(obj,move_x=-obj.xspeed):
                            self.move_left(obj)
                        else:
                            obj.flip_sprite()
            # ALL THAT SHOULD FALL WILL FALL
            if obj.grav_tick > 0:
                if self.frames % obj.grav_tick == 0:
                    if obj.jump != 0 and keyboard.is_pressed("w"):
                        self.move_obj(obj,0,-obj.jump)
                        obj.jump -= 1
                    else:   self.move_obj(obj,0,obj.yspeed)
            # DAMAGE-TAKING
            for e_char in obj.enemy_chars:
                self.take_dmg(obj,e_char)

            # CAMERA-MOVING
            if "x" in self.camera_follow:
                if obj.move in ["wasd","dirs"]:
                    if self.map.w_corner[1] + W_WID - WGC_X < obj.origx:
                        self.map.w_corner[1] += obj.xspeed
                    elif self.map.w_corner[1] + WGC_X > obj.origx:
                        if self.map.w_corner[1] > 0:
                            self.map.w_corner[1] -= obj.xspeed
            if "y" in self.camera_follow:
                    if self.map.w_corner[0] + W_HEI - WGC_Y < obj.origy:
                        self.map.w_corner[0] += obj.yspeed
                    elif self.map.w_corner[0] + WGC_Y > obj.origy:
                        if self.map.w_corner[0] > 0:
                            self.map.w_corner[0] -= obj.yspeed

        # GAME-ENDING CHECKS:
        i = 0
        while i < len(self.objs.live_objs):
            obji = self.objs.live_objs[i]
            curr_obj = self.objs.objs[obji]
            if curr_obj.move in ["wasd","dirs"]:
                if curr_obj.hp <= 0 or curr_obj.origy == len(self.map.out_map) -1:
                    self.quit = True
                    curr_obj.array = [['d','e','a','d']]
                pass
            else: # All non-player mobs, DEATH
                if curr_obj.hp <= 0:
                    self.map.inp_map[curr_obj.origy][curr_obj.origx] = BLANK
                    curr_obj.set_origin(0,0)
                    curr_obj.array = [[' ']]
                    curr_obj.move = None
            i+=1
        
        self.map.copy_inp_map(self.map.out_map) # Reset the output map 
        self.create_map() # Remap the sprites

    #Functions for better Readability
    def move_left(self,obj):
        if obj.face_right:
            obj.flip_sprite()
        self.move_obj(obj,-obj.xspeed)
    def move_right(self,obj):   
        if not obj.face_right:
            obj.flip_sprite()
        self.move_obj(obj,obj.xspeed)
    def move_up(self,obj):
        if not obj.grav_tick: # If no gravity then do this
            self.move_obj(obj,0,-obj.yspeed)
        elif not self.can_move(obj,0,1):
            # If on top of something
                obj.jump = obj.yspeed
                self.move_obj(obj,0,0-obj.yspeed)
    def move_down(self,obj):    self.move_obj(obj,0,obj.yspeed)

    def replace_chars(self,obj,new_char):
        """ Replaces the characters of an object on the
        INPUT_MAP with new_char."""
        new_obj = self.obj_from_char(new_char)
        # Only works correctly when width of obj sprite is divisible
        # by width of new_obj
        for y in range((obj.bot_right_y()//len(new_obj.array))+1):
            for x in range(1,obj.bot_right_x()//len(new_obj.array[0])+2):
                newx = obj.topleft[0] + x*len(new_obj.array[0])
                newy = obj.topleft[1] + y*len(new_obj.array)
                if not self.map.is_xy(newx,newy,BLANK,"o") or self.map.is_xy(newx,newy,obj.char,"o"):
                    self.map.set_xy(newx-1,newy,new_char,"i")

    def set_new_img(self,obj,new_img):
        obj.img = new_img
        obj.array = self.objs.sprites[obj.img]
        obj.rotate = 0

    def obj_from_char(self,char):
        for obj in self.objs.objs:
            if obj.char == char:
                return obj

    def take_dmg(self,obj,e_char):
        enemy = self.obj_from_char(e_char)
        if self.should_take_dmg(obj,enemy,e_char):
            obj.hp -= enemy.dmg
    def should_take_dmg(self,obj,enemy,e_char):
        """ Check all sides of an object for enemy chars
        on the geom_map"""
        xs = obj.topleft[0]
        xf = xs+obj.bot_right_x()+1
        ys = obj.topleft[1]
        yf = ys+obj.bot_right_y()+1
        try:
            if 'down' in enemy.dmg_dirs:
                if e_char in self.map.geom_map[ys-1][xs:xf]: #ABOVE
                    return True
            if 'up' in enemy.dmg_dirs:
                if e_char in self.map.geom_map[yf][xs:xf]: #BELOW
                    return True
            for y in range(ys,yf):
                if 'right' in enemy.dmg_dirs:
                    if self.map.geom_map[y][xs] == e_char: #LEFT
                        return True
                if 'left' in enemy.dmg_dirs:
                    if e_char in self.map.geom_map[y][xf+1] == e_char: #RIGHT
                        return True
        except:
            pass
        return False

    def teleport_obj(self,obj,y:int=0,x:int=0,char_left=BLANK,leave_shadow=False):
        if leave_shadow:
            self.objs.new(img=obj.img,char=char_left,coords=[obj.origx,obj.origy],
            geom="complex",set_rotate=obj.rotate) # Deprecated
        if self.map.is_xy(obj.origx,obj.origy,obj.char,"i"):
            # If char has not already been replaced
            self.map.set_xy(obj.origx,obj.origy,char_left,"i")
        obj.set_origin(x,y)
        self.map.set_xy(obj.origx,obj.origy,obj.char,"i")

    def move_obj(self,obj,move_x:int = 0,move_y:int = 0):
        """Moves a single object move_x and move_y amount OR LESS."""
        while move_x != 0 or move_y != 0:
            if self.can_move(obj,move_x,move_y):
                self.map.set_xy(obj.origx,obj.origy,BLANK,"i")
                # Clears the space the sprite is at.
                obj.set_origy(obj.origy+move_y)
                obj.set_origx(obj.origx+move_x)
                self.map.set_xy(obj.origx,obj.origy,obj.char,"i")
                # Sets the new coord.
                move_x,move_y = 0,0
            else:
                if move_x != 0:
                    move_x += int((move_x*-1)/(abs(move_x)))
                if move_y != 0:
                    move_y += int((move_y*-1)/(abs(move_y)))
                # This brings move_x and move_y 1 closer to 0
                # Whether they're negative or positive
    
    def can_move(self, obj, move_x = 0, move_y = 0):
        """Check if there are any characters in the
         area that the obj would take up. Takes literal change in x and y.
         Returns True if character can move in that diRECTion."""
        if obj.geom == "all":
            while (move_x != 0 or move_y != 0):
                for y in range(move_y + obj.origy - obj.bot_right_y(),move_y + obj.origy + 1):
                    for x in range(move_x + obj.topleft[0] + 1,move_x + obj.topleft[0] + obj.bot_right_x()+2):
                        try:
                            if self.map.geom_map[y][x] != BLANK and self.map.geom_map[y][x] != obj.char:
                                return False
                        except:
                            return False
                if move_x != 0:
                    move_x += int((move_x*-1)/(abs(move_x)))
                if move_y != 0:
                    move_y += int((move_y*-1)/(abs(move_y)))
            return True
        elif obj.geom == "line":
            while (move_x != 0 or move_y != 0):
                for x in range(move_x + obj.topleft[0] + 1,move_x + obj.topleft[0] + obj.bot_right_x()+2):
                    try:
                        if self.map.geom_map[obj.origy+move_y][x] != BLANK:
                            if self.map.geom_map[obj.origy+move_y][x] != obj.char:
                                return False
                    except:
                        return False
                if move_x != 0:
                    move_x += int((move_x*-1)/(abs(move_x)))
                if move_y != 0:
                    move_y += int((move_y*-1)/(abs(move_y)))
            return True
        elif obj.geom == "complex":
            while (move_x != 0 or move_y != 0):
                for y in range(obj.origy - obj.bot_right_y(),obj.origy + 1):
                    for x in range(obj.topleft[0] + 1,obj.topleft[0] + obj.bot_right_x()+2):
                        try:
                            if self.map.geom_map[y][x] != BLANK:
                                if self.map.geom_map[y+move_y][x+move_x] != BLANK:
                                    if self.map.geom_map[y+move_y][x+move_x] != obj.char:
                                        return False
                        except:
                            return False
                if move_x != 0:
                    move_x += int((move_x*-1)/(abs(move_x)))
                if move_y != 0:
                    move_y += int((move_y*-1)/(abs(move_y)))
            return True

    def create_map(self):
        """This is necessary to create the Map's Output Map.
        A new object will be created for each sprite that is both
        on the map and in the sprite dictionary."""
        for mapy in range(0,len(self.map.out_map)):
          for mapx in range(0,len(self.map.out_map[mapy])):
            if not self.map.is_xy(mapx,mapy,BLANK,'o'): #SKIP BLANKS (DUH)
                for obji in range(len(self.objs.objs)):
                # Goes by range so that it doesn't go through newly-added objs.
                    obj = self.objs.objs[obji]
                    curr_obj = obj # curr_obj is the pointer this func ops on.
                    if curr_obj.char != '': # Make sure they have a map char
                        # Check if a obj's map char is present on the map.
                        if self.map.is_xy(mapx,mapy,curr_obj.char,"o"):
                            if not self.map.inited:
                                if curr_obj.move != None or curr_obj.grav_tick > 0:
                                # Objs that never move won't have special attributes.
                                    if curr_obj.get_origin() != [0,0]:
                                    # Makes sure it's not the only obj, and has a set coord.
                                        curr_obj = self.objs.copy(obji)
                                curr_obj.set_origin(mapx,mapy)
                            self.map.set_xy(mapx, mapy, BLANK,"o") # remove origin char
                            # Print a sprite around its origin.
                            maxx = curr_obj.bot_right_x()
                            for obj_y in range(curr_obj.bot_right_y() + 1):
                                blanks_before = True
                                blanks_after = True
                                for obj_x in range(maxx//2 + 1):
                                    char = curr_obj.get_char(obj_x,obj_y)
                                    if char != BLANK or not blanks_before:
                                        blanks_before = False
                                        ypos = mapy + obj_y - curr_obj.bot_right_y()
                                        xpos = mapx + obj_x - (maxx // 2)
                                        self.map.set_xy(xpos, ypos, char,"o")
                                    char = curr_obj.get_char(maxx-obj_x,obj_y)
                                    if char != BLANK or not blanks_after:
                                        blanks_after = False
                                        ypos = mapy + obj_y - curr_obj.bot_right_y()
                                        xpos = mapx - obj_x + (maxx // 2) + maxx%2
                                        self.map.set_xy(xpos, ypos, char,"o")
        self.map.inited = True
        self.map.set_geom(self.objs)
        self.remove_extras()

    def remove_extras(self):
        i = 0
        while i < len(self.objs.objs):
            if self.objs.objs[i].get_origin() == [0,0]:
                self.objs.objs.pop(i)
            else:
                i+=1

class Map():
    """Three arrays are stored in a Map object: the wasd input 
    map, the output map, and a geom map.
    Set the map path upon initialization"""

    def __init__(self):
        self.path = ""
        self.inp_map = [] # Map of sprite origin coords.
        self.sparse_map = []
        # Stores each input map char and its coordinates.
        self.out_map = []
        # Set using the create_map function in the GameObject class.
        self.geom_map = [] # For checking collision.
        self.w_corner = [0,0] # Y,X
        # These are the map coordinates of the 
        # top-left-most item shown in the window.
        self.inited = False

    def set_geom(self,objs):
        """Called after the input and output maps have been made."""
        self.copy_inp_map(self.geom_map)
        last_obj = None
        assert len(self.out_map) > 0, "Error: Output map has not been created"
        for y in range(len(self.out_map)):
            for x in range(len(self.out_map[y])):
                if not self.is_xy(x,y,BLANK,"i"): # Skip blank spots.
                    # Find the object belonging to the character on OUT_MAP.
                    found = False
                    if last_obj != None and last_obj.char == self.get_xy(x,y,"i"):
                        found = True
                        obj = last_obj
                        # Checks to see if this char is the same as the last
                        # Theoretically improves efficiency
                    else:
                        i = 0
                        while i < len(objs.objs) and not found:
                            obj = objs.objs[i]
                            if obj.char == self.get_xy(x,y,"i"):
                                last_obj = obj
                                found = True
                            else: i +=1
                    if found:
                        length = len(obj.array[0]) # Get the width of a sprite.
                        # Remove the collision point that came from the input map
                        if obj.geom == "line":
                            for x2 in range(length):
                                if obj.array[-1][x2] != BLANK:
                                    self.set_xy(x - (length//2) + x2 + 1,y,obj.char,"c")
                                    # place sprite char on geom map
                        elif obj.geom == "all":
                            for y2 in range(len(obj.array)):
                                for x2 in range(len(obj.array[0])):
                                    ypos = y + y2 - obj.bot_right_y()
                                    xpos = x + x2 - (obj.bot_right_x() // 2)
                                    self.set_xy(xpos, ypos, obj.char,"c")
                        elif obj.geom == "complex":
                            # Based on all characters of a sprite that are not blank.
                            self.set_xy(x, y, BLANK,"c")
                            for y2 in range(len(obj.array)):
                                for x2 in range(len(obj.array[0])):
                                    ypos = y + y2 - obj.bot_right_y()
                                    xpos = x + x2 - obj.bot_right_x() // 2
                                    if obj.array[y2][x2] != BLANK:
                                        self.set_xy(xpos, ypos, obj.char,"c")

    def set_path(self,path=""):
        if len(path)>0:
            self.path = path
        self.store_map()
        self.inp_map = grid_patcher(self.inp_map,True)
        self.copy_inp_map(self.out_map)

    def copy_inp_map(self,copy):
        if len(copy) == 0:
            for y in range(len(self.inp_map)):
                copy.append(self.inp_map[y][:])
        else:
            assert len(self.inp_map[-1]) == len(copy[0]),"Error: maps are not the same sizes"
            for y in range(len(self.inp_map)):
                copy[y] = self.inp_map[y][:]

    def store_map(self):
        """ Stores text from file as 2D array or list:
        [[x1,x2,x3],[x1,x2,x3]]
        Reads from the preset path, saves to inp_map """
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
        """Uses coordinate-based printing. Comparatively slow.
        Sprite-based printing is faster since it literally prints
        less. print_objs() is found in the Game class."""
        row_and_hei = self.w_corner[0] + W_HEI
        # Addition is expensive, so we only do two assignments instead.
        wid = self.w_corner[1] + W_WID + 1 # <-'
        print(CUR * (W_HEI+INFO_HEI))
        for row in range(self.w_corner[0],row_and_hei):
        # UPDATE: Add check to see if it's any different from the new char
            [print(i,end="") for i in self.out_map[row][self.w_corner[1]:wid]]
            print()
        print()
            
    def set_xy(self,x,y,char,map = "o"):
        """Sets the character at a given position."""
        if x > -1 < y:
            try:
                if map == "o":
                    self.out_map[y][x] = char
                elif map == "c":
                    self.geom_map[y][x] = char
                elif map == "i":
                    self.inp_map[y][x] = char
            except:
                pass # For going out of bounds.
    def is_xy(self,x,y,char,map = "o"):
        """Returns if a certain character is at this position."""
        try:
            if map == "o":
                return self.out_map[y][x] == char
            elif map == "c":
                return self.geom_map[y][x] == char
            elif map == "i":
                return self.inp_map[y][x] == char
        except:
            return False # For going out of bounds.
    def get_xy(self,x,y,map = "o"):
        """Returns what characters is at this position."""
        try:
            if map == "o":
                return self.out_map[y][x]
            elif map == "c":
                return self.geom_map[y][x]
            elif map == "i":
                return self.inp_map[y][x]
        except:
            return BLANK # For going out of bounds.

class Objs():
    def __init__(self):
        self.path = ""
        self.objs = [] # Stores objects. Each includes a sprites key
        self.sprites = dict() # {img:array}
        self.live_objs = [] # a list of indices in sprites

    def set_live_objs(self):
        self.live_objs = list()
        for i in range(len(self.objs)):
            if self.objs[i].move != None or self.objs[i].grav_tick > 0:
                self.live_objs.append(i)

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
                        curr_array.append(list(curr_line))
                curr_line = file.readline()[:-1] # Removes the \n

    def new(self,img="", char = "", coords = [0,0], move = None,
        geom = "all", xspeed = 1,yspeed = 1,hp =1,face_right=True,face_down=False,
        grav_tick=0,dmg = 1,enemy_chars=[],dmg_dirs=[],set_rotate=0,
        spawn=[0,0],animate=True):
        """Creates an Obj and appends it to the objs list."""
        obj = self.Obj(img, char, coords, move, geom,xspeed,yspeed,
            hp,face_right,face_down,grav_tick,dmg,enemy_chars,dmg_dirs,
            spawn,animate)
        obj.array = self.sprites[img]
        while obj.rotate != set_rotate:
            obj.rotate_right()
        self.objs.append(obj)

    def copy(self,obji):
        """Makes a copy of an object from its objs index and appends
         that to the objs list."""
        o = self.objs[obji]
        self.new(o.img,o.char,[o.origx,o.origy],o.move,o.geom,o.xspeed,o.yspeed,o.hp,
            o.face_right,o.face_down,o.grav_tick,o.dmg,o.enemy_chars,o.dmg_dirs,o.rotate,
            o.spawn,o.animate)
        return self.objs[-1]

    class Obj():
        """A Sprite is simply just an image."""
        def __init__(self,img:str="", char = "", coords = [0,0], move = None, 
        geom:str = "all",xspeed = 1,yspeed = 1,hp =1,face_right=True,
        face_down=False,grav_tick:int=0,dmg = 1,enemy_chars=[],dmg_dirs=[],
        spawn=[0,0],animate=True):
            if not len(img): # If there is no img.
                self.img = [char]
            else:
                self.img = img
            self.origx = coords[0]
            self.origy = coords[1]
            self.topleft = [0,0] # STORED IN X,Y FORM.
            self.geom = geom # Options of: None, line, complex, or all.
            self.move = move
            # Options of: None, random, leftright, updown, wasd, arrows.
            self.char = char
            self.xspeed = xspeed
            self.yspeed = yspeed
            self.hp = hp
            self.grav_tick = grav_tick
            self.jump = 0 # based on yspeed
            self.dmg = dmg
            self.enemy_chars = enemy_chars
            self.dmg_dirs = dmg_dirs
            self.spawn = spawn
            self.animate = animate

            self.face_right = face_right # Left: False, Right: True
            self.face_down = face_down # Up: False, Down: True
            self.array = [] # Must be set through Objs function new().
            self.rotate = 0 # 0 through 3
            self.score = 0

        def set_origin(self,x,y):
            self.set_origx(x)
            self.set_origy(y)
        def set_origx(self,x):
            self.origx = x
            self.topleft[0] = self.origx - len(self.array[0])//2 - len(self.array[0])%2
        def set_origy(self,y):
            self.origy = y
            self.topleft[1] = self.origy + 1 - len(self.array)

        def get_origin(self):
            return [self.origx,self.origy]
    
        def get_char(self,x:int,y:int):
            """Returns the char stored here in a sprite array.
            Takes x,y, returns [y][x]"""
            try:    return self.array[y][x]
            except: return BLANK
            
        def bot_right(self):
            """Return coord vals [Y,X] of bot_right char in sprite.
            The map coord vals are stored in the topleft var."""
            return [len(self.array[0])-1,len(self.array)-1]
        def bot_right_x(self):
            """Get the far right x value of the object sprite"""
            return len(self.array[0]) - 1
        def bot_right_y(self):
            """Get the far right y value of the object sprite"""
            return len(self.array)-1
        
        def flip_sprite(self):
            """Flips the sprite of an image vertically (left to right)"""
            self.face_right = not self.face_right
            if self.animate:
                maxx = len(self.array[0])
                for y in range(len(self.array)):
                    for x in range(maxx//2+maxx%2):
                        hold = self.array[y][x]
                        if hold in FLIP_CHARS.keys():
                            hold = FLIP_CHARS[hold]
                        self.array[y][x] = self.array[y][maxx-x-1]
                        if self.array[y][x] in FLIP_CHARS.keys():
                            self.array[y][x] = FLIP_CHARS[self.array[y][x]]
                        self.array[y][maxx-x-1] = hold

        def rotate_right(self):
            """Rotates the object sprite 90 degrees."""
            self.rotate = (self.rotate + 1)%4
            # Only works properly on even-width objects.
            sprite = [] # Must make a new sprite sequentially,
            for x in range(len(self.array[0])//2):
                row = [] # otherwise it creates pointers.
                for y in range(len(self.array)*2):
                    row.append(BLANK)
                sprite.append(row)
            # To rotate, it is inverted, and then mirrored along y.
            for y in range(len(sprite)):
                for x in range(len(sprite[0])//2):
                    sprite[y][-((x*2)+2)] = self.array[x][(y*2)]
                    sprite[y][-((x*2)+1)] = self.array[x][(y*2)+1]
            self.array = sprite