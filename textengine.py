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
default_color = COLORS['default']

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
        self.texts = []
        self.quit = False
        self.camera_follow = []

        mixer.init()
        self.themes = []
        self.sounds = dict()

        self.frames = 0
        self.tick = 0
        self.fps = 0
        self.fpss = []
        self.display_fps = ""
        self.start_time = 0
        self.fps_min = 30
        self.game_speed = 1 # General actions can be called at 1/second.
        self.total = 0
        self.no_updates = False

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
                            "switch_geometry":self.act_switch_geom,
                            "message":self.act_display_msg,
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

    def run_game(self,debug=True):
        """Combine the map and the objs and begin the main game loop."""
        self.init_map()
        if debug:
            while(not self.quit):
                self.game_loop_debug()
            self.end_game()
        else:
            while(not self.quit):
                self.game_loop()

    def switch_map(self,index):
        if self.map_index >= len(self.map_list):
            self.map_index = 0
        self.map_index = index
        self.curr_map = self.map_list[self.map_index]
        # Reset Objects.
        self.objs.objs = list()
        for obj in self.objs.obj_pallete:
            obj.origx = 0
            obj.origy = 0
            self.objs.objs.append(obj)
    
    def next_map(self):
        self.switch_map(self.map_index + 1)

    def init_map(self,first=True):
        """All that comes before the main game_loop"""
        if first:
            print(CLEAR,default_color)
            self.start_time = time()
            self.play_theme()
        self.init_objs()
        self.init_rendering()
        self.curr_map.print_all(self.display_fps)

    def game_loop(self):
        """This is what loops for every game tick.
        It is run by the run_game method."""
        self.frame_start = time()
        self.move_all()
        self.rendering()
        self.add_overlay()
        if not self.no_updates:
            self.curr_map.print_all(self.display_fps)
            self.no_updates = True

    def game_loop_debug(self):
        self.frame_start = time()
        self.move_all()
        self.rendering()
        self.add_overlay()
        if self.fps > self.fps_min and not self.no_updates:
            self.curr_map.print_all(self.display_fps)
            self.no_updates = True
            self.run_fps(True)
        else:
            self.run_fps()
    
    def run_fps(self,with_avg=False):
        self.frames += 1
        self.tick = (self.tick + 1)%MAX_TICK
        if time() != self.frame_start:
            self.fps = 1/(time()-self.frame_start)
            if with_avg:
                self.fpss.append(self.fps)
        else:
            self.fps = 999
        self.display_fps = "FPS:" + str(self.fps)

    def end_game(self):
        """All the comes after the main game_loop"""
        mixer.music.stop()
        self.play_sound("quit")
        self.total = self.frames/(time()-self.start_time)
        end_game = COLORS['default']+SPACES+"Game Over!\nAverage FPS: "+str(self.total)+"\n"
        input(f"{end_game}Press ENTER to exit.\n{COLORS['default']}") # Hide input from the whole game
        print(CLEAR)

    def play_theme(self):
        if len(self.themes)>0:
            mixer.music.load(self.themes[0])
            mixer.music.play(-1)
    def add_theme(self,path:str):
        assert len(path) > 4, "Not a valid audio file name."
        self.themes.insert(0,path)
    def add_sound(self, path:str,sound_name:str=""):
        assert len(path) > 4, "Not a valid audio file name."
        new_sound = mixer.Sound(path)
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
        in_range = self.curr_map.end_camera_y + (WGC_Y*2)
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
        for key in self.key_dict[obj.move].keys():
            if is_pressed(key):
                self.key_dict[obj.move][key](obj)
        self.run_acts(obj)
        # CAMERA MOVING:
        move_x = 0
        move_y = 0
        if "x" in self.camera_follow:
            if self.curr_map.width > self.curr_map.end_camera_x < obj.origx + WGC_X + obj.width():
                move_x = 1
            elif self.curr_map.camera_x + WGC_X > obj.origx and self.curr_map.camera_x > 0:
                move_x = -1
        if "y" in self.camera_follow:
            if self.curr_map.height > self.curr_map.end_camera_y < obj.origy + WGC_Y:
                move_y = 1
            elif self.curr_map.camera_y + WGC_Y > obj.origy - obj.height() and self.curr_map.camera_y > 0:
                move_y = -1
        self.move_camera(move_x,move_y)
        # GAME-ENDING CHECKS:
        if obj.hp <= 0 or obj.origy == self.curr_map.width -1:
            self.quit = True
            self.kill_obj(obj) 
    def move_camera(self,x=0,y=0):
        if x!=0 or y!= 0:
            self.no_updates = False
        self.curr_map.camera_x += x
        self.curr_map.camera_y += y
        self.curr_map.end_camera_y += y
        self.curr_map.end_camera_x += x
    def kill_obj(self,obj,sound:bool=False): # DEATH
        if sound:
            self.play_sound("death")
        obj.set_origin(0,0)
        obj.live = False
        self.set_sprite(obj,"dead")
        obj.move = None

    def get_texts(self,path):
        path = DIRPATH + "/" + path
        with open(path, 'r',encoding='utf-8') as file:
            line = file.readline()[:-1]
            while(line):
                self.texts.append(line)
                line = file.readline()[:-1]

    # Synonymous functions
    def move_left(self,obj):
        self.set_sprite(obj,obj.animate["a"])
        obj.face_right = False
        if time() - obj.move_time["a"] > 1/obj.xspeed:
            obj.move_time["a"] = time()
            self.move_obj(obj,-1)
    def move_right(self,obj):
        self.set_sprite(obj,obj.animate["d"])
        obj.face_right = True
        if time() - obj.move_time["d"] > 1/obj.xspeed:
            obj.move_time["d"] = time()
            self.move_obj(obj,1)
    def move_down(self,obj):
        self.set_sprite(obj,obj.animate["s"])
        obj.face_down = True
        if time() - obj.move_time["s"] > 1/obj.yspeed:
            obj.move_time["s"] = time()
            if obj.grav:
                obj.jump = 0
            self.move_obj(obj,0,1)
    def move_up(self,obj):
        self.set_sprite(obj,obj.animate["w"])
        obj.face_down = False
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
                if not act.locked and act.kind == "interact":
                    if obj.char == act.char:
                        self.act_set_dict[act.effect](obj,act.arg)
                    else:
                        if obj.face_down:
                            if act.char in self.curr_map.geom_map[yf][xs:xf]: #BELOW
                                i=self.objs.find_obj_index(obj)+1
                                found = False
                                while not found and i < len(self.objs.objs):
                                    i_obj = self.objs.objs[i]
                                    if act.char == i_obj.char and i_obj.origy == yf and xs <= i_obj.origx+i_obj.width() and xf >= i_obj.origx:
                                        found = True
                                        self.act_set_dict[act.effect](i_obj,act.arg)
                                    else:
                                        i+=1
                        else:
                            if act.char in self.curr_map.geom_map[ys-1][xs:xf]: #ABOVE
                                i=self.objs.find_obj_index(obj)
                                found = False
                                while not found and i > -1:
                                    i_obj = self.objs.objs[i]
                                    if act.char == i_obj.char and i_obj.origy and ys-1 and xs <= i_obj.origx+i_obj.width() and xf >= i_obj.origx:
                                        found = True
                                        self.act_set_dict[act.effect](i_obj,act.arg)
                                    else:
                                        i-=1
                        """for y in range(ys,yf):
                            if obj.face_right:
                                if self.curr_map.geom_map[y][xf] == act.char: #RIGHT
                                    pass
                            else:
                                if self.curr_map.geom_map[y][xs-1] == act.char: #LEFT
                                    pass"""

    def reload_screen(self,obj):
        self.init_rendering()

    def set_xy_limits(self,obj):
        """Used in run_acts and run_interacts"""
        xs = obj.origx
        xf = min([xs+obj.width(),self.curr_map.width])
        if obj.geom in ["all","complex"]:
            yf = obj.origy + 1
            ys = yf - obj.height()
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
        """ARG: dictionary of old img key and new img value"""
        self.set_sprite(obj,arg[obj.img])
    def act_switch_geom(self,obj,arg):
        obj.geom = arg[obj.geom]
        self.set_sprite(obj,obj.img)
    def act_switch_theme(self,obj,arg):
        mixer.music.stop()
        self.add_theme(arg[-1])
        self.play_theme()
    def act_display_msg(self,obj,arg):
        arg = arg[-1]
        if arg == int(arg):
            try:
                msg = self.texts[arg]
            except IndexError:
                msg = ""
        else:
            msg = arg
        self.curr_map.overlay.add(msg)
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
        """Moves an object to a given location if no geometry is there."""
        move_x = obj.origx - x
        move_y = obj.origy - y
        if x > obj.origx:
            move_x *= -1
        if y < obj.origy:
            move_y *= -1
        if self.can_move(obj,move_x,move_y):
            self.move_map_char(obj,move_x,move_y)
    def move_obj(self,obj,move_x = 0,move_y = 0):
        """Moves a single object move_x and move_y amount OR LESS."""
        while move_x != 0 or move_y != 0:
            if self.can_move(obj,move_x,move_y):
                self.move_map_char(obj,move_x,move_y)
                move_x,move_y = 0,0
            else:
                if move_x != 0: move_x += int((move_x*-1)/(abs(move_x)))
                if move_y != 0: move_y += int((move_y*-1)/(abs(move_y)))
                # This brings move_x and move_y 1 closer to 0
    def can_move(self, obj, move_x = 0, move_y = 0):
        """Check if there are any characters in the area that 
        the obj would take up. Takes literal change in x and y.
        Returns True if character can move in that diRECTion."""
        yf = move_y + obj.origy + 1
        ys = yf - obj.height()
        xs = move_x + obj.origx
        xf = xs + obj.width()
        if move_x > 0:      xs = obj.origx + obj.width()
        elif move_x < 0:    xf = obj.origx
        if obj.geom not in ["line","skeleton"]:
            if move_y < 0:
                yf = obj.origy - obj.height() + 1
            elif move_y > 0:
                ys = obj.origy + 1
        else:
            ys = yf - 1
        for y in range(ys,yf):
            for x in range(xs,xf):
                try:
                    if BLANK not in self.curr_map.geom_map[y][x]:
                        return False
                except: return False
        return True
    def move_map_char(self,obj,move_x,move_y):
        """Similar to self.set_xy, only applies to objs.objs."""
        self.add_to_render_objs(obj)
        newx = obj.origx + move_x
        newy = obj.origy + move_y
        obj = self.objs.objs.pop(self.objs.find_obj_index(obj))
        obj.origy = newy
        obj.origx = newx
        i = 0
        while i < len(self.objs.objs):#-1
            if (self.objs.objs[i].origy < newy) or (self.objs.objs[i].origy == newy and self.objs.objs[i].origx < newx):
                i+=1
            else:
                self.objs.objs.insert(i,obj)
                i = len(self.objs.objs)

    def init_objs(self):
        """Initializes all objects, referring to objs.objs made
        by the user, cloning as needed."""
        old_len = len(self.objs.objs)
        for c in self.curr_map.init_map:
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
        for x in range(obj.origx, min([obj.origx + obj.width(), len(self.curr_map.geom_map[y])]) )]
        for y in range(obj.origy - obj.height() +1,obj.origy +1)]
    def geom_complex(self,obj):
        # Based on all characters of a sprite that are not blank.
        [[self.curr_map.set_xy_geom(x + obj.origx, obj.origy - y, obj.char) 
        for x in range( min([obj.width(), len(self.curr_map.geom_map[y])-obj.origx]) ) 
        if SIGN not in obj.sprite[y][x]]
        for y in range(obj.height())]
    def geom_line(self,obj):
        [self.curr_map.set_xy_geom(x + obj.origx, obj.origy, obj.char)
        for x in range( min([obj.width(), len(self.curr_map.geom_map[-1])-obj.origx]) )]
    def geom_skeleton(self,obj):
        [self.curr_map.set_xy_geom(x + obj.origx, obj.origy, obj.char)
        for x in range( min([obj.width(), len(self.curr_map.geom_map[-1])-obj.origx]) )
        if SIGN not in obj.sprite[-1][x]]
    def geom_none(self,obj):
        pass

    def add_to_render_objs(self,obj):
        """Adds everything in the rows of a moved object into
        the updated objects list."""
        # Clear the render area the sprite is currently at.
        start_y = obj.origy-obj.height()+1
        for y in range(start_y,obj.origy+1):
            start_x = find_non_matching(obj.sprite[y-start_y],SIGN) + obj.origx
            for x in range(start_x, min([obj.origx + obj.width(), self.curr_map.width ])):
                char = obj.sprite[y-start_y][x-obj.origx]
                if SIGN not in char:
                    self.curr_map.remove_xy_rend(x,y,char)
        self.remove_geom(obj)
        # Render the objects that the sprite area currently takes up.
        self.objs.render_objs.add(obj)
    
    def remove_geom(self,obj):
        for y in range(obj.origy-obj.height()+1,obj.origy+1):
            for x in range(obj.origx, min([obj.origx + obj.width(), self.curr_map.width ])):
                if obj.char in self.curr_map.get_xy_geom(x,y):
                    self.curr_map.set_xy_geom(x,y,BLANK)
        
    def set_sprite(self,obj,new_img):
        self.add_to_render_objs(obj)
        self.objs.set_sprite(obj,new_img)
        self.geom_set_dict[obj.geom](obj)

    def flip_sprite(self,obj):
        assert obj.animate not in [None,"flip"], "This object is not animated."
        obj.face_right = not obj.face_right
        if obj.face_right:
            self.set_sprite(obj,obj.animate["d"])

    def init_rendering(self):
        self.curr_map.clear_rend_map()
        self.curr_map.clear_map(self.curr_map.geom_map)
        self.no_updates = False
        for obj in self.objs.objs:
            self.render_obj(obj)
            self.geom_set_dict[obj.geom](obj)
            # Geometry is all-in-all static, and otherwise
            # changed by object movement alone.
        self.objs.render_objs = set()
    def rendering(self):
        """This creates the output AND geometry
        maps out of all object sprites. NOT for initializing
        objects (not that you asked)."""
        end_range_y = self.curr_map.end_camera_y + (WGC_Y*3)
        if len(self.objs.render_objs) > 0:
            self.no_updates = False
            for obj in self.objs.render_objs:
                if obj.origy < end_range_y: self.render_obj(obj)
                else:   break
            self.objs.render_objs = set()
    def render_obj(self,obj):
        # Print a sprite at its origin.
        end_x = min([obj.origx + obj.width(),self.curr_map.width])
        start_y = obj.origy-obj.height()+1
        for y in range(start_y,obj.origy+1):
            for x in range(obj.origx,end_x):
                char = obj.sprite[y-start_y][x-obj.origx]
                if SIGN not in char:
                    if self.curr_map.rend_map[y][x][-1] != BLANK:
                        self.curr_map.rend_map[y][x].append(BLANK)
                    self.curr_map.rend_map[y][x][-1] = char
        # Add any text above the object sprite
        if obj.txt > -1:
            txt = self.texts[obj.txt]
            out_y = obj.origy - obj.height() - 2
            out_x = obj.origx + (obj.width())//2 - len(txt)//2
            [self.curr_map.set_xy_rend(out_x+i,out_y,txt[i]) for i in range(len(txt))]

    def add_overlay(self):
        i = 0
        for string in self.curr_map.overlay:
            #placement on screen is based on index in the overlay
            x = self.curr_map.camera_x + (W_WID - len(string))//2
            y = self.curr_map.camera_y + W_HEI - i - 1
            for char in string:
                if char != BLANK:
                    self.curr_map.set_xy_rend(x, y,char)
                x += 1
            i += 1

class Map():
    """Three arrays are stored in a Map object: the wasd input 
    map, the output map, and a geom map.
    Set the map path upon initialization"""
    def __init__(self):
        self.init_map = list() # Made to store user-made map. 1D list of strings.
        self.rend_map = [] # Map of what will be rendered. 3-Dimensional.
        self.geom_map = [] # For checking collision.
        self.print_map = ""
        self.overlay = set()
        self.height = W_HEI
        self.width = W_WID
        self.camera_x = 0
        self.camera_y = 0 # start_window_y
        self.end_camera_y = W_HEI
        self.end_camera_x = W_WID
            # These are the map coordinates of the 
            # top-left-most char shown in the window.
        self.file_name = ""

    def set_path(self,path):
        self.store_user_map(path)
        self.clear_rend_map()

    def clear_map(self,map):
        """ Create a blank map of size self.width by self.height.
        Should not be used on init_map"""
        if len(map) == 0: # If the map is new.
            [map.append(list(BLANK * self.width)) for y in range(self.height)]
        else:
            for y in range(self.height):
                map[y] = (list(BLANK * self.width))
        return map
    def clear_rend_map(self):
        if len(self.rend_map) == 0: # If the map is new.
            for y in range(self.height):
                new_row = []
                for x in range(self.width):
                    new_item = [[BLANK]] # z-levels start at 1
                    new_row.append(new_item)
                self.rend_map.append(new_row)
        else:
            for y in range(self.height):
                for x in range(self.width):
                    self.rend_map[y][x] = list(BLANK) # Remove all other z-levels

    def store_user_map(self,path):
        """ Stores characters and their coords in self.init_map,
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
                        self.init_map.append([x,y,line[x]])
                y += 1
                line = file.readline()
        self.height = y
        self.width = maxwidth

    def print_all(self,fps):
        """Displays the proper area of self.rend_map."""
        self.print_map = ""
        self.line = []
        for row in range(self.camera_y,self.end_camera_y):
            self.line.append(default_color)
            [self.print_get_row(self.rend_map[row][x][-1]) for x in range(self.camera_x,self.end_camera_x)]
            self.line.append("\n")
        self.print_map = "".join(self.line)
        print(f"{RETURN}{self.print_map}{fps}")
    def print_get_row(self,char):
        self.line.append(char)

    def set_xy_geom(self,x,y,char):
        """Sets char at a given position on map"""
        self.geom_map[y][x] = char
    def get_xy_geom(self,x,y):
        """Returns what character is at this position."""
        return self.geom_map[y][x]
    def set_xy_rend(self,x,y,z,char):
        """Sets char at a given position on map"""
        if self.rend_map[y][x][z] == BLANK:
            self.rend_map[y][x][z] = char
        else:
            self.rend_map[y][x].append(char)
    def remove_xy_rend(self,x,y,char):
        if len(self.rend_map[y][x]) > 1:
            for z in range(len(self.rend_map[y][x])):
                if self.rend_map[y][x][z] == char:
                    self.rend_map[y][x].pop(z)
                    break
        elif self.rend_map[y][x][0] == char: # Only one layer.
            self.rend_map[y][x][0] = BLANK

            
    def get_xy_rend(self,x,y,z=-1):
        return self.rend_map[y][x][z]

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
        self.render_objs = set()
        # This is an ordered list of objs that moved or changed form. It is emptied 
        # at the start of every frame, and is what the rendering function is based on.
        self.obj_pallete = set() # These are all the original objects.
        self.sprites = {"dead":[[str(" ")]]}
        # Sprites are stored as rows of strings, so that color codes may be appended.
        #self.texts = []
        self.max_height= 0 
        self.max_width = 0
        self.max_id = 0

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
    
    def set_sprite_color(self,obj):
        chars = [SIGN]
        if obj.geom == "skeleton":
            chars.append(BLANK)
        for y in range(obj.height()):
            for x in range(obj.width()):
                char = obj.sprite[y][x]
                if chars[0] not in char and chars[-1] not in char:
                    char = obj.color + char # This is not an empty character (BLANK or SIGN)
                else:
                    char = SIGN # Turn BLANKS into SIGNS, so no BLANKS need to be skipped.
                if x != obj.width() -1:
                    if obj.sprite[y][x+1] == chars[-1] or obj.sprite[y][x+1] == chars[0]:
                        char = char + default_color
                obj.sprite[y][x] = char
            obj.sprite[y][-1] = char + default_color


    def get_flipped_sprite(self,obj,sprite):
        """ Returns a vertically mirrored
        2D sprite of the given sprite"""
        new_sprite = []
        for row in range(len(sprite)):
            line = []
            for x in range(len(sprite[row])):
                char = sprite[row][len(sprite[row])-x-1]
                if char in FLIP_CHARS:
                    char = FLIP_CHARS[char]
                line.append(char)
            new_sprite.append(line)
        self.set_sprite_color(obj)
        return new_sprite

    def set_sprite(self,obj,new_img):
        obj.img = new_img
        obj.sprite = []
        for row in self.sprites[obj.img]:
            obj.sprite.append(list(row)) # Make a list copy
        self.set_sprite_color(obj)
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
            self.sprites[flip_img] = self.get_flipped_sprite(obj,self.sprites[obj.img])
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
            self.sprites[facing_left] = self.get_flipped_sprite(obj,self.sprites[obj.img])
            obj.animate = {"w":facing_up,"a":facing_left,"s":facing_down,"d":obj.img}
        obj.id = self.max_id
        self.max_id+=1
        obj.i = len(self.objs)
        self.objs.append(obj)
        self.obj_pallete.add(obj)

    def new(self,img, char, x=0,y=0, geom = "all",
    move = None, xspeed = 1, yspeed = 1, hp =1,face_right=True,
    face_down=False, grav=False,dmg = 1, enemy_chars=[],
    dmg_dirs=[], set_rotate=0, animate=None,txt=-1,max_jump=1,
    color=None,data=dict()):
        """Creates an Obj and appends it to the objs list."""
        if color == None:
            color = default_color
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
            self.layer = 0 # For what z they are put in on-map
            self.enemy_chars = enemy_chars
            self.dmg_dirs = dmg_dirs
            self.animate = animate # Edited in the objs.append_obj function
            if type(color) == type(42):
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

def add_printing(string):
    pass
def move_cursor(x=0,y=0):
    """Moves the cursor from its current position"""
    if x < 0:
        x *= -1
        add_printing(f"\033[{x}D",end='',flush=True)
    elif x > 0:
        add_printing(f"\033[{x}C",end="",flush=True)
    if y < 0:
        y *= -1
        #add_printing(f"\033[{y}B",end='')
        add_printing(f"\033[{y}A",end="",flush=True)
    elif y > 0:
        add_printing("\n"*y,flush=True)

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

def find_non_matching(string,bad_c):
    for c in range(len(string)):
        if string[c]!=bad_c:
            return c
    return 0