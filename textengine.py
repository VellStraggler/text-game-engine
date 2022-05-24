###################################
#                                 #
#      Textoon Game Engine        #
#    Created by: David Wells      #
#          Version 1.0            #
#                                 #
###################################
from keyboard import is_pressed,wait
from pygame import mixer
from os.path import dirname
from os import system
from random import randint
from time import time,sleep
from math import log
system("")
#ALLOWS A WINDOWS TERMINAL TO SOMEHOW UNDERSTAND ESCAPE CODES!! :D
DIRPATH = dirname(__file__) + "/"

BLANK = ' '
SKIP = '$'
CLEAR = "\033[2J"
CUR = '\033[A\033[F'
ZER = '\033[H'
RIT = '\033[1C'
MAX_TICK = 16

W_WID = 100
W_HEI = 29
# Based on the Windows Terminal window at default size.
INFO_HEI=2
RETURN = CUR * (W_HEI+INFO_HEI)
WGC_X = W_WID//2 - 5 
WGC_Y = W_HEI//2 
# WINDOW GUIDE CUSHION, the breathing room between the sprite between
# the window follows and the edge of the window.

SPACES = ' ' * 50
S_LINE = ' ' * W_WID
BUBBLE = [["╱","⎺","╲"],["|"],["╲","_","╱"]]
# /⎺⎺⎺⎺⎺⎺⎺\
#| message |
# \_______/

# Dictionary of chars (keys) and their opposites (values)
FLIP_CHARS = {'\\':'/','/':'\\','[':']',']':'[','{':'}','}':'{','<':'>',
    '>':'<','(':')',')':'(','◐':'◑','◑':'◐','↙':'↘','↘':'↙','כ':'c',
    'c':'כ','◭':'◮','◮':'◭','╱':'╲','╲':'╱','↖':'↗','↗':'↖','⌋':'⌊',
    '⌊':'⌋'}

ccode = "\033[0;39;"
COLORS = {"default":ccode+"49m","white":ccode+"47m",
        "cyan":ccode+"46m","yellow":ccode+"43m",
        "green":ccode+"42m","magenta":ccode+"45m",}
DEFAULT_COLOR = COLORS['default']

class Game():
    """
    Creates an empty map and empty sprite list.
    Fill these using map.set_path(path) and objs.set_path(path).
    """
    def __init__(self):
        self.map_dict = {"default":Map()}
        self.map_name = "default"
        self.map = self.map_dict[self.map_name]
        # A pointer to the current map being played.
        self.objs = self.map.objs
        self.acts = Acts()
        # UPDATE: OBJECTS SHOULD BE DEPENDANT ON THE MAP, NOT ON THE ENTIRE GAME
        # And for every new map created, it should be given a pallete of objects to draw from
        # upon it's initiation.
        self.universal_objs = set()
        self.sprites = {"dead":[[" "]]}
        self.max_sprite_width = 1
        self.max_sprite_height= 1
        self.texts = []
        self.quit = False
        self.camera_follow = []

        mixer.init()
        self.themes = []
        self.sounds = dict()

        self.tick = 0
        self.fps = 0
        self.display_fps = 0
        self.fps_list = []
        self.display_data = ""
        self.start_time = 0
        self.fps_min = 30
        self.fps_max = 60
        self.fps_timer = 0
        self.fps_timer_wait = 0.25

        self.game_speed = 1 # General actions can be called at 1/second.
        self.total = 0

        self.geom_set_dict= {"all":self.geom_all,
                            "complex":self.geom_complex,
                            "line":self.geom_line,
                            "skeleton":self.geom_skeleton,
                            "background":self.geom_none,
                            None:self.geom_none}
        self.act_set_dict = {"change_sprite":self.act_change_sprite,
                            "change_color":self.act_change_color,
                            "rotate":self.act_rotate,
                            "quit":self.act_quit,
                            "sound":self.act_sound,
                            "unlock":self.act_unlock,
                            "lock":self.act_lock,
                            "change_map":self.act_change_map,
                            "change_theme":self.act_change_theme,
                            "change_geometry":self.act_change_geom,
                            "message":self.act_display_msg,
                            "kill":self.act_kill,
                            "teleport":self.act_teleport,
                            "up_score":self.act_up_score}   
        self.key_dict = {"wasd":
                            {"w":self.move_up,"s":self.move_down,
                            "a":self.move_left,"d":self.move_right,
                            "e":self.run_interacts,"ctrl+r":self.reload_screen},
                        "dirs":
                            {"up arrow":self.move_up,"left arrow":self.move_left,
                            "down arrow":self.move_down,"right arrow":self.move_right,
                            ".":self.run_interacts}}

    def set_map_path(self,path,directed_path=False):
        self.map.set_path(path,directed_path)
    def set_sprite_path(self,path):
        """Take the sprite file path and store the sprites in
        the sprites dictionary. Interpret the sprites for
        parts that are empty."""
        path = DIRPATH + path
        name = None
        curr_sprite = []
        height = 0
        color_coded = False
        code_below = False
        color_code = [""]
        # Adds parent directory of running program
        with open(path, 'r',encoding='utf-8') as file:
            line = file.readline()[:-1] # Removes "\n".
            while(line):
                if line[0] == SKIP:
                    # Add the previous sprite to the sprites dictionary.
                    if name != None: # If this isn't the first img
                        if len(curr_sprite[0]) > self.max_sprite_width:
                            self.max_sprite_width = len(curr_sprite[0])
                        if height > self.max_sprite_height:
                            self.max_sprite_height = height
                        if color_coded:
                            if code_below: # The second half of the sprite is actually the color code
                                half_len = len(curr_sprite)//2
                                for row in range(half_len):
                                    colored_line = []
                                    for i in range(len(curr_sprite[0])):
                                        color = color_code[int(curr_sprite[half_len][i])]
                                        char = curr_sprite[row][i]
                                        colored_line.append(color + char)
                                    curr_sprite[row] = colored_line
                                    curr_sprite.pop(half_len)
                            else: # Each character has its color code before it. Difficult for artist to read.
                                true_len = len(curr_sprite[0])//2
                                # Assumes every line is the same length
                                for row in range(len(curr_sprite)):
                                    colors_only = []
                                    chars_only = []
                                    for half_i in range(true_len):
                                        color = color_code[int(curr_sprite[row][(half_i*2)])]
                                        char = curr_sprite[row][(half_i*2)+1]
                                        colors_only.append(color)
                                        chars_only.append(char)
                                    chars_only = replace_spaces(chars_only)
                                    colored_line = []
                                    for i in range(true_len):
                                        colored_line.append(colors_only[i] + chars_only[i])
                                    curr_sprite[row] = colored_line
                        self.sprites[name] = curr_sprite # If color coded and if not.
                        curr_sprite = []
                    skips = find_count(line,SKIP)
                    # if skips == 1: end of file (do nothing)
                    if skips == 2: # Regular Sprite
                        color_coded = False
                        name = line[1:-1] # Remove SKIPs
                        height = 0
                    elif skips >= 3: # Color-coded Sprite
                        #$sprite-name$color0,color1$
                        #0H1E0Y1 0T1H0E1R0E
                        color_coded = True
                        inds = find_indices(line,SKIP)
                        name = line[1:inds[1]]
                        code_below = False
                        if skips == 4:
                            if line[inds[2]+1:inds[3]] == "below":  code_below = True
                        colors_raw = line[inds[1]+1:inds[2]]
                        colors_raw = colors_raw.split(",")
                        color_code = [""]
                        for num in colors_raw:
                            color_code.append(color_by_num(int(num)))
                else: # Append to the current sprite image.
                    line = replace_spaces(line)
                    line = ms_gothic(line)
                    curr_sprite.append(list(line))
                    height +=1
                line = file.readline()[:-1] # Removes the \n
        self.set_sprites_in_objs()
        
    def set_sprites_in_objs(self):
        self.objs.sprites = self.sprites
        self.objs.max_sprite_height = self.max_sprite_height
        self.objs.max_sprite_width = self.max_sprite_width
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

    def init_map(self,first=True):
        """All that comes before the main game_loop"""
        if first:
            self.start_time = time()
            self.play_theme()
        print(CLEAR)
        self.init_objs()
        self.init_render_all()
        self.map.display_timer()
        self.map.print_all()

    def game_loop(self):
        """This is what loops for every game tick.
        It is run by the run_game method."""
        self.frame_start = time()
        self.move_all()
        self.render_all()
        self.map.display_timer()
        if self.fps <= self.fps_max:
            self.map.print_all()
        self.run_frame_counter()
    def game_loop_debug(self):
        self.frame_start = time()
        self.move_all()
        self.render_all()
        self.map.display_timer()
        self.map.print_all(self.display_data)
        self.run_frame_counter(True)

    def run_frame_counter(self,with_avg=False):
        self.tick = (self.tick + 1)%MAX_TICK
        if time() != self.frame_start:
            self.fps = round(1/(time()-self.frame_start),2)
            if with_avg:
                self.fps_list.append(self.fps)
            if time() >= self.fps_timer:
                self.fps_timer = time() + self.fps_timer_wait
                self.display_fps = self.fps
        else:
            self.fps = 999.00 # Cosmetic only.
        self.display_data = "FPS:" + str(self.display_fps) + " Map: " + self.map_name[self.map_name.rfind("/")+1:]

    def end_game(self):
        """All the comes after the main game_loop"""
        mixer.music.stop()
        self.play_sound("quit")
        fps_avg = str(sum(self.fps_list)/len(self.fps_list))
        end_game = CLEAR+SPACES+"Game Over!\nAverage FPS: "+fps_avg+"\n"
        input(f"{end_game}Press ENTER to exit.\n{DEFAULT_COLOR}") # Hide input from the whole game
        print(CLEAR)

    def play_theme(self):
        if len(self.themes)>0:
            mixer.music.load(self.themes[0])
            mixer.music.play(-1)
    def set_theme(self,path:str):
        assert len(path) > 4, "Not a valid audio file name."
        path = DIRPATH + path
        self.themes.insert(0,path)
    def add_sound(self, path:str,sound_name:str=""):
        assert len(path) > 4, "Not a valid audio file name."
        path = DIRPATH + path
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
        #id_tracker = set()
        end_y_range = self.map.end_camera_y + (WGC_Y*2)
        for obj in self.objs.objs:
            if obj.origy > end_y_range:
                break
            else:#if obj.origy > start_y_range and obj.origx > start_x_range and obj.origy < end_x_range:
                #id_tracker_len = len(id_tracker)
                #id_tracker.add(id(obj)) #Checks if we've looked at this object already
                if not obj.simple:# and len(id_tracker) != id_tracker_len:
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
        if is_pressed("p"):#pausing
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
            if self.map.width > self.map.end_camera_x < obj.origx + WGC_X + obj.width():
                move_x = 1
            elif self.map.camera_x + WGC_X > obj.origx and self.map.camera_x > 0:
                move_x = -1
        if "y" in self.camera_follow:
            if self.map.height > self.map.end_camera_y < obj.origy - obj.height() + WGC_Y:
                move_y = 1
            elif self.map.camera_y + WGC_Y > obj.origy - obj.height() and self.map.camera_y > 0:
                move_y = -1
        self.map.move_camera(move_x,move_y)
        coords = "("+str(obj.origx)+","+str(obj.origy)+")"
        self.display_data += coords
        # GAME-ENDING CHECKS:
        if obj.hp <= 0 or obj.origy == self.map.width -1:
            self.quit = True
            self.kill_obj(obj) 
    
    def kill_obj(self,obj,sound:bool=False): # DEATH
        if sound:
            self.play_sound("death")
        self.teleport_obj(obj,-1,-1)
        obj.geom = None
        obj.move = None
        self.set_sprite(obj,"dead")

    def get_texts(self,path):
        path = DIRPATH + path
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

    def run_interacts(self,obj):
        """This is run when a player's given interact button is pressed.
        Objects without geometry cannot be presently acted upon."""
        if time() - obj.move_time["i"] > 1/self.game_speed:
            obj.move_time["i"] = time()
            xs,xf,ys,yf = self.set_xy_limits(obj)
            for act in self.acts.acts:
                if not act.locked and act.kind == "interact":
                    if obj.char == act.char:
                        self.act_set_dict[act.effect](obj,act.arg) #act on oneself
                    else:
                        if obj.face_down:
                            if act.char in self.map.geom[yf][xs:xf]: #BELOW
                                i=self.objs.find_obj_index(obj)+1
                                found = False
                                while not found and i < len(self.objs.objs):
                                    i_obj = self.objs.objs[i]
                                    if act.char == i_obj.char and (i_obj.origy-i_obj.height()+1==yf or i_obj.origy==yf) and xs <= i_obj.origx+i_obj.width() and xf >= i_obj.origx:
                                        found = True
                                        self.act_set_dict[act.effect](i_obj,act.arg)
                                    else:
                                        i+=1
                        else:
                            if act.char in self.map.geom[ys-1][xs:xf]: #ABOVE
                                i=self.objs.find_obj_index(obj)-1
                                found = False
                                while not found and i > -1:
                                    i_obj = self.objs.objs[i]
                                    if act.char == i_obj.char and i_obj.origy == ys-1 and xs <= i_obj.origx+i_obj.width() and xf >= i_obj.origx:
                                        found = True
                                        self.act_set_dict[act.effect](i_obj,act.arg)
                                    else:
                                        i-=1
                        for y in range(ys,yf):
                            if obj.face_right:
                                if self.map.geom[y][xf] == act.char: #RIGHT
                                    i=self.objs.find_obj_index(obj)+1
                                    found = False
                                    while not found and i < len(self.objs.objs):
                                        i_obj = self.objs.objs[i]
                                        if act.char == i_obj.char and ys<=i_obj.origy<yf and xf <= i_obj.origx:
                                            found = True
                                            self.act_set_dict[act.effect](i_obj,act.arg)
                                        else:
                                            i+=1
                            else:
                                if self.map.geom[y][xs-1] == act.char: #LEFT
                                    i=self.objs.find_obj_index(obj)-1
                                    found = False
                                    while not found and i > -1:
                                        i_obj = self.objs.objs[i]
                                        if act.char == i_obj.char and ys<=i_obj.origy<yf and xs <= i_obj.origx+i_obj.width():
                                            found = True
                                            self.act_set_dict[act.effect](i_obj,act.arg)
                                        else:
                                            i-=1

    def reload_screen(self,obj=None):
        self.init_render_all()

    def set_xy_limits(self,obj):
        """Used in run_acts and run_interacts"""
        xs = obj.origx
        xf = min([xs+obj.width(),self.map.width-1])
        if obj.geom in ["all","complex"]:
            yf = min([obj.origy + 1,self.map.height-1])
            ys = yf - obj.height()
        else:
            ys = obj.origy
            yf = min([ys+1,self.map.height-1])
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
                    for char in self.map.geom[yf][xs:xf]:
                        bubble.add(char)
                    for char in self.map.geom[ys-1][xs:xf]:
                        bubble.add(char)
                    for y in range(ys,yf):
                        bubble.add(self.map.geom[y][xs-1])
                        bubble.add(self.map.geom[y][xf])
                    if act.arg[0] in bubble:
                        self.act_set_dict[act.effect](obj,act.arg)

    # These functions are put into act_set_dict, for quicker lookup than if statements.
    def act_change_sprite(self,obj,arg):
        """ARG: dictionary of old img key and new img value"""
        self.set_sprite(obj,arg[obj.img])
    def act_change_color(self,obj,arg):
        obj.set_color(arg[obj.color])
        self.set_sprite(obj,obj.img)
    def act_change_geom(self,obj,arg):
        obj.geom = arg[obj.geom]
        self.set_sprite(obj,obj.img)
    def act_change_theme(self,obj,arg):
        mixer.music.stop()
        self.set_theme(arg[-1])
        self.play_theme()
    def act_display_msg(self,obj,arg):
        arg = arg[-1]
        if arg == int(arg):
            try:msg = self.texts[arg]
            except IndexError:msg = ""
        else:msg = arg
        self.map.set_disp_msg(msg)
    def act_rotate(self,obj,arg):
        obj.rotate_right()
        self.objs.set_sprite(obj,obj.img)
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
        # ARG: name of action to unlock
        for targ_act in self.acts.acts:
            if targ_act.name == arg:
                targ_act.locked = False
    def act_lock(self,obj,arg):
        # ARG: name of action to lock
        for targ_act in self.acts.acts:
            if targ_act.name == arg:
                targ_act.locked = True
    def act_up_score(self,obj,arg=[1]):
        obj.score += arg[-1]
    def act_kill(self,obj,arg):
        """Make sure this is the last act of that object."""
        self.kill_obj(obj)
    def act_teleport(self,obj,arg):
        """Arg is a list of x,y coords"""
        self.teleport_obj(obj,arg[-2],arg[-1])
    def act_change_map(self,actor,arg:list):
        """ arg = [prev_x,prev_y,new_x,new_y,old_map,new_map] or
        arg = [old_map,new_map].
        Find the map in map_dict, or create it. Also centers camera
        on the actor object."""
        self.map.print_to_black()
        from_map_name = DIRPATH + arg[-2] # the map to leave
        if from_map_name == self.map.file_name: # if we are in the map to leave
            to_map_name = DIRPATH + arg[-1]
            # Remove actor from present map
            if len(arg)==6:
                self.objs.objs.pop(self.objs.find_obj_index(actor))
            if to_map_name in self.map_dict.keys(): # Is map created?
                self.map_name = to_map_name
                self.map = self.map_dict[to_map_name]
                self.objs = self.map.objs
            else: # Create new map and add it to the map list.
                self.create_new_map(to_map_name)
            if len(arg)==6: # Add actor to new map and center camera on them.
                actor.origx = arg[2]
                actor.origy = arg[3]
                self.map.center_camera(actor.origx,actor.origy)
                self.objs.append_obj_ordered(actor)
                self.add_to_render_objs(actor)
            self.set_sprites_in_objs()
            self.init_render_all()
    def create_new_map(self,path):
        """Creates the map from a given path, populating it with object sprites
        found in travel objects. Sets this new map to the game's current map."""
        for obj in self.objs.pallete_objs:
            self.universal_objs.add(obj) # Collect objects from the pallete
        self.map_dict[path] = Map(self.universal_objs)
        self.map_name = path
        self.map = self.map_dict[path]
        self.objs = self.map.objs
        self.set_sprites_in_objs()
        self.set_map_path(path,True)
        self.init_map(False)

    def take_dmg(self,obj,e_char):
        enemy = self.objs.obj_from_char(e_char)
        if self.should_take_dmg(obj,enemy,e_char):
            obj.hp -= enemy.dmg
    def should_take_dmg(self,obj,enemy,e_char):
        """ Check all sides of an object for enemy chars
        on the geom"""
        xs = obj.origx
        xf = xs+obj.width()
        ys = obj.origy - obj.height() + 1
        yf = ys+obj.height()
        try:
            if 'down' in enemy.dmg_dirs:
                if e_char in self.map.geom[ys-1][xs:xf]: #ABOVE
                    return True
            if 'up' in enemy.dmg_dirs:
                if e_char in self.map.geom[yf+1][xs:xf]: #BELOW
                    return True
            for y in range(ys,yf):
                if 'right' in enemy.dmg_dirs:
                    if self.map.geom[y][xs-1] == e_char: #LEFT
                        return True
                if 'left' in enemy.dmg_dirs:
                    if e_char in self.map.geom[y][xf] == e_char: #RIGHT
                        return True
        except: pass
        return False

    def set_default_color(self,color):
        self.map.background_color =color
        self.objs.default_color = color
    def teleport_obj(self,obj,x:int=0,y:int=0):
        """Moves an object to a given location if no geometry is there."""
        move_x = x - obj.origx
        move_y = y - obj.origy
        if x > obj.origx:
            move_x *= -1
        if y < obj.origy:
            move_y *= -1
        if self.can_move(obj,move_x,move_y):
            self.move_map_char(obj,move_x,move_y)
        if obj.move in ["wasd","dirs"]:
            self.map.center_camera(obj.origx+obj.width()//2,obj.origy-obj.height()//2)
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
                    if BLANK not in self.map.geom[y][x]:
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
        self.objs.append_obj_ordered(obj)

    def init_objs(self):
        """Create objects from the pallete and place them on coordinates
        as directed by the input map."""
        for obj_data in self.map.input_map:
            obj_x,obj_y,obj_char = obj_data[0],obj_data[1],obj_data[2]
            parent_obj = self.objs.obj_from_char(obj_char)
            new_obj = self.objs.copy(parent_obj,obj_x,obj_y)
            self.objs.init_obj(new_obj)
    
    # These functions are put into geom_set_dict, for quicker lookup than if statements.
    def geom_all(self,obj):
        [[self.map.set_xy_geom(x, y, obj.char) 
        for x in range(obj.origx, min([obj.origx + obj.width(), len(self.map.geom[y])]) )]
        for y in range(obj.origy - obj.height() +1,obj.origy +1)]
    def geom_complex(self,obj):
        # Based on all characters of a sprite that are not blank.
        [[self.map.set_xy_geom(x + obj.origx, obj.origy - y, obj.char) 
        for x in range( min([obj.width(), len(self.map.geom[y])-obj.origx]) ) 
        if SKIP not in obj.sprite[y][x]]
        for y in range(obj.height())]
    def geom_line(self,obj):
        [self.map.set_xy_geom(x + obj.origx, obj.origy, obj.char)
        for x in range( min([obj.width(), len(self.map.geom[-1])-obj.origx]) )]
    def geom_skeleton(self,obj):
        [self.map.set_xy_geom(x + obj.origx, obj.origy, obj.char)
        for x in range( min([obj.width(), len(self.map.geom[-1])-obj.origx]) )
        if SKIP not in obj.sprite[-1][x]]
    def geom_none(self,obj):
        pass

    def add_to_render_objs(self,obj):
        """Adds everything in the rows of a moved object into
        the updated objects list."""
        # Clear the render area the sprite is currently at.
        start_y = obj.origy-obj.height()+1
        for y in range(start_y,obj.origy+1):
            start_x = find_non(obj.sprite[y-start_y],SKIP) + obj.origx
            for x in range(start_x, min([obj.origx + obj.width(), self.map.width ])):
                char = obj.sprite[y-start_y][x-obj.origx]
                if SKIP not in char:
                    self.map.remove_xy_rend(x,y,char)
        self.remove_geom(obj)
        # Render the objects that the sprite area currently takes up.
        self.objs.render_objs.add(obj)
    
    def remove_geom(self,obj):
        for y in range(obj.origy-obj.height()+1,obj.origy+1):
            for x in range(obj.origx, min([obj.origx + obj.width(), self.map.width ])):
                if obj.char in self.map.get_xy_geom(x,y):
                    self.map.set_xy_geom(x,y,BLANK)
        
    def set_sprite(self,obj,new_img):
        self.add_to_render_objs(obj)
        self.objs.set_sprite(obj,new_img)
        self.geom_set_dict[obj.geom](obj)

    def flip_sprite(self,obj):
        assert obj.animate not in [None,"flip"], "This object is not animated."
        obj.face_right = not obj.face_right
        if obj.face_right:
            self.set_sprite(obj,obj.animate["d"])
        else:
            self.set_sprite(obj,obj.animate["a"])

    def init_render_all(self):
        self.map.init_rend()
        self.map.init_geom()
        for obj in self.objs.objs:
            self.render_obj_simple(obj)
            self.geom_set_dict[obj.geom](obj)
            # Geometry is all-in-all static, and otherwise
            # changed by object movement alone.
        self.objs.render_objs = set()
    def render_all(self):
        """This creates the output AND geometry
        maps out of all object sprites. NOT for initializing
        objects (not that you asked)."""
        end_range_y = self.map.end_camera_y + (WGC_Y*3)
        if len(self.objs.render_objs) > 0:
            for obj in self.objs.render_objs:
                if obj.origy >= end_range_y:
                    break
                self.render_obj(obj)
            self.objs.render_objs = set()
    def render_obj_simple(self,obj):
        start_y = obj.origy+1-obj.height()
        end_y = min([obj.origy+1,self.map.height-1])
        if obj.geom!="background":
            for y in range(start_y,end_y):
                start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.origx
                end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.origx+1,self.map.width])
                for x in range(start_x,end_x):
                    char = obj.sprite[y-start_y][x-obj.origx]
                    if SKIP not in char:
                        self.map.rend[y][x].append(char)
        else:
            for y in range(start_y,end_y):
                start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.origx
                end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.origx+1,self.map.width])
                for x in range(start_x,end_x):
                    char = obj.sprite[y-start_y][x-obj.origx]
                    if SKIP not in char:
                        self.map.rend[y][x][0] = char
    def render_obj(self,obj):
        start_y = obj.origy+1-obj.height()
        end_y = min([obj.origy+1,self.map.height-1])
        # Find all the objects that are in front of the character
        objs_ahead = self.find_objs_ahead(obj)
        for y in range(start_y,end_y):
            start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.origx
            end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.origx+1,self.map.width])
            # Don't attempt to print out of bounds
            for x in range(start_x,end_x):
                covered = False
                for bobj in objs_ahead:
                    back_x = x - bobj.origx
                    back_y = y - bobj.origy + bobj.height()
                    # Check if part of the bobj is at this coordinate
                    if -1 < back_x < bobj.width() and -1 < back_y < bobj.height():
                        covered = True
                char = obj.sprite[y-start_y][x-obj.origx]
                if SKIP not in char: # If this is not a blank character
                    if covered:
                        index = max([len(self.map.rend[y][x])-1,1])
                        self.map.rend[y][x].insert(index,char)
                    else:
                        self.map.rend[y][x].append(char)
    def find_objs_ahead(self,obj):
        objs_ahead = set()
        i = self.objs.find_obj_index(obj)
        bobj = self.objs.objs[i]
        while bobj.origy - bobj.height() < obj.origy + (obj.height()*2) and i < len(self.objs.objs)-1:
            i+=1
            bobj = self.objs.objs[i]
            if bobj.origx + bobj.width() > obj.origx:
                if bobj.origx < obj.origx + obj.width():
                    if bobj.geom != "background":
                        objs_ahead.add(bobj)
        return objs_ahead

    def render_obj_old(self,obj):
        """Print a sprite at its object's origin."""
        start_y = obj.origy+1-obj.height()
        end_y = min([obj.origy+1,self.map.height-1])
        start_x = find_non(obj.sprite[-1],SKIP) + obj.origx
        if obj.geom!="background":
            thing_behind = False
            thing_ahead = False
            for x in range(start_x,start_x+obj.width()):
                if len(self.map.rend[end_y-2][x]) > 1:
                    thing_behind = True
                    # If the row above the baseline of an object has a thickness greater than one, something is behind the object.
                if len(self.map.rend[end_y][x]) > 1:
                    thing_ahead = True
                if len(self.map.rend[end_y-1][x]) > 1:
                    thing_ahead = True
                    # If the row below the baseline of an object has a thickness greater than one, something is in front.
                """If something is ahead and behind, we will insert under the top layer. When there are just two layers and until we hit three or one, we will append.
                If nothing is ahead, we will always append. Same if nothing is behind.
                """
            if not thing_ahead:
                for y in range(start_y,end_y):
                    start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.origx
                    end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.origx,self.map.width-1])+1
                    for x in range(start_x,end_x):
                        char = obj.sprite[y-start_y][x-obj.origx]
                        if SKIP not in char:
                            self.map.rend[y][x].append(char)
            else:
                obj_ahead_found = thing_behind
                for y in range(start_y,end_y):
                    start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.origx
                    end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.origx,self.map.width-1])+1
                    # Don't attempt to print out of bounds
                    for x in range(start_x,end_x):
                        char = obj.sprite[y-start_y][x-obj.origx]
                        layers = len(self.map.rend[y][x])
                        if layers == 3 or layers == 1:
                            obj_ahead_found = True
                        if SKIP not in char: # If this is not a blank character
                            if layers > 1 and obj_ahead_found:
                                    self.map.rend[y][x].insert(-1,char)
                            else:
                                self.map.rend[y][x].append(char)
        else: # Add to background. Working!
            for y in range(start_y,end_y):
                start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.origx
                end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.origx,self.map.width-1])+1
                for x in range(start_x,end_x):
                    char = obj.sprite[y-start_y][x-obj.origx]
                    if SKIP not in char: # If this is not a blank character
                        if self.map.rend[y][x][0] == BLANK:
                            self.map.rend[y][x][0] = char

        # Add any text above the object sprite
        # Only works on static objects thus far.
        """if obj.txt > -1:
            txt = self.texts[obj.txt]
            out_y = obj.origy - obj.height() - 1
            out_x = obj.origx + (obj.width())//2 - len(txt)//2
            [self.map.set_xy_rend(out_x+i,out_y,-1,txt[i]) for i in range(len(txt))]"""

class Map():
    """Three arrays are stored in a Map object: the wasd input 
    map, the output map, and a geom map.
    Set the map path upon initialization"""
    def __init__(self,universal_objs=set()):
        self.file_name = ""
        self.background_color = DEFAULT_COLOR

        self.input_map = list() # Made to store user-made map. 1D list of strings.
        self.rend = [] # Map of what will be rendered. 3-Dimensional.
        self.geom = [] # For checking collision.
        self.print_map = ""

        self.objs = Objs(universal_objs)

        self.height = W_HEI
        self.width = W_WID
        self.camera_x = 0
        self.camera_y = 0 # start_window_y
        self.end_camera_y = W_HEI
        self.end_camera_x = W_WID
            # These are the map coordinates of the 
            # top-left-most char shown in the window.
            
        self.disp_msg = ""
        self.msg_timer = 0

    def set_path(self,path,directed_path=False):
        """ Stores characters and their coords in the input map,
        using a preset path. Also sets self.width and self.height. """
        if not directed_path:
            path = DIRPATH + path
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
                    char = line[x]
                    if char != BLANK:
                        self.input_map.append([x,y,char])
                y += 1
                line = file.readline()
        self.height = y
        self.width = maxwidth
        self.init_rend()
        self.init_geom()

    def set_disp_msg(self,new_msg):
        self.msg_timer = time() + len(new_msg)/15
        self.disp_msg =[[self.background_color+BUBBLE[0][0]],
                        [self.background_color+BUBBLE[1][0]],
                        [self.background_color+BUBBLE[2][0]]]
        new_msg = BLANK + new_msg + BLANK
        for c in new_msg:
            self.disp_msg[0].append(BUBBLE[0][1])
            self.disp_msg[1].append(c)
            self.disp_msg[2].append(BUBBLE[2][1])
        self.disp_msg[0].append(BUBBLE[0][2])
        self.disp_msg[1].append(BUBBLE[1][0])
        self.disp_msg[2].append(BUBBLE[2][2])

    def init_geom(self):
        """ Create geom map of size self.width by self.height."""
        if len(self.geom) == 0: # If the map is new.
            [self.geom.append(list(BLANK * self.width)) for y in range(self.height)]
        else:self.clear_geom()
    def clear_geom(self):
        for y in range(self.height):
            self.geom[y] = (list(BLANK * self.width))
    def init_rend(self):
        if len(self.rend) == 0: # If the map is new.
            for y in range(self.height):
                new_row = []
                for x in range(self.width):
                    new_item = [[BLANK]] # z-levels start at 1
                    new_row.append(new_item)
                self.rend.append(new_row)
        else:self.clear_rend()
    def clear_rend(self):
        for y in range(self.height):
            for x in range(self.width):
                self.rend[y][x] = list(BLANK) # Remove all other z-levels

    def print_all(self,data=""):
        """Displays the proper area of self.rend."""
        self.line = [self.background_color]
        [self.p2([self.p1(self.rend[row][x][-1]) for x in range(self.camera_x,self.end_camera_x)]) for row in range(self.camera_y,self.end_camera_y)]
        self.add_message()
        self.add_data(data)
        self.line.pop(-1)#An extra \n needed removing.
        self.print_map = RETURN + "".join(self.line)
        print(self.print_map)
    def print_to_black(self):
        """Clears the screen line by line. Moves
        theme volume from 0 to 100%."""
        print(RETURN,end="")
        volume = 0
        for line in range(W_HEI):
            print(S_LINE)
            mixer.music.set_volume(volume)
            sleep(.03)
            volume += 1/W_HEI
        mixer.music.set_volume(1)
    def p1(self,char):
        self.line.append(char)
    def p2(self,line):
        self.line.append(self.background_color+"\n")
    def add_message(self):
        if len(self.disp_msg) > 0:
            start = int(len(self.line)*((W_HEI-len(self.disp_msg)+.5)/W_HEI))
            row_down = int(len(self.line)*(1/W_HEI))
            half_msg_len = len(self.disp_msg[0])//2-1
            i = start
            for row in self.disp_msg:
                for c in row:
                    self.line[i-half_msg_len]=str(c)
                    i += 1
                start += row_down
                i = start
    def display_timer(self):
        if len(self.disp_msg) > 0:
            if self.msg_timer < time():
                self.disp_msg = ""
    def add_data(self,data):
        if len(data) > 0:
            i = int(len(self.line)*((W_HEI-1)/W_HEI))+1
            for c in data:
                try:self.line[i]=c
                except:pass
                i +=1
        
    def set_xy_geom(self,x,y,char):
        """Sets char at a given position on map"""
        self.geom[y][x] = char
    def get_xy_geom(self,x,y):
        """Returns what character is at this position."""
        return self.geom[y][x]
    def set_xy_rend(self,x,y,z,char):
        """Sets char at a given position on map"""
        if self.rend[y][x][z] == BLANK:
            self.rend[y][x][z] = char
        else:
            self.rend[y][x].append(char)
    def remove_xy_rend(self,x,y,char):
        if len(self.rend[y][x]) > 1:
            for z in range(len(self.rend[y][x])):
                if self.rend[y][x][z] == char:
                    self.rend[y][x].pop(z)
                    break
        elif self.rend[y][x][0] == char: # Only one layer.
            self.rend[y][x][0] = BLANK
            
    def get_xy_rend(self,x,y,z=-1):
        return self.rend[y][x][z]

    def move_camera(self,x=0,y=0):
        self.camera_x += x
        self.camera_y += y
        self.end_camera_y += y
        self.end_camera_x += x
    def center_camera(self,x,y):
        """Takes a coordinate and centers the camera on that point."""
        half_wid = W_WID//2
        half_hei = W_HEI//2
        if x + half_wid >= self.width:
            x = self.width - half_wid -1
        elif x - half_wid < 0:
            x = half_wid
        if y + half_hei >= self.height:
            y = self.height - half_hei -1
        elif y - half_hei < 0:
            y = half_hei
        self.camera_x = x - half_wid
        self.camera_y = y - half_hei
        self.end_camera_x = self.camera_x + W_WID
        self.end_camera_y = self.camera_y + W_HEI

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
    def __init__(self,universal_objs=set()):
        self.inventory = []
        self.objs = [] # must be drawn from pallete_objs
        self.render_objs = set() #These objects need to be updated exactly
        #once per frame, thus the set. 
        self.pallete_objs = universal_objs # These are all the original objects.
        self.sprites = dict()
        self.max_sprite_height= 1
        self.max_sprite_width = 1
        self.default_color = DEFAULT_COLOR
    
    def set_sprite_color(self,obj):
        chars = [SKIP]
        if obj.geom == "skeleton":
            chars.append(BLANK)
        for y in range(obj.height()):
            for x in range(obj.width()):
                char = obj.sprite[y][x]
                if chars[0] not in char and chars[-1] not in char:
                    char = obj.color + char # This is not an empty character (BLANK or SKIP)
                else:
                    char = SKIP # Turn BLANKS into SKIPS, so no BLANKS need to be skipped.
                if x != obj.width() -1:
                    if obj.sprite[y][x+1] == chars[-1] or obj.sprite[y][x+1] == chars[0]:
                        char = char + self.default_color
                obj.sprite[y][x] = char
            obj.sprite[y][-1] = char + self.default_color
    def set_sprite(self,obj,new_img):
        obj.img = new_img
        obj.sprite = []
        for row in self.sprites[obj.img]:
            obj.sprite.append(list(row)) # Make a list copy
        self.set_sprite_color(obj)
        obj.rotate = 0
    def get_flipped_sprite(self,sprite,obj=None):
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
        if obj is not None:
            self.set_sprite_color(obj)
        return new_sprite

    def obj_from_char(self,char):
        """Takes a character and finds the corresponding
        pallete object as created by the user."""
        for obj in self.pallete_objs:
            if char in obj.char or char == obj.char:
                return obj
        assert False, "This char is not found in the pallete."
    def find_obj_index(self,obj):
        """Looks for an object within objs by id. Returns -1
        if not found."""
        i=0
        while i < len(self.objs):
            currid = id(self.objs[i])
            if id(obj) == currid:
                return i
            i+= 1
        return -1
    def append_obj_ordered(self,obj):
        """This is for a ready-made object who must be placed in the right spot
        within the objs list."""
        i = 0
        placed = False
        while i < len(self.objs) and not placed:
            next_obj = self.objs[i]
            if (next_obj.origy > obj.origy) or (next_obj.origy == obj.origy and next_obj.origx >= obj.origx):
                placed = True
            else:
                i+=1
        self.objs.insert(i,obj)
    def init_obj(self,obj,rotate=0):
        while rotate != obj.rotate:
            obj.rotate_right()
        self.set_sprite(obj,obj.img)
        if obj.animate == "flip":
            original = obj.img
            flip_img = reversed(obj.img)
            self.sprites[flip_img] = self.get_flipped_sprite(self.sprites[obj.img],obj)
            obj.animate = {"w":obj.img,"a":flip_img,"s":obj.img,"d":original}
        elif obj.animate == None:
            obj.animate = {"w":obj.img,"a":obj.img,"s":obj.img,"d":obj.img}
        elif obj.animate == "sneaky":
            # This takes the object img name and assumes it to be facing right
            # and to be the reverse of facing left.
            # It looks for the object image with "-w" and "-s" added at the end
            assert (obj.img + "-w") in self.sprites.keys(), "img_name-w required."
            assert (obj.img + "-s") in self.sprites.keys(), "img_name-s required."
            facing_up = obj.img + "-w"
            facing_down = obj.img + "-s"
            facing_left = obj.img + "-a"
            self.sprites[facing_left] = self.get_flipped_sprite(self.sprites[obj.img],obj)
            obj.animate = {"w":facing_up,"a":facing_left,"s":facing_down,"d":obj.img}
        obj.i = len(self.objs)
        self.objs.append(obj)
    def add_to_pallete(self,obj):
        obj_clone = self.copy(obj) #reset coords
        self.pallete_objs.add(obj_clone)
    def new(self,img, char, x=-1,y=-1, geom = "all",
    move = None, xspeed = 1, yspeed = 1, hp =1,face_right=True,
    face_down=False, grav=False,dmg = 1, enemy_chars=[],
    dmg_dirs=[], set_rotate=0, animate=None,txt=-1,max_jump=1,
    color=None,data=dict()):
        """Creates an Obj and appends it to the objs list. This should
        only be called by the module-user (you)."""
        if color == None:
            color = self.default_color
        obj = self.Obj(img, char, x,y, geom, move,xspeed,yspeed,
            hp,face_right,face_down,grav,dmg,enemy_chars,dmg_dirs,
            animate,txt,max_jump,color,data)
        #self.append_obj(obj,set_rotate)
        self.add_to_pallete(obj)

    def copy(self,obji,newx=-1,newy=-1):
        """Returns a duplicate of an object."""
        if type(obji) == type(int()):
            o = self.objs[obji]
        else: # An object was given, not an index
            o = obji
        obj = self.Obj(o.img, o.char, newx,newy, o.geom, o.move, o.xspeed, o.yspeed,
            o.hp, o.face_right, o.face_down, o.grav, o.dmg, o.enemy_chars, o.dmg_dirs,
            o.animate,o.txt,o.max_jump,o.color,o.data)
        return obj

    class Obj():
        def __init__(self,img, char, x=-1,y=-1, geom = "all",
        move = None, xspeed = 1,yspeed = 1,hp =1,face_right=True,
        face_down=False,grav:bool=False,dmg = 1,enemy_chars=[],dmg_dirs=[],
        animate=None,txt:int=-1,max_jump=1,color=DEFAULT_COLOR,data=dict()):
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
            self.geom = geom # Options of: None, line, complex, skeleton, background, or all.
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
            self.color = self.set_color(color)
            # "flip" is default, mirrors the image for every change between right and left.
            # Otherwise, if it's not None it becomes a dictionary: {w,a,s,d:sprite images.}            
            self.txt = txt # line number from textsheet
            self.face_right = face_right # Left: False, Right: True
            self.face_down = face_down # Up: False, Down: True
            self.sprite = [] # Must be set through Objs function new().
            self.rotate = 0 # 0 through 3
            self.score = 0
            self.data = data

        def set_color(self,color):
            if type(color) == type(42):
                self.color = color_by_num(color)
            else:
                self.color = color # The literal escape code, not the number.
            return self.color

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

def find_non(string,bad_c):
    """Returns the index of the first non-case of a character in a
    string. Returns 0 if not found"""
    for c in range(len(string)):
        if string[c]!=bad_c:
            return c
    return 0
def rfind_non(string,bad_c):
    """Starting from the end of a string, this returns the index of
    the first non-case of a character in a string. Returns 0 if not found"""
    for c in range(len(string)-1,-1,-1):
        if string[c]!=bad_c:
            return c
    return len(string)-1
def find_count(string,character):
    """Finds the number of times a given character occurs in a string."""
    count = 0
    for c in string:
        if c == character:
            count += 1
    return count
def find_indices(string,character):
    """Returns a list of indices of the occurrences of a given character in a string."""
    indices = list()
    i = 0
    for c in string:
        if c == character:
            indices.append(i)
        i+=1
    return indices

def ms_gothic(line:str):
    line_dict = {'\\':'╲','│':'|','/':'╱'}
    line = [x for x in line]
    for x in range(len(line)):
        if line[x] in line_dict.keys():
            line[x] = line_dict[line[x]]
    return "".join(line)
def replace_spaces(line:str):
    """All spaces before and after other characters are replaced
    by the constant SKIP."""
    s1,s2 = True,True
    start,end = "",""
    for x in range((len(line)+1)//2):
        char = line[x]
        if char != BLANK or not s1: s1 = False
        else:   char = SKIP
        start = start + char

        char = line[len(line)-x-1]
        if char != BLANK or not s2: s2 = False
        else:   char = SKIP
        end = char + end
    if len(line)%2==0:
        return start + end
    else:
        return start[:-1] + end