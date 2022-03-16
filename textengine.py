from hashlib import new
import time, keyboard, os, random
from multiprocessing.pool import ThreadPool
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

# Dictionary of chars (keys) and their opposites (values)
FLIP_CHARS = {'\\':'/','/':'\\','[':']',']':'[','{':'}','}':'{','<':'>',
    '>':'<','(':')',')':'(','◐':'◑','◑':'◐','↙':'↘','↘':'↙','כ':'c',
    'c':'כ','◭':'◮','◮':'◭','╱':'╲','╲':'╱','↖':'↗','↗':'↖','⌋':'⌊',
    '⌊':'⌋'}

class Game():
    """
    Creates an empty map and empty sprite list.
    Fill these using map.set_path(path) and objs.get_sprites(path).
    """
    def __init__(self):
        self.map = Map()
        self.objs = Objs()
        self.mission = Mission()
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
        while(not self.quit):
            self.game_loop()
        self.end_game()

    def init_map(self):
        """All that comes before the main game_loop"""
        print(CLR)
        self.create_objs()
        self.create_map()
        self.start_time = time.time()
        self.play_theme()

    def end_game(self):
        """All the comes after the main game_loop"""
        self.pool.terminate()
        self.pool.join()
        self.total = self.frames/(time.time()-self.start_time)
        print(f"{SPACES}Game Over!\nAverage FPS: {self.total:.3f}")
        scores = []
        for obj in self.objs.objs:
            if not obj.simple:
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
        self.create_map()
        self.map.print_all()
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
            time.sleep(1)
            keyboard.wait("p")
        id_tracker = []
        i = 0
        to_corner = False
        while i < len(self.objs.objs) and not to_corner:
            obj = self.objs.objs[i]
            if obj.origy < self.map.window[0] - (WGC_Y*2):
                i+=1
            elif obj.origx < self.map.window[1] - (WGC_X*2):
                i+=1
            elif obj.origx > self.map.window[1] + W_WID + (WGC_X*2):
                i+=1
            elif obj.origy > self.map.window[0] + W_HEI + (WGC_Y*2):
                to_corner = True
            else:
                id_tracker.append(obj.id)
                # If obj has been edited before, it should be skipped.
                if len(id_tracker) != len(set(id_tracker)):
                    id_tracker = list(set(id_tracker))
                else:
                    if not obj.simple:
                        # PLAYER MOVEMENT
                        if obj.move == "wasd":
                            if keyboard.is_pressed("w"):    self.move_up(obj)
                            if keyboard.is_pressed("e"):    obj.rotate_right()
                            if keyboard.is_pressed("a"):    self.move_left(obj)
                            if keyboard.is_pressed("s"):    self.move_down(obj)
                            if keyboard.is_pressed("d"):    self.move_right(obj)
                        elif obj.move == "dirs":
                            if keyboard.is_pressed("up arrow"): self.move_up(obj)
                            if keyboard.is_pressed("/"):        obj.rotate_right()
                            if keyboard.is_pressed("left arrow"):self.move_left(obj)
                            if keyboard.is_pressed("down arrow"):self.move_down(obj)
                            if keyboard.is_pressed("right arrow"):self.move_right(obj)
                        elif obj.move == "leftright":
                            if obj.face_right:
                                if self.can_move(obj,move_x=obj.xspeed):
                                    self.move_right(obj)
                                else:   obj.flip_sprite()
                            else:
                                if self.can_move(obj,move_x=-obj.xspeed):
                                    self.move_left(obj)
                                else:   obj.flip_sprite()
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
                        if obj.move in ["wasd","dirs"]:
                            if "x" in self.camera_follow:
                                if self.map.window[1] + W_WID - WGC_X < obj.origx:
                                    self.map.window[1] += obj.xspeed
                                elif self.map.window[1] + WGC_X > obj.origx:
                                    if self.map.window[1] > 0:
                                        self.map.window[1] -= obj.xspeed
                            if "y" in self.camera_follow:
                                if self.map.window[0] + W_HEI - WGC_Y < obj.origy:
                                    self.map.window[0] += obj.yspeed
                                elif self.map.window[0] + WGC_Y > obj.origy:
                                    if self.map.window[0] > 0:
                                        self.map.window[0] -= obj.yspeed

                        # GAME-ENDING CHECKS:
                        if obj.move in ["wasd","dirs"]:
                            if obj.hp <= 0 or obj.origy == self.map.width -1:
                                self.quit = True
                                obj.array = [['d','e','a','d']]
                            pass
                        else: # All non-player mobs, DEATH
                            if obj.hp <= 0:
                                obj.set_origin(0,0)
                                obj.array = [[' ']]
                                obj.move = None
                i+=1

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
    def move_down(self,obj):    
        self.move_obj(obj,0,obj.yspeed)

    def replace_chars(self,obj,new_char):
        """ Replaces the characters of an object on the
        INPUT_MAP with new_char.
        ISSUE: Not working properly."""
        new_obj = self.obj_from_char(new_char)
        assert new_obj.height() == 1, "New Object's gotta be short."
        if obj.height()%new_obj.height()==0 and obj.width()%new_obj.width()==0:
            for y in range(obj.height()):
                for x in range(obj.width()//new_obj.width()):
                    nx = obj.origx + (x * new_obj.width())
                    ny = obj.origy - obj.height() + 1 + y
                    if not self.map.is_xy(nx,ny,BLANK,"o"):
                        self.map.set_xy(nx,ny,new_char,"i")

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
        xs = obj.origx
        xf = xs+obj.width()
        ys = obj.origy - obj.height() + 1
        yf = ys+obj.height()
        try:
            if 'down' in enemy.dmg_dirs:
                if e_char in self.map.geom_map[ys-1][xs:xf]: #ABOVE
                    return True
            if 'up' in enemy.dmg_dirs:
                if e_char in self.map.geom_map[yf+1][xs:xf]: #BELOW
                    return True
            for y in range(ys,yf):
                if 'right' in enemy.dmg_dirs:
                    if self.map.geom_map[y][xs-1] == e_char: #LEFT
                        return True
                if 'left' in enemy.dmg_dirs:
                    if e_char in self.map.geom_map[y][xf] == e_char: #RIGHT
                        return True
        except:
            pass
        return False

    def teleport_obj(self,obj,y:int=0,x:int=0,char_left=BLANK):
        if self.map.is_xy(obj.origx,obj.origy,obj.char,"i"):
            # If char has not already been replaced
            self.map.set_xy(obj.origx,obj.origy,char_left,"i")
        obj.set_origin(x,y)
        self.map.set_xy(obj.origx,obj.origy,obj.char,"i")

    def move_obj(self,obj,move_x:int = 0,move_y:int = 0):
        """Moves a single object move_x and move_y amount OR LESS."""
        while move_x != 0 or move_y != 0:
            if self.can_move(obj,move_x,move_y):
                self.move_map_char(obj,move_x,move_y)
                move_x,move_y = 0,0
            else:
                if move_x != 0:
                    move_x += int((move_x*-1)/(abs(move_x)))
                if move_y != 0:
                    move_y += int((move_y*-1)/(abs(move_y)))
                # This brings move_x and move_y 1 closer to 0
                # Whether they're negative or positive
    
    def can_move(self, obj, move_x = 0, move_y = 0):
        """Check if there are any characters in the area that 
        the obj would take up. Takes literal change in x and y.
        Returns True if character can move in that diRECTion."""
        if obj.geom == "all":
            for y in range(move_y + obj.origy - obj.height() + 1, move_y + obj.origy + 1):
                for x in range(move_x + obj.origx,move_x + obj.origx + obj.width()):
                    try:
                        if self.map.geom_map[y][x] != BLANK:
                            if self.map.geom_map[y][x] != obj.char:
                                return False
                    except: return False
            return True
        elif obj.geom == "line":
            for x in range(move_x + obj.origx,move_x + obj.origx + obj.width()):
                try:
                    if self.map.geom_map[obj.origy+move_y][x] != BLANK:
                        if self.map.geom_map[obj.origy+move_y][x] != obj.char:
                            return False
                except: return False
            return True
        elif obj.geom == "complex":
            for y in range(move_y + obj.origy - obj.height() + 1, move_y + obj.origy + 1):
                for x in range(move_x + obj.origx,move_x + obj.origx + obj.width()):
                    try:
                        if self.map.geom_map[y-move_y][x-move_x] == obj.char:
                            if self.map.geom_map[y][x] != BLANK:
                                if self.map.geom_map[y][x] != obj.char:
                                    return False
                    except: return False
            return True

    def move_map_char(self,obj,move_x,move_y):
        """Similar to self.set_xy, only applies to objs.objs."""
        newx = obj.origx + move_x
        newy = obj.origy + move_y
        max = len(self.objs.objs)
        i = 0
        while i < max:
            currid = self.objs.objs[i].id
            if obj.id == currid:
                obj = self.objs.objs.pop(i)
                i = max
            else:
                i+= 1
        obj.set_origy(newy)
        obj.set_origx(newx)
        i = 0
        while i < max-1:
            if self.objs.objs[i].origx < newx or self.objs.objs[i].origy < newy:
                i+=1
            else:
                self.objs.objs.insert(i,obj)
                i = max

    def create_objs(self):
        """Initializes all objects, referring to objs.objs made
        by the user, cloning as needed."""
        old_len = len(self.objs.objs)
        for c in self.map.sparse_map:
            i = 0
            search = True
            while i < old_len and search:
                char = self.objs.objs[i].char
                if char == c[2]:
                    self.objs.copy(i,c[0],c[1])
                    search = False
                else:
                    i+=1
                
    def create_map(self):
        """This creates the output AND geometry
        maps out of all object sprites. NOT for initializing
        objects (not that you asked)."""
        self.map.clear_map(self.map.out_map)
        self.map.clear_map(self.map.geom_map)
        i = 0
        to_corner = False
        while i < len(self.objs.objs) and not to_corner:
            obj = self.objs.objs[i]
            if obj.origy < self.map.window[0] - (WGC_Y*2) or obj.origx < self.map.window[1] - (WGC_X*2):
                i+=1
            elif obj.origy > self.map.window[0] + W_HEI + (WGC_Y*2):
                to_corner = True
            else:
                if self.map.window[0] + W_HEI + (WGC_Y*2) > obj.origy:
                    # Print a sprite around its origin.
                    for y in range(obj.height()):
                        blanks_before = True
                        blanks_after = True
                        for x in range((obj.width()//2)+1):
                            char = obj.get_char(x,y)
                            # Don't put any blanks at the start or 
                            # end of a line of a sprite.
                            if char != BLANK or not blanks_before:
                                blanks_before = False
                                ypos = obj.origy + y - obj.height()
                                xpos = obj.origx + x
                                self.map.set_xy(xpos, ypos, char,"o")
                            char = obj.get_char(obj.width()-x,y)
                            if char != BLANK or not blanks_after:
                                blanks_after = False
                                ypos = obj.origy + y - obj.height()
                                xpos = obj.origx - x + obj.width()
                                self.map.set_xy(xpos, ypos, char,"o")

                        if obj.geom == "all":
                            for x in range(obj.width()):
                                self.map.set_xy(obj.origx+x, obj.origy-y, obj.char,"g")
                        elif obj.geom == "complex":
                            # Based on all characters of a sprite that are not blank.
                            for x in range(obj.width()):
                                if obj.array[y][x] != BLANK:
                                    self.map.set_xy(obj.origx+x, obj.origy-y, obj.char,"g")
                    if obj.geom == "line":
                        for x in range(obj.width()):
                            if obj.array[-1][x] != BLANK:
                                self.map.set_xy(obj.origx+x, obj.origy, obj.char,"g")
                i+=1
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
        self.width = 0
        self.height = 0
        self.sparse_map = [] # Made to store user-made map .
        self.out_map = [] # What the user will see.
        self.geom_map = [] # For checking collision.
        self.window = [0,0] # Y,X
        # These are the map coordinates of the 
        # top-left-most item shown in the window.

    def set_path(self,path=""):
        if len(path)>0:
            self.path = path
        self.store_map()
        self.clear_map(self.out_map)

    def clear_map(self,copy):
        """Create a blank map of size self.width by self.height."""
        if len(copy) == 0: # If the copy is new.
            for y in range(self.height):
                copy.append(list(BLANK * self.width))
        else:
            assert len(copy) == self.height, "Map must be the same height."
            assert len(copy[-1]) == self.width, "Map must be the same width."
            for y in range(self.height):
                copy[y] = (list(BLANK * self.width))

    def store_map(self):
        """ Stores characters and their coords in self.sparse_map,
        using a preset path. Also sets self.width and self.height. """
        self.path = DIRPATH + "\\" + self.path
        # Adds parent directory of running program
        y = 0
        maxwidth = 0
        with open(self.path,'r') as file:
            line = file.readline() # stores first line as string
            while line:
                line = line[:-1] # Remove newline calls.
                if len(line) > maxwidth:
                    maxwidth = len(line)
                for x in range(len(line)):
                    if line[x] != BLANK:
                        self.sparse_map.append([x,y,line[x]])
                y += 1
                line = file.readline()
        self.height = y - 1
        self.width = maxwidth
            
    def print_all(self):
        """Uses coordinate-based printing. Comparatively slow.
        Sprite-based printing is faster since it literally prints
        less. print_objs() is found in the Game class."""
        hei = self.window[0] + W_HEI
        wid = self.window[1] + W_WID
        print(CUR * (W_HEI+INFO_HEI))
        for row in range(self.window[0],hei):
        # UPDATE: Add check to see if it's any different from the new char
            try:[print(i,end="") for i in self.out_map[row][self.window[1]:wid]]
            except:print(BLANK,end='')
            print()
        print()

    def set_xy(self,x,y,char,map = "o",prev_char = None):
        """Sets char at a given position on map"""
        if x > -1 < y:
            try:
                if map == "o":
                    self.out_map[y][x] = char
                elif map == "g":
                    self.geom_map[y][x] = char
                elif map == "i":
                    stop = False
                    i = 0
                    length = len(self.objs.objs)
                    if char == BLANK: # Delete item from objs.objs
                        while i < length and not stop:
                            mx = self.objs.objs[i][1]
                            my = self.objs.objs[i][0]
                            mchar = self.objs.objs[i][2]
                            if my == y and mx == x and mchar == prev_char:
                                self.objs.objs.pop(i)
                                stop = True
                            elif my > y:
                                stop = True # You're trying to delete blankness.
                            else:
                                i+= 1
                    else:
                        while i < length and not stop:
                            if self.objs.objs[i][0] < y or self.objs.objs[i][1] < x:
                                i+=1
                            else:
                                self.objs.objs.insert(i,[y,x,char])
                                stop = True
                            
            except:
                pass # For going out of bounds.
    def is_xy(self,x,y,char,map = "o"):
        """Returns if a certain character is at this position."""
        return char in self.get_xy(x,y,map)
    def get_xy(self,x,y,map = "o"):
        """Returns what character is at this position."""
        try:
            if map == "o":
                return self.out_map[y][x]
            elif map == "g":
                return self.geom_map[y][x]
            elif map == "i":
                stop = False
                i = 0
                chars = []
                while i < len(self.objs.objs) and not stop:
                    if self.objs.objs[i][0] == y or self.objs.objs[i][1] == x:
                        chars.append(self.objs.objs[i][2])
                        i+=1
                    elif self.objs.objs[i][0] > y:
                        stop = True
                    else:
                        i+=1
                if len(chars) == 0:
                    return [BLANK] # Nothing is saved at the given coord.
                return chars
        except:
            return [BLANK] # For going out of bounds.

class Mission():
    def __init__(self,title="",type="",obj=None,duration=-1,reward=""):
        self.title = title
        self.type = type #location, item, score, survive, die
        # It can be any number of these as well.
        self.obj = obj # What will fulfil mission
        self.duration = duration
        self.reward = reward #teleport, item, score
        
class Objs():
    def __init__(self):
        self.path = ""
        self.objs = [] # Stores objects. Each includes a sprites key
        self.sprites = dict() # {img:array}
        self.max_id = 0

    def get_sprites(self,path):
        self.path = DIRPATH + "/" + path
        curr_img = None
        curr_array = []
        # Adds parent directory of running program
        with open(self.path, 'r',encoding='utf-8') as file:
            line = file.readline()[:-1] # Removes "\n".
            while(line):
                if line[0] == SIGN and line[-1] == SIGN:
                # Begins and ends with SIGN
                    if curr_img != None: # If this isn't the first img
                        self.sprites[curr_img] = curr_array
                        curr_array = []
                    curr_img = line[1:-1] # Remove SIGNs
                else:
                    curr_array.append(list(line))
                line = file.readline()[:-1] # Removes the \n

    def new(self,img, char, x=0,y=0, geom = "all",
    move = None, xspeed = 1, yspeed = 1, hp =1,face_right=True,
    face_down=False, grav_tick=0,dmg = 1, enemy_chars=[],
    dmg_dirs=[], set_rotate=0, animate=True):
        """Creates an Obj and appends it to the objs list."""
        obj = self.Obj(img, char, x,y, geom, move,xspeed,yspeed,
            hp,face_right,face_down,grav_tick,dmg,enemy_chars,dmg_dirs,
            animate)
        while obj.rotate != set_rotate:
            obj.rotate_right()
        obj.array = self.sprites[img]
        obj.id = self.max_id
        self.max_id+=1
        self.objs.append(obj)

    def copy(self,obji,newx,newy):
        """Makes a copy of an object from its objs index and appends
         that to the objs list."""
        o = self.objs[obji]
        self.new(o.img,o.char,newx,newy,o.geom,o.move,o.xspeed,o.yspeed,o.hp,
           o.face_right,o.face_down,o.grav_tick,o.dmg,o.enemy_chars,o.dmg_dirs,o.rotate,
           o.animate)
        return self.objs[-1]

    class Obj():
        """A Sprite is simply just an image."""
        def __init__(self,img, char, x=0,y=0, geom = "all",
        move = None, xspeed = 1,yspeed = 1,hp =1,face_right=True,
        face_down=False,grav_tick:int=0,dmg = 1,enemy_chars=[],dmg_dirs=[],
        animate=True):
            self.simple = False
            if move == None and grav_tick == 0:
                self.simple = True
            if not len(img): # If there is no img.
                self.img = [char]
            else:
                self.img = img
            self.origx = x
            self.origy = y
            self.top_y = 0
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
            self.animate = animate
            self.id = 0

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
        def set_origy(self,y):
            self.origy = y
            self.top_y = self.origy - self.height() + 1

        def get_origin(self):
            return [self.origx,self.origy]
    
        def get_char(self,x:int,y:int):
            """Returns the char stored here in a sprite array.
            Takes x,y, returns [y][x]"""
            try:    return self.array[y][x]
            except: return BLANK
            
        def width(self):
            return len(self.array[0])
        def height(self):
            return len(self.array)
        
        def flip_sprite(self):
            """Flips the sprite of an image vertically (left to right)"""
            self.face_right = not self.face_right
            if self.animate:
                for y in range(self.height()):
                    for x in range(self.width()//2+self.width()%2):
                        hold = self.array[y][x]
                        if hold in FLIP_CHARS.keys():
                            hold = FLIP_CHARS[hold]
                        self.array[y][x] = self.array[y][self.width()-x-1]
                        if self.array[y][x] in FLIP_CHARS.keys():
                            self.array[y][x] = FLIP_CHARS[self.array[y][x]]
                        self.array[y][self.width()-x-1] = hold

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