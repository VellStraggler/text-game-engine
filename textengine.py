from hashlib import new
import time, keyboard, os, random
import pygame

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

SPACES = ' ' * 50
S_LINE = ' ' * W_WID

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
        self.acts = Acts()
        self.speeches = []
        self.quit = False
        self.camera_follow = []
        self.folder = "" #Optional, shortens user code.

        pygame.mixer.init()
        self.themes = []
        self.sounds = dict()

        self.frames = 0
        self.tick = 0
        self.f_time = 0
        self.fpss = []
        self.start_time = 0
        self.waiting = 0
        self.game_delay = 0
        self.total = 0

        self.geom_set_dict =    {"all":self.geom_all,
                            "complex":self.geom_complex,
                            "line":self.geom_line,
                            "skeleton":self.geom_line}
        self.act_set_dict = {"switch_sprite":self.act_switch_sprite,
                            "quit":self.act_quit,
                            "sound":self.act_sound,
                            "unlock":self.act_unlock,
                            "switch_map":self.act_switch_map,
                            "kill":self.act_kill}   

    def run_game(self,debug=False):
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
        pygame.mixer.music.stop()
        self.play_sound("quit")
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
        self.move_all()
        self.create_map()
        self.map.print_all()
        self.run_fps()
    
    def wait(self):
        self.loop_time = time.time()
        while(self.waiting<self.game_delay):
            self.waiting = time.time() - self.loop_time
        self.waiting = 0
    def run_fps(self):
        self.frames += 1
        self.tick = (self.tick + 1)%MAX_TICK
        self.f_time = time.time()
        print("FPS:",1/(self.f_time-self.loop_time))
        self.fpss.append(self.f_time)

    def play_theme(self):
        if len(self.themes)>0:
            pygame.mixer.music.load(self.themes[0])
            pygame.mixer.music.play(-1)

    def add_theme(self,path:str):
        assert len(path) > 4, "Not a valid audio file name."
        self.themes.insert(0,self.folder + path)
    def add_sound(self, path:str,sound_name:str=""):
        assert len(path) > 4, "Not a valid audio file name."
        new_sound = pygame.mixer.Sound(self.folder + path)
        if len(sound_name)>0:
            self.sounds[sound_name] = new_sound
        else:
            path = path[:-4] # Remove ".wav".
            for s in ["/","\\"]:
                i = path.rfind(s)
                if i != -1: # Remove folder names and slashes.
                    path = path[i+1:]
            self.sounds[path] = new_sound
    def add_sounds_simple(self,sounds:list,dir_name:str=""):
        """Add a list of sounds to the game. They must be names only
        (no ".wav" or "folder/"), and should be the names of sounds keys
        that will be used automatically.
        Automatic sound names: jump, death, pain"""
        if len(dir_name) > 0:
            dir_name = dir_name + "/"
        for sound in sounds:
            sound = dir_name + sound + ".wav"
            self.add_sound(sound)
    def play_sound(self,key):
        if key in self.sounds.keys():
            self.sounds[key].play()

    def move_all(self):
        if keyboard.is_pressed("q"):
            self.quit = True
        if keyboard.is_pressed("p"):
            pygame.mixer.music.set_volume(.25)
            keyboard.wait("p")
            time.sleep(.5)
            pygame.mixer.music.set_volume(1)
        id_tracker = []
        i = 0
        to_corner = False
        while i < len(self.objs.objs) and not to_corner:
            obj = self.objs.objs[i]
            if obj.origy < self.map.window[0] - (WGC_Y*2):          i+=1
            elif obj.origx < self.map.window[1] - (WGC_X*2):        i+=1
            elif obj.origx > self.map.window[1] + W_WID + (WGC_X*2):i+=1
            elif obj.origy > self.map.window[0] + W_HEI + (WGC_Y*2):to_corner = True
            else:
                id_tracker.append(obj.id)
                if len(id_tracker) != len(set(id_tracker)):
                    id_tracker = list(set(id_tracker))
                elif not obj.simple:
                        if obj.move in ["wasd","dirs"]:
                            self.player_actions(obj)
                        elif obj.move == "leftright":
                            if obj.face_right:
                                if self.can_move(obj,move_x=obj.xspeed):
                                    self.move_right(obj)
                                else: obj.flip_sprite()
                            elif self.can_move(obj,move_x=-obj.xspeed):
                                self.move_left(obj)
                            else: obj.flip_sprite()
                                
                            if obj.hp <= 0: # All non-player mobs, DEATH.
                                self.kill_obj(obj,True)
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
                i+=1

    def player_actions(self,obj):
        # CAMERA-MOVING
        if "x" in self.camera_follow:
            if self.map.width > self.map.window[1] + W_WID < obj.origx + WGC_X:
                self.map.window[1] += obj.xspeed
            elif self.map.window[1] + WGC_X > obj.origx:
                if self.map.window[1] > 0:
                    self.map.window[1] -= obj.xspeed
        if "y" in self.camera_follow:
            if self.map.height > self.map.window[0] + W_HEI < obj.origy + WGC_Y :
                self.map.window[0] += obj.yspeed
            elif self.map.window[0] + WGC_Y > obj.origy:
                if self.map.window[0] > 0:
                    self.map.window[0] -= obj.yspeed
        # GAME-ENDING CHECKS:
        if obj.hp <= 0 or obj.origy == self.map.width -1:
            self.quit = True
            obj.array = [['d','e','a','d']]
        interact = False
        if obj.move == "wasd":
            if keyboard.is_pressed("w"):    self.move_up(obj)
            if keyboard.is_pressed("r"):    obj.rotate_right()
            if keyboard.is_pressed("a"):    self.move_left(obj)
            if keyboard.is_pressed("s"):    self.move_down(obj)
            if keyboard.is_pressed("d"):    self.move_right(obj)
            if keyboard.is_pressed("e"):    interact = True
        elif obj.move == "dirs":
            if keyboard.is_pressed("up arrow"): self.move_up(obj)
            if keyboard.is_pressed("/"):        obj.rotate_right()
            if keyboard.is_pressed("left arrow"):self.move_left(obj)
            if keyboard.is_pressed("down arrow"):self.move_down(obj)
            if keyboard.is_pressed("right arrow"):self.move_right(obj)
            if keyboard.is_pressed("."):    interact = True
        self.run_acts(obj,interact)


    def kill_obj(self,obj,sound:bool=False):
        if sound:
            self.play_sound("death")
        obj.set_origin(0,0)
        obj.array = [[' ']]
        obj.move = None

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
            self.play_sound("jump")
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

    def run_acts(self,obj,interact=False):
        """ Check all sides of an object for objects
        that can be interacted with."""
        xs = obj.origx
        xf = xs+obj.width()
        if obj.geom in ["all","complex"]:
            ys = obj.origy - obj.height() + 1
            yf = ys+obj.height()
        else:
            ys = obj.origy
            yf = ys+1
        # ISSUE: INTERACTIVE OBJECTS MUST HAVE GEOMETRY ON THEIR ORIGIN
        for act in self.acts.acts:
            if not act.locked:
                if interact:
                    if act.kind == "interact":
                        i_char = act.char
                        if obj.face_down:
                            if i_char in self.map.geom_map[yf+1][xs:xf]: #BELOW
                                pass
                        else:
                            if i_char in self.map.geom_map[ys-1][xs:xf]: #ABOVE
                                i=0
                                found = False
                                while self.objs.objs[i].id != obj.id and not found:
                                    i_obj = self.objs.objs[i]
                                    if i_char != i_obj.char:
                                        i+=1
                                    elif i_obj.origy != ys-1 or (i_obj.origx+i_obj.width()) < xs:
                                        i+=1
                                    else:
                                        found = True
                                self.act_set_dict[act.effect](i_obj,act.arg)
                        for y in range(ys,yf):
                            if obj.face_right:
                                if self.map.geom_map[y][xf] == i_char: #RIGHT
                                    pass
                            else:
                                if self.map.geom_map[y][xs-1] == i_char: #LEFT
                                    pass
                if act.kind == "location":
                    # ARG: LOCATION TO REACH, [X,Y] FORM
                    # To focus only on a certain x or y, set the other to -1.
                    if ys <= act.arg[1] < yf or act.arg[1] == -1:
                        if xs <= act.arg[0] < xf or act.arg[0] == -1:
                            self.act_set_dict[act.effect](obj,act.arg)

    # These functions are put into act_set_dict, for quicker lookup than if statements.
    def act_switch_sprite(self,obj,arg):
        # ARG: dictionary of old img key and new img value
        new_img = arg[obj.img]
        self.set_new_img(obj,new_img)
    def act_quit(self,obj,arg):
        self.quit = True
    def act_sound(self,obj,arg):
        # ARG: sound path
        self.add_sound(arg,arg)
        self.play_sound(arg)
    def act_unlock(self,obj,arg):
        # ARG: name of acts to unlock
        for targ_act in self.acts.acts:
            if targ_act.name == arg:
                targ_act.locked = False
    def act_switch_map(self,obj,arg):
        # ARG: name of new map
        self.end_game()
        self.map.set_path("mario/mario_test_.txt")
        self.init_map()
    def act_kill(self,obj,arg):
        # Make sure this is the last act of that object.
        self.kill_obj(obj)            

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
        except: pass
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
                if move_x != 0: move_x += int((move_x*-1)/(abs(move_x)))
                if move_y != 0: move_y += int((move_y*-1)/(abs(move_y)))
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
        elif obj.geom == "line" or obj.geom == "skeleton":
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
        obj.origy = newy
        obj.origx = newx
        i = 0
        while i < max-1:
            if self.objs.objs[i].origy < newy:
                i+=1
            elif self.objs.objs[i].origy == newy and self.objs.objs[i].origx < newx:
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
        while i > -1: # Get rid of unwanted copies.
            if self.objs.objs[i].get_origin() == [0,0]:
                self.objs.objs.pop(i)
            else:
                i-=1
    
    # These functions are put into geom_set_dict, for quicker lookup than if statements.
    def geom_all(self,obj):
        [[self.map.set_xy(x, y, obj.char,"g") 
        for x in range(obj.origx, obj.origx + obj.width())]
        for y in range(obj.origy - obj.height() +1,obj.origy +1)]
    def geom_complex(self,obj):
        # Based on all characters of a sprite that are not blank.
        [[self.map.set_xy(x + obj.origx, obj.origy - y, obj.char,"g") 
        for x in range(obj.width()) 
        if obj.array[y][x] != BLANK]
        for y in range(obj.height())]
    def geom_line(self,obj):
        [self.map.set_xy(x + obj.origx, obj.origy, obj.char,"g")
        for x in range(obj.width())
        if obj.array[-1][x] != BLANK]

    def create_map(self):
        """This creates the output AND geometry
        maps out of all object sprites. NOT for initializing
        objects (not that you asked)."""
        self.map.clear_map(self.map.rend_map)
        self.map.clear_map(self.map.geom_map)
        i = 0
        to_corner = False
        while i < len(self.objs.objs) and not to_corner:
            obj = self.objs.objs[i]
            #if obj.origy < self.map.window[0] - (WGC_Y*3) or obj.origx < self.map.window[1] - (WGC_X*3):
            #   i+=1
            if obj.origy > self.map.window[0] + W_HEI + (WGC_Y*3):
                to_corner = True
            else:
                i+=1
                # Print a sprite around its origin.
                if obj.geom == "skeleton":
                    for y in range(obj.height()):
                        for x in range(obj.width()):
                            char = obj.get_char(x,y)
                            # Don't print any blanks at all.
                            if char != BLANK:
                                ypos = obj.origy + y - obj.height()
                                xpos = obj.origx + x
                                self.map.set_xy(xpos, ypos, char,"o")
                else:
                    for y in range(obj.height()):
                        before = True
                        after = True
                        for x in range((obj.width()//2)+1):
                            char = obj.get_char(x,y)
                            # Don't put any blanks at the start or 
                            # end of a line of a sprite.
                            if char != BLANK or not before:
                                before = False
                                ypos = obj.origy + y - obj.height()
                                xpos = obj.origx + x
                                self.map.set_xy(xpos, ypos, char,"o")
                            char = obj.get_char(obj.width()-x,y)
                            if char != BLANK or not after:
                                after = False
                                ypos = obj.origy + y - obj.height()
                                xpos = obj.origx - x + obj.width()
                                self.map.set_xy(xpos, ypos, char,"o")
                self.geom_set_dict[obj.geom](obj)

class Map():
    """Three arrays are stored in a Map object: the wasd input 
    map, the output map, and a geom map.
    Set the map path upon initialization"""
    def __init__(self):
        self.geom_map = [] # For checking collision.
        self.height = 0
        self.overlay = [[BLANK for x in range(W_WID)] for y in range(W_HEI)]
            # Optional overlay of the game.
        self.use_overlay = False
        self.path = ""
        self.print_map = [S_LINE for i in range(W_HEI)]
            # Map of the final screen. 1D list of strings.
        self.rend_map = [] # Map of what will be rendered
        self.sparse_map = [] # Made to store user-made map .
        self.width = 0
        self.window = [0,0] # Y,X
            # These are the map coordinates of the 
        # These are the map coordinates of the 
            # These are the map coordinates of the 
        # top-left-most item shown in the window.

    def set_path(self,path):
        self.geom_map = [] # For checking collision.
        self.path = path
        self.rend_map = [] # What the user will see.
        self.sparse_map = [] # Made to store user-made map .
        self.store_map()
        self.clear_map(self.rend_map)

    def clear_map(self,copy):
        """Create a blank map of size self.width by self.height."""
        if len(copy) == 0: # If the copy is new.
            for y in range(self.height):
                copy.append(list(BLANK * self.width))
        else:
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
        """ Appends the proper area of self.rend_map to self.print_map,
        and prints print_map to game window."""
        hei = self.window[0] + W_HEI
        wid = self.window[1] + W_WID
        print(CUR * (W_HEI+INFO_HEI)) #"\033[1;35;100m"
        for row in range(W_HEI):
            self.print_map[row] = "".join(self.rend_map[row+self.window[0]][self.window[1]:wid])
            # UPDATE: OVERLAY WOULD GO HERE.
        [print(self.print_map[i]) for i in range(W_HEI)]
        print()

    def set_xy(self,x,y,char,map = "o",prev_char = None):
        """Sets char at a given position on map"""
        if x > -1 < y:
            try:
                if map == "o":
                    self.rend_map[y][x] = char
                elif map == "g":
                    self.geom_map[y][x] = char
                else: #"i"
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
                return self.rend_map[y][x]
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
class Acts():
    def __init__(self):
        self.acts = []
    def new(self,name="default",kind="interact",
    char="",effect="",arg="",locked = False):
        new_act = self.Act(name,kind,char,effect,arg,locked)
        self.acts.append(new_act)
    def append(self,act):
        self.acts.append(act)

    class Act():
        def __init__(self,name="default",kind="interact",
        char="",effect="",arg="",locked=False):
            self.char = char # What you must be near to fulfil the act.                
            self.arg = arg # could be the new skin, the score added,
            self.effect = effect #teleport, item, score, change skin
            self.kind = kind # location, item, score, survive, die, interact
            self.locked = locked
            self.name = name
        
class Objs():
    def __init__(self):
        self.inventory = []
        self.max_id = 0
        self.objs = [] # Stores objects. Each includes a sprites key
        self.path = ""
        self.sprites = dict() # {img:array}
        self.texts = []
        self.max_height= 0 
        self.max_width = 0

    def get_sprites(self,path):
        self.path = DIRPATH + "/" + path
        c_img = None
        c_array = []
        height = 0
        # Adds parent directory of running program
        with open(self.path, 'r',encoding='utf-8') as file:
            line = file.readline()[:-1] # Removes "\n".
            while(line):
                if line[0] == SIGN and line[-1] == SIGN:
                # Begins and ends with SIGN
                    if c_img != None: # If this isn't the first img
                        if len(c_array[0]) > self.max_width:
                            self.max_width = len(c_array[0])
                        if height > self.max_height:
                            self.max_height = height
                        self.sprites[c_img] = c_array
                        c_array = []
                    c_img = line[1:-1] # Remove SIGNs
                    height = 0
                else:
                    c_array.append(list(line))
                    height +=1
                line = file.readline()[:-1] # Removes the \n

    def get_texts(self,path):
        path = DIRPATH + "/" + path
        with open(path, 'r',encoding='utf-8') as file:
            line = file.readline()[:-1]
            while(line):
                self.texts.append(line)
                line = file.readline()[:-1]
    
    def append_objs(self,objs:list=[]):
        """Add a list of objects to self.objs."""
        for obj in objs:
            self.append_obj(obj)
            
    def append_obj(self,obj,rotate=0):
        while rotate != obj.rotate:
            obj.rotate_right()
        obj.array = self.sprites[obj.img]
        obj.id = self.max_id
        self.max_id+=1
        obj.i = len(self.objs)
        self.objs.append(obj)

    def new(self,img, char, x=0,y=0, geom = "all",
    move = None, xspeed = 1, yspeed = 1, hp =1,face_right=True,
    face_down=False, grav_tick=0,dmg = 1, enemy_chars=[],
    dmg_dirs=[], set_rotate=0, animate=True,txt="",txt_line=-1):
        """Creates an Obj and appends it to the objs list."""
        if txt_line > -1:
            txt = self.texts[txt_line]
        obj = self.Obj(img, char, x,y, geom, move,xspeed,yspeed,
            hp,face_right,face_down,grav_tick,dmg,enemy_chars,dmg_dirs,
            animate,txt)
        self.append_obj(obj,set_rotate)

    def copy(self,obji,newx,newy):
        """Makes a copy of an object from its objs index and appends
         that to the objs list."""
        o = self.objs[obji]
        self.new(o.img,o.char,newx,newy,o.geom,o.move,o.xspeed,o.yspeed,o.hp,
           o.face_right,o.face_down,o.grav_tick,o.dmg,o.enemy_chars,o.dmg_dirs,o.rotate,
           o.animate,o.txt)
        return self.objs[-1]

    class Obj():
        def __init__(self,img, char, x=0,y=0, geom = "all",
        move = None, xspeed = 1,yspeed = 1,hp =1,face_right=True,
        face_down=False,grav_tick:int=0,dmg = 1,enemy_chars=[],dmg_dirs=[],
        animate=True,txt=""):
            self.img = img
            self.origx = x
            self.origy = y
            self.geom = geom # Options of: None, line, complex, skeleton, or all.
            self.move = move # None, random, leftright, updown, wasd, dirs.
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
            
            self.txt = txt
            self.face_right = face_right # Left: False, Right: True
            self.face_down = face_down # Up: False, Down: True
            self.array = [] # Must be set through Objs function new().
            self.rotate = 0 # 0 through 3
            self.score = 0
            self.simple = False
            if move == None and grav_tick == 0:
                self.simple = True

        def set_origin(self,x,y):
            self.origx = x
            self.origy = y

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