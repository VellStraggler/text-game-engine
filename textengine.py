from keyboard import is_pressed,wait
from pygame import mixer
import numpy as np
from os.path import dirname
import random
from time import time,sleep
from math import log

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
RETURN = CUR * (W_HEI+INFO_HEI)
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

ccode = "\033[0;39;"
COLORS = {"default":ccode+"49m","white":ccode+"47m",
        "cyan":ccode+"46m","yellow":ccode+"43m",
        "green":ccode+"42m","magenta":ccode+"45m",}
CLENGTH = len(COLORS["default"])

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
                            "skeleton":self.geom_skeleton,
                            None:self.geom_none}
        self.act_set_dict = {"switch_sprite":self.act_switch_sprite,
                            "rotate":self.act_rotate,
                            "quit":self.act_quit,
                            "sound":self.act_sound,
                            "unlock":self.act_unlock,
                            "switch_map":self.act_switch_map,
                            "switch_theme":self.act_switch_theme,
                            "kill":self.act_kill,
                            "up_score":self.up_score}   
        self.key_dict = {"wasd":
                            {"w":self.move_up,"s":self.move_down,
                            "a":self.move_left,"d":self.move_right,
                            "e":self.run_interacts,"ctrl+r":self.reload_screen},
                        "dirs":
                            {"up arrow":self.move_up,"left arrow":self.move_left,
                            "down arrow":self.move_down,"right arrow":self.move_right,
                            ".":self.run_interacts}}
        
        self.default_color = COLORS["default"]

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
            print(CLEAR,self.default_color)
            self.start_time = time()
            self.play_theme()
        self.init_objs()
        self.init_rendering()

    def end_game(self):
        """All the comes after the main game_loop"""
        mixer.music.stop()
        self.play_sound("quit")
        self.total = self.frames/(time()-self.start_time)
        print(f"{COLORS['default']}{SPACES}Game Over!\nAverage FPS: {self.total:.3f}")
        scores = []
        for obj in self.objs.objs:
            if not obj.simple:
                if obj.move == "wasd":
                    scores.append('Player 1: ' + str(obj.score))
                elif obj.move =="dirs":
                    scores.append('Player 2: ' + str(obj.score))
        print(f"Scores: {scores}")
        input(f"Press ENTER to exit.\n") # Hide input from the whole game
        print(COLORS['default'],CLEAR)

    def game_loop(self):
        """This is what loops for every game tick.
        It is run by the run_game method."""
        self.frame_start = time()
        self.move_all()
        self.rendering()
        self.curr_map.print_all()
        self.run_fps()
    
    def run_fps(self):
        self.frames += 1
        self.tick = (self.tick + 1)%MAX_TICK
        self.f_time = time()
        print("FPS:",1/(self.f_time-self.frame_start))
        self.fpss.append(self.f_time)

    def set_default_color(self,color):
        self.default_color = color
        self.objs.default_color = color

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
        id_tracker = []
        self.objs.update_objs = []
        in_range = self.curr_map.window[1] + W_HEI + (WGC_Y*2)
        for obj in self.objs.objs:
            if obj.origy > in_range:
                break
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
                            else: self.flip_sprite(obj)
                        else:
                            if self.can_move(obj,-1):
                                self.move_left(obj)
                            else: self.flip_sprite(obj)
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
        if is_pressed("q"):
            self.quit = True
        if is_pressed("p"):
            mixer.music.set_volume(.25)
            wait("p")
            sleep(.5)
            mixer.music.set_volume(1)

    def player_actions(self,obj):
        # PLAYER MOVEMENT:
        if obj.move in self.key_dict.keys(): # "wasd" or "dirs"
            for key in self.key_dict[obj.move].keys():
                if is_pressed(key):
                    self.key_dict[obj.move][key](obj)
        self.run_acts(obj)
        # CAMERA MOVING:
        if "x" in self.camera_follow:
            if self.curr_map.width > self.curr_map.window[0] + W_WID < obj.origx + WGC_X + obj.width():
                self.move_camera(1)
            elif self.curr_map.window[0] + WGC_X > obj.origx:
                if self.curr_map.window[0] > 0:
                    self.move_camera(-1)
        if "y" in self.camera_follow:
            if self.curr_map.height > self.curr_map.window[1] + W_HEI < obj.origy + WGC_Y:
                self.move_camera(0,1)
            elif self.curr_map.window[1] + WGC_Y > obj.origy - obj.height():
                if self.curr_map.window[1] > 0:
                    self.move_camera(0,-1)
        # GAME-ENDING CHECKS:
        if obj.hp <= 0 or obj.origy == self.curr_map.width -1:
            self.quit = True
            self.kill_obj(obj)

    def can_move_camera(self,x=0,y=0,obj=None):
        pass    
    def move_camera(self,x=0,y=0):
        self.curr_map.window[0] += x
        self.curr_map.window[1] += y
        self.curr_map.start_window_y += y
        self.curr_map.end_window_y += y
        self.curr_map.start_window_x += x
        self.curr_map.end_window_x += x
    def kill_obj(self,obj,sound:bool=False): # DEATH
        if sound:
            self.play_sound("death")
        self.add_to_update_objs(obj)
        obj.set_origin(0,0)
        obj.live = False
        self.set_sprite(obj,"dead")
        obj.move = None

    # Synonymous functions
    def move_left(self,obj):
        self.set_sprite(obj,obj.animate["a"])
        if time() - obj.move_time["a"] > 1/obj.xspeed:
            obj.move_time["a"] = time()
            self.move_obj(obj,-1)
    def move_right(self,obj):
        self.set_sprite(obj,obj.animate["d"])
        if time() - obj.move_time["d"] > 1/obj.xspeed:
            obj.move_time["d"] = time()
            self.move_obj(obj,1)
    def move_down(self,obj):
        self.set_sprite(obj,obj.animate["s"])
        if time() - obj.move_time["s"] > 1/obj.yspeed:
            obj.move_time["s"] = time()
            if obj.grav:
                obj.jump = 0
            self.move_obj(obj,0,1)
    def move_up(self,obj):
        self.set_sprite(obj,obj.animate["w"])
        if time() - obj.move_time["w"] > 1/obj.yspeed:
            obj.move_time["w"] = time()
            if not obj.grav:
                self.move_obj(obj,0,-1)
            elif not self.can_move(obj,0,1): # If on top of something.
                obj.jump = obj.max_jump
                self.move_obj(obj,0,-1)
                self.play_sound("jump")
            elif obj.jump > 0:
                self.move_obj(obj,0,-1)

    def obj_from_char(self,char):
        for obj in self.objs.objs:
            if char in obj.char:
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

    def reload_screen(self,obj):
        self.init_rendering()

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
                        try:bubble.add(self.curr_map.geom_map[y][xs-1])
                        except:pass
                        try:bubble.add(self.curr_map.geom_map[y][xf])
                        except:pass
                    if act.arg[0] in bubble:
                        self.act_set_dict[act.effect](obj,act.arg)

    # These functions are put into act_set_dict, for quicker lookup than if statements.
    def act_switch_sprite(self,obj,arg):
        # ARG: dictionary of old img key and new img value
        self.set_sprite(obj,arg[obj.img])
    def act_switch_theme(self,obj,arg):
        mixer.music.stop()
        self.add_theme(arg[-1])
        self.play_theme()
    def act_rotate(self,obj,arg):
        obj.rotate_right()
        self.objs.sprites[obj.img] = obj.sprite
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
    def up_score(self,obj,arg):
        obj.score += arg[-1]        

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
                        if BLANK not in self.curr_map.geom_map[y][x]:
                            return False
                    except: return False
        elif obj.geom == "line" or obj.geom == "skeleton":
            for x in range(xs,xf):
                try:
                    if BLANK not in self.curr_map.geom_map[obj.origy+move_y][x]:
                        return False
                except: return False
        elif obj.geom == "complex":
            for y in range(ys,yf):
                for x in range(xs,xf):
                    try:
                        if BLANK not in self.curr_map.geom_map[y][x]:
                            return False
                    except: return False
        return True
    def move_map_char(self,obj,move_x,move_y):
        """Similar to self.set_xy, only applies to objs.objs."""
        newx = obj.origx + move_x
        newy = obj.origy + move_y
        self.add_to_update_objs(obj)
        # re-init of this list is at the start of move_all
        i = self.objs.find_obj_index(obj)
        obj = self.objs.objs.pop(i)
        obj.origy = newy
        obj.origx = newx
        i = 0
        while i < len(self.objs.objs)-1:
            if self.objs.objs[i].origy < newy:
                i+=1
            elif self.objs.objs[i].origy == newy and self.objs.objs[i].origx < newx:
                i+=1
            else:
                self.objs.objs.insert(i,obj)
                i = len(self.objs.objs)
    

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
        if BLANK not in obj.sprite[y][x]]
        for y in range(obj.height())]
    def geom_line(self,obj):
        [self.curr_map.set_xy_geom(x + obj.origx, obj.origy, obj.char)
        for x in range(obj.width())]
    def geom_skeleton(self,obj):
        [self.curr_map.set_xy_geom(x + obj.origx, obj.origy, obj.char)
        for x in range(obj.width())
        if BLANK not in obj.sprite[-1][x]]
    def geom_none(self,obj):
        pass

    def add_to_update_objs(self,obj):
        """Adds everything in the rows of a moved object into
        the updated objects list."""
        # Clear the render area the sprite is currently at.
        for y in range(obj.origy-obj.height(),obj.origy+1):
            for x in range(obj.origx-1,obj.origx + obj.width()+1):
                self.curr_map.set_xy_rend(x,y,BLANK)
                char = self.curr_map.get_xy_geom(x,y)
                if len(char) > 1:
                    char = char[CLENGTH+1]
                if char == obj.char:
                    self.curr_map.set_xy_geom(x,y,BLANK)
        # Render the area the sprite currently takes up as if it weren't there
        min_y = obj.origy - obj.height()
        #if min_y < self.curr_map.start_window_y:
        #    min_y = self.curr_map.start_window_y
        max_y = obj.origy + self.objs.max_height
        #if max_y > self.curr_map.end_window_y:
        #    max_y = self.curr_map.end_window_y
        min_x = obj.origx - self.objs.max_width
        #if min_x < self.curr_map.start_window_x:
        #    min_x = self.curr_map.start_window_x
        max_x = obj.origx + self.objs.max_width
        #if max_x > self.curr_map.end_window_x:
        #    max_x = self.curr_map.start_window_x

        i = 0
        c_obj = self.objs.objs[i]
        while c_obj.origy < min_y or (c_obj.origx < min_x and c_obj.origy >= min_y):
            i += 1
            c_obj = self.objs.objs[i]
        while i < len(self.objs.objs)-1 and self.objs.objs[i].origy <= max_y:
            if min_x <= c_obj.origx <= max_x:
                self.objs.add_to_update_objs(c_obj)
                # The main object will be at the center of this search.
            i += 1
            c_obj = self.objs.objs[i]
        
    def set_sprite(self,obj,new_img):
        self.add_to_update_objs(obj) #re-render
        self.objs.set_sprite(obj,new_img)
        self.geom_set_dict[obj.geom](obj)

    def flip_sprite(self,obj):
        assert obj.animate not in [None,"flip"], "This object is not animated."
        self.add_to_update_objs(obj)
        obj.face_right = not obj.face_right
        if obj.face_right:
            self.set_sprite(obj,obj.animate["d"])

    def init_rendering(self):
        self.curr_map.empty_map(self.curr_map.rend_map)
        self.curr_map.empty_map(self.curr_map.geom_map)
        for obj in self.objs.objs:
            self.render_obj(obj)
            self.geom_set_dict[obj.geom](obj)
            # Geometry is all-in-all static, and otherwise
            # changed by object movement alone.
    def rendering(self):
        """This creates the output AND geometry
        maps out of all object sprites. NOT for initializing
        objects (not that you asked)."""
        #start_range_y = self.curr_map.window[1] - (WGC_Y*3)
        end_range_y = self.curr_map.window[1] + W_HEI + (WGC_Y*3)
        #start_range_x = self.curr_map.window[0] - (WGC_X*3)
        #end_range_x = self.curr_map.window[0] + W_WID + (WGC_X*3)
        for obj in self.objs.update_objs:
            if obj.origy < end_range_y:
                self.render_obj(obj)
            else:
                break
    def render_obj(self,obj):
        # Print a sprite at its origin.
        ypos = obj.origy - obj.height()
        substance = False
        if obj.geom != "skeleton":
            for row in obj.sprite:
                substance = False
                xpos = obj.origx
                for char in row:
                    if char != SIGN:
                        self.curr_map.set_xy_rend(xpos, ypos, char)
                        substance = True
                    elif substance:
                        break
                    xpos += 1
                ypos += 1     
        else: # skeleton
            for row in obj.sprite:
                xpos = obj.origx
                substance = False
                for char in row:
                    if char != SIGN:
                        if BLANK not in char:
                            self.curr_map.set_xy_rend(xpos, ypos, char)
                        substance = True
                    elif substance:
                        break
                    xpos += 1
                ypos += 1
        # Add any text above the object sprite
        if obj.txt > -1:
            txt = self.objs.texts[obj.txt]
            out_y = obj.origy - obj.height() - 2
            out_x = obj.origx + (obj.width())//2 - len(txt)//2
            [self.curr_map.set_xy_rend(out_x+i,out_y,txt[i]) for i in range(len(txt))]

class Map():
    """Three arrays are stored in a Map object: the wasd input 
    map, the output map, and a geom map.
    Set the map path upon initialization"""
    def __init__(self):
        self.geom_map = [] # For checking collision.
        self.height = W_HEI
        self.width = W_WID
        self.sparse_map = list() # Made to store user-made map.
            # Map of the final screen. 1D list of strings.
        self.rend_map = [] # Map of what will be rendered
            # UPDATE: GETTING PHASED OUT.
        self.overlay = [[BLANK for x in range(W_WID)] for y in range(W_HEI)]
            # Optional overlay of the game.
        self.use_overlay = False
        self.window = [0,0] # X,Y, AS IT SHOULD BE >:D
            # These are the map coordinates of the 
            # top-left-most char shown in the window.
        self.start_window_y = self.window[1]
        self.end_window_y = self.window[1] + W_HEI + (WGC_Y*3)
        self.start_window_x = self.window[0] - (WGC_X*3)
        self.end_window_x = self.window[0] + W_WID + (WGC_X*3)
        self.file_name = ""

    def set_path(self,path):
        self.store_map(self.sparse_map,path)
        self.empty_map(self.rend_map)

    def set_overlay(self,path):
        self.use_overlay = True
        self.store_map(self.overlay,path)

    def empty_map(self,map:list):
        """ Create a blank map of size self.width by self.height.
        Should not be used on sparse_map"""
        if len(map) == 0: # If the map is new.
            [map.append(list(BLANK * self.width)) for y in range(self.height)]
        else:
            for y in range(self.height):
                map[y] = (list(BLANK * self.width))
        return map

    def store_map(self,sparse_map:list,path):
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
        print(RETURN)
        [[print("".join(self.rend_map[row][self.window[0]:self.window[0] + W_WID]))] for row in range(self.window[1],self.window[1]+W_HEI)]

    def set_xy_geom(self,x,y,char):
        """Sets char at a given position on map"""
        try: self.geom_map[y][x] = char
        except: pass
    def get_xy_geom(self,x,y):
        """Returns what character is at this position."""
        try: return self.geom_map[y][x]
        except: return BLANK
    def set_xy_rend(self,x,y,char):
        """Sets char at a given position on map"""
        try: self.rend_map[y][x] = char
        except: pass
    def get_xy_rend(self,x,y):
        try: return self.rend_map[y][x]
        except: return BLANK

class Acts():
    def __init__(self):
        self.acts = []
    def new(self,name="default",kind="interact",
        char="",effect="",arg="",locked = False):
        new_act = self.Act(name,kind,char,effect,arg,locked)
        if effect == "sound":
            self.acts.insert(0,new_act) # Sounds must be played first.
        else:
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
        self.update_objs = []
        # This is a list of objs that moved or changed form. It is emptied 
        # at the start of every frame, and is what the rendering function is based on.
        # These HAVE to be ordered, thus add_to_update_objs()
        self.usr_objs = [] # These are all the original objects.
        self.sprites = {"dead":[[str(" ")]]}
        # Sprites are stored as rows of strings, so that color codes may be appended.
        self.texts = []
        self.max_height= 0 
        self.max_width = 0
        self.max_id = 0
        self.default_color = COLORS['default']

    def get_sprites(self,path):
        """Takes the sprite file path and stores the sprites in
        the sprites dictionary. It also interprets the sprites for
        parts of their strings that are empty."""
        path = DIRPATH + "/" + path
        curr_img = None
        curr_sprite = []
        height = 0
        # Adds parent directory of running program
        with open(path, 'r',encoding='utf-8') as file:
            line = file.readline()[:-1] # Removes "\n".
            while(line):
                if line[0] == SIGN and line[-1] == SIGN:
                # Begins and ends with SIGN
                    if curr_img != None: # If this isn't the first img
                        if len(curr_sprite[0]) > self.max_width:
                            self.max_width = len(curr_sprite[0])
                        if height > self.max_height:
                            self.max_height = height
                        self.sprites[curr_img] = curr_sprite
                        curr_sprite = []
                    curr_img = line[1:-1] # Remove SIGNs
                    height = 0
                else:
                    line = self.replace_spaces(line)
                    curr_sprite.append(list(line))
                    height +=1
                line = file.readline()[:-1] # Removes the \n

    def replace_spaces(self,line:str):
        """All spaces before and after other characters are replaced
        by the constant SIGN."""
        s1 = True
        s2 = True
        start = ""
        end = ""
        for x in range((len(line)+1)//2):
            char = line[x]
            if char != BLANK or not s1: s1 = False
            else:   char = SIGN
            start = start + char
            char = line[len(line)-x-1]
            if char != BLANK or not s2: s2 = False
            else:   char = SIGN
            end = char + end
        if len(line)%2==0:
            return start + end
        else:
            return start[:-1] + end

    def get_texts(self,path):
        path = DIRPATH + "/" + path
        with open(path, 'r',encoding='utf-8') as file:
            line = file.readline()[:-1]
            while(line):
                self.texts.append(line)
                line = file.readline()[:-1]

    def add_to_update_objs(self,obj):
        """Adds an object to the list of objects that will be updated
        on the map. This list is unordered."""
        self.update_objs.append(obj)
    
    def add_color(self,obj,char,row=1):
        if char != SIGN:
            if char != "_" or row != 0:
                char = obj.color + char + self.default_color
        return char

    def get_flipped_sprite(self,obj):
        """ Returns a vertically mirrored
        2D sprite of the given sprite"""

        new_sprite = []
        for row in range(len(obj.sprite)):
            line = []
            for x in range(len(obj.sprite[row])):
                char = obj.sprite[row][len(obj.sprite[row])-x-1]
                if len(char) > 1:
                    char = char[len(char)//2]
                if char in FLIP_CHARS:
                    char = FLIP_CHARS[char]
                char = self.add_color(obj,char,row)
                line.append(char)
            new_sprite.append(line)
        return new_sprite

    def set_sprite(self,obj,new_img):
        obj.img = new_img
        obj.sprite = []
        for row in self.sprites[obj.img]:
            obj.sprite.append(list(row)) # Make a list copy
        if len(obj.get_char(0,0)) == 1:
            for y in range(len(obj.sprite)):
                for x in range(len(obj.sprite[y])):
                    obj.sprite[y][x] = self.add_color(obj,obj.sprite[y][x],y)
        obj.rotate = 0

    def find_obj_index(self,obj):
        i=0
        while i < len(self.objs):
            currid = self.objs[i].id
            if obj.id == currid:
                return i
            i+= 1
        return -1
    
    def append_objs(self,objs:list=[]):
        """Add a list of objects to self.objs."""
        [self.append_obj(obj) for obj in objs]
            
    def append_obj(self,obj,rotate=0):
        """Important object initialization happens here."""
        while rotate != obj.rotate:
            obj.rotate_right()
        self.set_sprite(obj,obj.img)
        if obj.animate == "flip":
            original = obj.img
            flip_img = reversed(obj.img)
            self.sprites[flip_img] = self.get_flipped_sprite(obj)
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
            self.sprites[facing_left] = self.get_flipped_sprite(obj)
            obj.animate = {"w":facing_up,"a":facing_left,"s":facing_down,"d":obj.img}
        obj.id = self.max_id
        self.max_id+=1
        obj.i = len(self.objs)
        self.objs.append(obj)
        self.usr_objs.append(obj)

    def new(self,img, char, x=0,y=0, geom = "all",
    move = None, xspeed = 1, yspeed = 1, hp =1,face_right=True,
    face_down=False, grav=False,dmg = 1, enemy_chars=[],
    dmg_dirs=[], set_rotate=0, animate=None,txt=-1,max_jump=1,
    color=None,data=dict()):
        """Creates an Obj and appends it to the objs list."""
        if color == None:
            color = self.default_color
        obj = self.Obj(img, char, x,y, geom, move,xspeed,yspeed,
            hp,face_right,face_down,grav,dmg,enemy_chars,dmg_dirs,
            animate,txt,max_jump,color,data)
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
           o.animate,o.txt,o.max_jump,o.color,o.data)
        return self.objs[-1]

    class Obj():
        def __init__(self,img, char, x=0,y=0, geom = "all",
        move = None, xspeed = 1,yspeed = 1,hp =1,face_right=True,
        face_down=False,grav:bool=False,dmg = 1,enemy_chars=[],dmg_dirs=[],
        animate=None,txt:int=-1,max_jump=1,color=COLORS["default"],data=dict()):
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
            if type(color) == type(420):
                self.color = color_by_num(color)
            else:
                self.color = color # The literal escape code, not the number.
            # "flip" is default, mirrors the image for every change between right and left.
            # Otherwise, if it's not None it becomes a dictionary: {w,a,s,d:sprite images.}

            self.id = 0
            
            self.txt = txt # line number from textsheet
            self.face_right = face_right # Left: False, Right: True
            self.face_down = face_down # Up: False, Down: True
            self.sprite = [] # Must be set through Objs function new().
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
            """Returns the char stored here in a sprite sprite.
            Takes x,y, returns [y][x]"""
            try:    return self.sprite[y][x]
            except: return BLANK
            
        def width(self):
            return len(self.sprite[0])
        def height(self):
            return len(self.sprite)

        def rotate_right(self):
            """Rotates the object sprite 90 degrees."""
            self.rotate = (self.rotate + 1)%4
            # Only works properly on even-width objects.
            sprite = [] # Must make a new sprite sequentially,
            for x in range(len(self.sprite[0])//2):
                row = [] # otherwise it creates pointers.
                for y in range(len(self.sprite)*2):
                    row.append(BLANK)
                sprite.append(row)
            # To rotate, it is inverted, and then mirrored along y.
            for y in range(len(sprite)):
                for x in range(len(sprite[0])//2):
                    sprite[y][-((x*2)+2)] = self.sprite[x][(y*2)]
                    sprite[y][-((x*2)+1)] = self.sprite[x][(y*2)+1]
            self.sprite = sprite

def color_by_num(x):
    return ("\033[48;5;" + str(x) + "m")

def print_color_numbers():
    """For Debugging: Returns a sheet of all color numbers highlighted
    by their respective color."""
    spaces = " "
    color_base = "\033[48;5;"
    for x in range(256):
        color = color_base + str(x) + "m"
        try:spaces = " " * (3 - int(log(x,10)))
        except:pass
        print(f"{color}{x}{spaces}{COLORS['default']}",end="")
        if (x-15)%6 == 0:
            print()