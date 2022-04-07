import random
from keyboard import is_pressed,wait
from os.path import dirname
from pygame import mixer
from time import time,sleep
import numpy

DIRPATH = dirname(__file__)
# Required to run program in Python3 terminal.
BLANK = ' '
SIGN = '$'
CLEAR = "\033[2J"
CUR = '\033[A\033[F'
ZER = '\033[H'
RIT = '\033[1C'
MAX_TICK = 16
# Default animation dictionary for a given object.

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
        self.map_list = [Map()]
        self.map_index = 0
        self.curr_map = self.map_list[self.map_index]
        # A pointer to the current map being played.
        self.objs = Objs()
        self.acts = Acts()
        self.speeches = []
        self.quit = False
        self.camera_follow = []
        self.folder = "" #Optional, shortens user code.

        mixer.init()
        self.themes = []
        self.sounds = dict()

        self.frames = 0
        self.tick = 0
        self.f_time = 0
        self.fpss = []
        self.start_time = 0
        self.waiting = 0
        self.game_speed = 1 # General actions can be called at 1/second.
        self.total = 0

        self.geom_set_dict= {"all":self.geom_all,
                            "complex":self.geom_complex,
                            "line":self.geom_line,
                            "skeleton":self.geom_line,
                            None:self.geom_none}
        self.act_set_dict = {"switch_sprite":self.act_switch_sprite,
                            "rotate":self.act_rotate,
                            "quit":self.act_quit,
                            "sound":self.act_sound,
                            "unlock":self.act_unlock,
                            "switch_map":self.act_switch_map,
                            "switch_theme":self.act_switch_theme,
                            "kill":self.act_kill}   
        self.key_dict = {"wasd":
                            {"w":self.move_up,"a":self.move_left,
                            "s":self.move_down,"d":self.move_right,
                            "e":self.run_interacts},
                        "dirs":
                            {"up arrow":self.move_up,"left arrow":self.move_left,
                            "down arrow":self.move_down,"right arrow":self.move_right,
                            ".":self.run_interacts}}

    def run_game(self):
        """Combine the map and the objs and begin the main game loop."""
        self.init_map()
        while(not self.quit):
            self.game_loop()
        self.end_game()

    def switch_map(self,index):
        if self.map_index >= len(self.map_list):
            self.map_index = 0
        self.map_index = index
        self.curr_map = self.map_list[self.map_index]
        # Reset Objects.
        self.objs.objs = list()
        for obj in self.objs.usr_objs:
            obj.origx = 0
            obj.origy = 0
            self.objs.objs.append(obj)
    
    def next_map(self):
        self.switch_map(self.map_index + 1)

    def init_map(self,first=True):
        """All that comes before the main game_loop"""
        if first:
            print(CLEAR)
            self.start_time = time()
            self.play_theme()
        self.init_objs()
        self.create_map()

    def end_game(self):
        """All the comes after the main game_loop"""
        mixer.music.stop()
        self.play_sound("quit")
        self.total = self.frames/(time()-self.start_time)
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
        self.frame_start = time()
        self.move_all()
        self.create_map()
        self.curr_map.print_all()
        self.run_fps()
    
    def run_fps(self):
        self.frames += 1
        self.tick = (self.tick + 1)%MAX_TICK
        self.f_time = time()
        print("FPS:",1/(self.f_time-self.frame_start))
        self.fpss.append(self.f_time)

    def play_theme(self):
        if len(self.themes)>0:
            mixer.music.load(self.themes[0])
            mixer.music.play(-1)
    def add_theme(self,path:str):
        assert len(path) > 4, "Not a valid audio file name."
        self.themes.insert(0,self.folder + path)
    def add_sound(self, path:str,sound_name:str=""):
        assert len(path) > 4, "Not a valid audio file name."
        new_sound = mixer.Sound(self.folder + path)
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
        if is_pressed("q"):
            self.quit = True
        if is_pressed("p"):
            mixer.music.set_volume(.25)
            wait("p")
            sleep(.5)
            mixer.music.set_volume(1)
        id_tracker = []
        for obj in self.objs.objs:
            if obj.origy > self.curr_map.window[0] + W_HEI + (WGC_Y*2):break
            else:
                id_tracker.append(obj.id)
                if len(id_tracker) != len(set(id_tracker)):
                    id_tracker = list(set(id_tracker))
                elif not obj.simple:
                    if obj.move in ["wasd","dirs"]:
                        self.player_actions(obj)
                    elif obj.move == "leftright":
                        if obj.face_right:
                            if self.can_move(obj,1):
                                self.move_right(obj)
                            else: self.objs.flip_sprite(obj)
                        else:
                            if self.can_move(obj,-1):
                                self.move_left(obj)
                            else: self.objs.flip_sprite(obj)
                        if obj.hp <= 0: # All non-player mobs, DEATH.
                            self.kill_obj(obj,True)
                            
                    # ALL THAT SHOULD FALL WILL FALL
                    if obj.grav:
                        if time() - obj.move_time["w"] > 3/obj.yspeed:
                            obj.jump =0
                            # If they haven't moved up in awhile
                        if time() - obj.move_time["g"] > 1/obj.yspeed:
                            if obj.jump > 0:
                                obj.jump -= 1
                            obj.move_time["g"] = time()
                            if obj.jump == 0:
                                self.move_obj(obj,0,1)
                    # DAMAGE-TAKING
                    for e_char in obj.enemy_chars:
                        self.take_dmg(obj,e_char)

    def player_actions(self,obj):
        # PLAYER MOVEMENT:
        if obj.move in self.key_dict.keys(): # "wasd" or "dirs"
            for key in self.key_dict[obj.move].keys():
                if is_pressed(key):
                    self.key_dict[obj.move][key](obj)
        self.run_acts(obj)
        # CAMERA MOVING:
        if "x" in self.camera_follow:
            if self.curr_map.width > self.curr_map.window[1] + W_WID < obj.origx + WGC_X:
                self.curr_map.window[1] += 1
            elif self.curr_map.window[1] + WGC_X > obj.origx - obj.width():
                if self.curr_map.window[1] > 0:
                    self.curr_map.window[1] -= 1
        if "y" in self.camera_follow:
            if self.curr_map.height > self.curr_map.window[0] + W_HEI < obj.origy + WGC_Y :
                self.curr_map.window[0] += 1
            elif self.curr_map.window[0] + WGC_Y > obj.origy:
                if self.curr_map.window[0] > 0:
                    self.curr_map.window[0] -= 1
        # GAME-ENDING CHECKS:
        if obj.hp <= 0 or obj.origy == self.curr_map.width -1:
            self.quit = True
            obj.array = [['d','e','a','d']]

    def kill_obj(self,obj,sound:bool=False):
        if sound:
            self.play_sound("death")
        obj.set_origin(0,0)
        obj.live = False
        obj.array = [[' ']]
        obj.move = None

    # Synonymous functions
    def move_left(self,obj):
        if time() - obj.move_time["a"] > 1/obj.xspeed:
            obj.move_time["a"] = time()
            obj.img = obj.animate["a"]
            obj.array = self.objs.sprites[obj.img]
            self.move_obj(obj,-1)
    def move_right(self,obj):
        if time() - obj.move_time["d"] > 1/obj.xspeed:
            obj.move_time["d"] = time()
            obj.img = obj.animate["d"]
            obj.array = self.objs.sprites[obj.img]
            self.move_obj(obj,1)
    def move_down(self,obj):
        if time() - obj.move_time["s"] > 1/obj.yspeed:
            obj.move_time["s"] = time()
            obj.img = obj.animate["s"]
            obj.array = self.objs.sprites[obj.img]
            if obj.grav:
                obj.jump = 0
            self.move_obj(obj,0,1)
    def move_up(self,obj):
        if time() - obj.move_time["w"] > 1/obj.yspeed:
            obj.move_time["w"] = time()
            obj.img = obj.animate["w"]
            obj.array = self.objs.sprites[obj.img] 
            if not obj.grav:
                self.move_obj(obj,0,-1)
            elif not self.can_move(obj,0,1): # If on top of something.
                obj.jump = obj.max_jump
                self.move_obj(obj,0,-1)
                self.play_sound("jump")
            elif obj.jump > 0:
                self.move_obj(obj,0,-1)

    def set_new_img(self,obj,new_img):
        obj.img = new_img
        obj.array = self.objs.sprites[obj.img]
        obj.rotate = 0

    def obj_from_char(self,char):
        for obj in self.objs.objs:
            if obj.char == char:
                return obj

    def run_interacts(self,obj):
        if time() - obj.move_time["i"] > 1/self.game_speed:
            obj.move_time["i"] = time()
            xs,xf,ys,yf = self.set_xy_limits(obj)
            for act in self.acts.acts:
                if not act.locked:
                    if act.kind == "interact":
                        i_char = act.char
                        if obj.char == i_char:
                            self.act_set_dict[act.effect](obj,act.arg)
                        else:
                            if obj.face_down:
                                if i_char in self.curr_map.geom_map[yf+1][xs:xf]: #BELOW
                                    pass
                            else:
                                if i_char in self.curr_map.geom_map[ys-1][xs:xf]: #ABOVE
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
                                    if self.curr_map.geom_map[y][xf] == i_char: #RIGHT
                                        pass
                                else:
                                    if self.curr_map.geom_map[y][xs-1] == i_char: #LEFT
                                        pass

    def set_xy_limits(self,obj):
        """Used in run_acts and run_interacts"""
        xs = obj.origx
        xf = xs+obj.width()
        if obj.geom in ["all","complex"]:
            ys = obj.origy - obj.height() + 1
            yf = ys+obj.height()
        else:
            ys = obj.origy
            yf = ys+1
        return xs,xf,ys,yf

    def run_acts(self,obj):
        """ Check all sides of an object for objects
        that can be interacted with."""
        xs,xf,ys,yf = self.set_xy_limits(obj)
        # ISSUE: INTERACTIVE OBJECTS MUST HAVE GEOMETRY ON THEIR ORIGIN
        for act in self.acts.acts:
            if not act.locked: 
                if act.kind == "location":
                    # ARG: LOCATION TO REACH, [X,Y] FORM
                    # To focus only on a certain x or y, set the other to -1.
                    if ys <= act.arg[1] < yf or act.arg[1] == -1:
                        if xs <= act.arg[0] < xf or act.arg[0] == -1:
                            self.act_set_dict[act.effect](obj,act.arg)
                            # Call the proper function from the act_set dictionary
                elif act.kind == "touch":
                    bubble = set()
                    for char in self.curr_map.geom_map[yf+1][xs:xf]:
                        bubble.add(char)
                    for char in self.curr_map.geom_map[ys-1][xs:xf]:
                        bubble.add(char)
                    for y in range(ys,yf):
                        bubble.add(self.curr_map.geom_map[y][xs-1])
                        bubble.add(self.curr_map.geom_map[y][xf])
                    if act.arg[0] in bubble:
                        self.act_set_dict[act.effect](obj,act.arg)

    # These functions are put into act_set_dict, for quicker lookup than if statements.
    def act_switch_sprite(self,obj,arg):
        # ARG: dictionary of old img key and new img value
        new_img = arg[obj.img]
        self.set_new_img(obj,new_img)
    def act_switch_theme(self,obj,arg):
        mixer.music.stop()
        self.add_theme(arg[-1])
        self.play_theme()
    def act_rotate(self,obj,arg):
        obj.rotate_right()
        self.objs.sprites[obj.img] = obj.array
        obj.animate = {"w":obj.img,"a":obj.img,"s":obj.img,"d":obj.img}
    def act_quit(self,obj,arg):
        self.quit = True
    def act_sound(self,obj,arg):
        # ARG: sound path
        if type(arg) == type(list()):
            arg = arg[-1]
        self.add_sound(arg,arg)
        self.play_sound(arg)
    def act_unlock(self,obj,arg):
        # ARG: name of acts to unlock
        for targ_act in self.acts.acts:
            if targ_act.name == arg:
                targ_act.locked = False
    def act_switch_map(self,obj,arg:list):
        # The last item in ARG is the file_name
        # Find the map in map_list, or create it
        file_name = arg[-1]
        index = 0
        map_not_found = True
        while map_not_found and index < len(self.map_list):
            map = self.map_list[index]
            if map.file_name == file_name:
                self.curr_map = map
                map_not_found = False
            else:
                index += 1
        if map_not_found:
        # Create new map, initialize it, and add it to the map list.
            map = Map()
            map.set_path(file_name)
            self.map_list.append(map)
            index = len(self.map_list) - 1
        self.curr_map = map
        self.switch_map(index)
        self.init_map(False)
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
                if e_char in self.curr_map.geom_map[ys-1][xs:xf]: #ABOVE
                    return True
            if 'up' in enemy.dmg_dirs:
                if e_char in self.curr_map.geom_map[yf+1][xs:xf]: #BELOW
                    return True
            for y in range(ys,yf):
                if 'right' in enemy.dmg_dirs:
                    if self.curr_map.geom_map[y][xs-1] == e_char: #LEFT
                        return True
                if 'left' in enemy.dmg_dirs:
                    if e_char in self.curr_map.geom_map[y][xf] == e_char: #RIGHT
                        return True
        except: pass
        return False

    def teleport_obj(self,obj,x:int=0,y:int=0):
        """Moves an object to a given location. Does not check to see if anything
        is in the way."""
        move_x = obj.origx - x
        move_y = obj.origy - y
        if x > obj.origx:
            move_x *= -1
        if y < obj.origy:
            move_y *= -1
        self.move_map_char(obj,move_x,move_y)

    def move_obj(self,obj,move_x = 0,move_y = 0):
        """Moves a single object move_x and move_y amount OR LESS."""
        assert move_x in [-1,0,1] and move_y in [-1,0,1], "ONLY 1s and 0s accepted here."
        assert move_x == 0 or move_y == 0, "You can only move along one axis at a time."
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
        ys,yf = move_y + obj.origy - obj.height() + 1, move_y + obj.origy + 1
        xs,xf = move_x + obj.origx,move_x + obj.origx + obj.width()
        if move_x > 0:
            xs = obj.origx + obj.width()
        elif move_x < 0:
            xf = obj.origx
        if move_y > 0:
            ys = obj.origy + 1
        elif move_y < 0:
            yf = obj.origy - obj.height() + 1
        if obj.geom == "all":
            for y in range(ys,yf):
                for x in range(xs,xf):
                    try:
                        if self.curr_map.geom_map[y][x] != BLANK:
                            return False
                    except: return False
        elif obj.geom == "line" or obj.geom == "skeleton":
            for x in range(xs,xf):
                try:
                    if self.curr_map.geom_map[obj.origy+move_y][x] != BLANK:
                        return False
                except: return False
        elif obj.geom == "complex":
            for y in range(ys,yf):
                for x in range(xs,xf):
                    try:
                        if self.curr_map.geom_map[y][x] != BLANK:
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

    def add_to_sparse(self,x,y,char):
        obj = self.objs.copy(self.obj_from_char(char),x,y)
        i = 0
        max = len(self.objs.objs)
        while i < max-1:
            if self.objs.objs[i].origy < y:
                i+=1
            elif self.objs.objs[i].origy == y and self.objs.objs[i].origx < x:
                i+=1
            else:
                self.objs.objs.insert(i,obj)
                i = max
        self.curr_map.sparse_map.insert(0,[x,y,char])

    def init_objs(self):
        """Initializes all objects, referring to objs.objs made
        by the user, cloning as needed."""
        old_len = len(self.objs.objs)
        for c in self.curr_map.sparse_map:
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
        [[self.curr_map.set_xy_geom(x, y, obj.char) 
        for x in range(obj.origx, obj.origx + obj.width())]
        for y in range(obj.origy - obj.height() +1,obj.origy +1)]
    def geom_complex(self,obj):
        # Based on all characters of a sprite that are not blank.
        [[self.curr_map.set_xy_geom(x + obj.origx, obj.origy - y, obj.char) 
        for x in range(obj.width()) 
        if obj.array[y][x] != BLANK]
        for y in range(obj.height())]
    def geom_line(self,obj):
        [self.curr_map.set_xy_geom(x + obj.origx, obj.origy, obj.char)
        for x in range(obj.width())
        if obj.array[-1][x] != BLANK]
    def geom_none(self,obj):
        pass

    def create_map(self):
        """This creates the output AND geometry
        maps out of all object sprites. NOT for initializing
        objects (not that you asked)."""
        self.curr_map.empty_map(self.curr_map.rend_map)
        self.curr_map.empty_map(self.curr_map.geom_map)
        for obj in self.objs.objs:
            if obj.origy > self.curr_map.window[0] + W_HEI + (WGC_Y*3):
                break
            else:
                # Print a sprite around its origin.
                if obj.geom == "skeleton":
                    for y in range(obj.height()):
                        for x in range(obj.width()):
                            char = obj.get_char(x,y)
                            # Don't print any blanks at all.
                            if char != BLANK:
                                ypos = obj.origy + y - obj.height()
                                xpos = obj.origx + x
                                self.curr_map.set_xy_rend(xpos, ypos, char)
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
                                self.curr_map.set_xy_rend(xpos, ypos, char)
                            char = obj.get_char(obj.width()-x,y)
                            if char != BLANK or not after:
                                after = False
                                ypos = obj.origy + y - obj.height()
                                xpos = obj.origx - x + obj.width()
                                self.curr_map.set_xy_rend(xpos, ypos, char)
                # Add any text above the object sprite
                if obj.txt > -1:
                    txt = self.objs.texts[obj.txt]
                    out_y = obj.origy - obj.height() - 2
                    out_x = obj.origx + (obj.width())//2 - len(txt)//2
                    [self.curr_map.set_xy_rend(out_x+i,out_y,txt[i]) for i in range(len(txt))]
                self.geom_set_dict[obj.geom](obj)
        
class Map():
    """Three arrays are stored in a Map object: the wasd input 
    map, the output map, and a geom map.
    Set the map path upon initialization"""
    def __init__(self):
        self.geom_map = [] # For checking collision.
        self.height = W_HEI
        self.width = W_WID
        self.overlay = [[BLANK for x in range(W_WID)] for y in range(W_HEI)]
            # Optional overlay of the game.
        self.use_overlay = False
        self.print_map = [S_LINE for i in range(W_HEI)]
            # Map of the final screen. 1D list of strings.
        self.rend_map = [] # Map of what will be rendered
        self.sparse_map = [] # Made to store user-made map.
        self.window = [0,0] # Y,X
            # These are the map coordinates of the 
            # top-left-most item shown in the window.
        self.file_name = ""

    def set_path(self,path):
        self.store_map(self.sparse_map,path)
        self.empty_map(self.rend_map)

    def set_overlay(self,path):
        self.use_overlay = True
        self.store_map(self.overlay,path)

    def empty_map(self,map):
        """ Create a blank map of size self.width by self.height.
        Should not be used on sparse_map"""
        if len(map) == 0: # If the map is new.
            for y in range(self.height):
                map.append(list(BLANK * self.width))
        else:
            for y in range(self.height):
                map[y] = (list(BLANK * self.width))
        return map

    def store_map(self,sparse_map,path):
        """ Stores characters and their coords in self.sparse_map,
        using a preset path. Also sets self.width and self.height. """
        path = DIRPATH + "\\" + path
        if ".txt" not in path:
            path += ".txt"
        # Adds parent directory of running program
        self.file_name = path
        y = 0
        maxwidth = 0
        with open(path,'r') as file:
            line = file.readline() # stores first line as string
            while line:
                line = line[:-1] # Remove newline calls.
                if len(line) > maxwidth:
                    maxwidth = len(line)
                for x in range(len(line)):
                    if line[x] != BLANK:
                        sparse_map.append([x,y,line[x]])
                y += 1
                line = file.readline()
        if sparse_map == self.sparse_map:
            self.height = y
            self.width = maxwidth

    def print_all(self):
        """ Appends the proper area of self.rend_map to self.print_map,
        and prints print_map to game window."""
        wid = self.window[1] + W_WID
        print(CUR * (W_HEI+INFO_HEI)) #"\033[1;35;100m"
        cushion = " " * 25
        for row in range(W_HEI):
            self.print_map[row] = "".join(self.rend_map[row+self.window[0]][self.window[1]:wid])
            # UPDATE: OVERLAY WOULD GO HERE.
        [print(cushion,self.print_map[i]) for i in range(W_HEI)]
        print()

    def set_xy_geom(self,x,y,char):
        """Sets char at a given position on map"""
        if x > -1 < y and x < self.width and y < self.height:
            self.geom_map[y][x] = char
    def get_xy_geom(self,x,y):
        """Returns what character is at this position."""
        if x > -1 < y and x < self.width and y < self.height:
            return self.geom_map[y][x]
    def set_xy_rend(self,x,y,char):
        """Sets char at a given position on map"""
        if x > -1 < y and x < self.width and y < self.height:
            self.rend_map[y][x] = char
    def get_xy_rend(self,x,y):
        if x > -1 < y and x < self.width and y < self.height:
            return self.rend_map[y][x]

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
        self.objs = [] # Stores objects. Each includes a sprites key
        self.usr_objs = [] # These are all the original objects.
        self.sprites = {"dead":[[" "]]}
        self.texts = []
        self.max_height= 0 
        self.max_width = 0
        self.max_id = 0

    def get_sprites(self,path):
        """Takes the sprite file path and stores the sprites in
        the sprites dictionary."""
        path = DIRPATH + "/" + path
        c_img = None
        c_array = []
        height = 0
        # Adds parent directory of running program
        with open(path, 'r',encoding='utf-8') as file:
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

    def flip_sprite(self,obj):
        assert obj.animate not in [None,"flip"], "This object is not animated."
        obj.face_right = not obj.face_right
        if obj.face_right:
            obj.img = obj.animate["d"]
            obj.array = self.sprites[obj.img]

    def get_flipped_sprite(self,array):
        """ Returns a vertically mirrored
        2D array of the given array"""
        new_array = []
        for y in range(len(array)):
            line = []
            for x in range(len(array[0])):
                char = array[y][len(array[0])-x-1]
                if char in FLIP_CHARS.keys():
                    char = FLIP_CHARS[char]
                line.append(char)
            new_array.append(line)
        return new_array
    
    def append_objs(self,objs:list=[]):
        """Add a list of objects to self.objs."""
        for obj in objs:
            self.append_obj(obj)
            
    def append_obj(self,obj,rotate=0):
        """Important object initialization happens here."""
        while rotate != obj.rotate:
            obj.rotate_right()
        obj.array = self.sprites[obj.img]
        if obj.animate == "flip":
            original = obj.img
            flip_img = str(reversed(obj.img))
            self.sprites[flip_img] = self.get_flipped_sprite(obj.array)
            obj.animate = {"w":obj.img,"a":flip_img,"s":obj.img,"d":original}
        elif obj.animate == None:
            obj.animate = {"w":obj.img,"a":obj.img,"s":obj.img,"d":obj.img}
        elif obj.animate == "sneaky":
            # This takes the object sprite and assumes it to be facing right
            # and to be the reverse of facing left.
            # It looks for the object image with "-w" and "-s" added at the end
            assert (obj.img + "-w") in self.sprites.keys(), "img_name-w required."
            assert (obj.img + "-s") in self.sprites.keys(), "img_name-s required."
            facing_up = obj.img + "-w"
            facing_down = obj.img + "-s"
            facing_left = obj.img + "-a"
            self.sprites[facing_left] = self.get_flipped_sprite(obj.array)
            obj.animate = {"w":facing_up,"a":facing_left,"s":facing_down,"d":obj.img}
        obj.id = self.max_id
        self.max_id+=1
        obj.i = len(self.objs)
        self.objs.append(obj)
        self.usr_objs.append(obj)

    def new(self,img, char, x=0,y=0, geom = "all",
    move = None, xspeed = 1, yspeed = 1, hp =1,face_right=True,
    face_down=False, grav=False,dmg = 1, enemy_chars=[],
    dmg_dirs=[], set_rotate=0, animate=None,txt=-1,max_jump=1,data=dict()):
        """Creates an Obj and appends it to the objs list."""
        obj = self.Obj(img, char, x,y, geom, move,xspeed,yspeed,
            hp,face_right,face_down,grav,dmg,enemy_chars,dmg_dirs,
            animate,txt,max_jump,data)
        self.append_obj(obj,set_rotate)

    def copy(self,obji,newx,newy):
        """Makes a copy of an object from its objs index and appends
         that to the objs list."""
        if type(obji) == type(int()):
            o = self.objs[obji]
        else: # An object was given, not an index
            o = obji
        self.new(o.img,o.char,newx,newy,o.geom,o.move,o.xspeed,o.yspeed,o.hp,
           o.face_right,o.face_down,o.grav,o.dmg,o.enemy_chars,o.dmg_dirs,o.rotate,
           o.animate,o.txt,o.max_jump,o.data)
        return self.objs[-1]

    class Obj():
        def __init__(self,img, char, x=0,y=0, geom = "all",
        move = None, xspeed = 1,yspeed = 1,hp =1,face_right=True,
        face_down=False,grav:bool=False,dmg = 1,enemy_chars=[],dmg_dirs=[],
        animate=None,txt:int=-1,max_jump=1,data=dict()):
            self.simple = False
            self.move = move # None, leftright, wasd, dirs.
            self.grav = grav
            if move == None and not grav:
                self.simple = True
            self.xspeed = xspeed
            self.yspeed = yspeed
            if not self.simple:
                self.move_time = {"w":0,"a":0,"s":0,"d":0,"i":0,"g":0}
                #wasd: controls, i:interact, g:gravity (falling)

            self.img = img
            self.geom = geom # Options of: None, line, complex, skeleton, or all.
            self.origx = x
            self.origy = y
            self.char = char
            self.hp = hp
            self.max_jump = max_jump
            self.jump = 0 # based on yspeed
            self.dmg = dmg
            self.enemy_chars = enemy_chars
            self.dmg_dirs = dmg_dirs
            self.animate = animate # Edited in the objs.append_obj function
            # "flip" is default, mirrors the image for every change between right and left.
            # Otherwise, if it's not None it becomes a dictionary: {w,a,s,d:sprite images.}

            self.id = 0
            
            self.txt = txt # line number from textsheet
            self.face_right = face_right # Left: False, Right: True
            self.face_down = face_down # Up: False, Down: True
            self.array = [] # Must be set through Objs function new().
            self.rotate = 0 # 0 through 3
            self.score = 0
            self.live = True
            self.data = data

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
        
        def flip_sprite_old(self):
            """Flips the sprite of an image vertically (left to right)"""
            self.face_right = not self.face_right
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