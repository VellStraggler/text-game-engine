###################################
#                                 #
#      Textoon Game Engine        #
#    Created by: David Wells      #
#          Version 1.0            #
#                                 #
###################################
from keyboard import is_pressed,wait
from os.path import dirname
from os import system
from random import randint
from time import time,sleep
from math import log
from pygame import mixer
CLEAR = "\033[2J"
print(CLEAR) # erase pygame's message.
system("") # Allow the terminal to understand escape codes

DIRPATH = dirname(__file__) + "/"

BLANK = ' '
SKIP = '$'
CUR = '\033[A\033[F'
MAX_TICK = 16
ANIMATE_FPS = 1/8
CHUNK_WID = 32
CHUNK_HEI = 16

WINDOW_WID = 120#60 for baby screen with 250 fps, 189 for fullscreen (and 30 fps)
WINDOW_HEI = 29 #49 for fullscreen
# Based on the Windows Terminal window at default size.
INFO_HEI=2
RETURN = CUR * (WINDOW_HEI+INFO_HEI)
WINDOW_CUSHION_X = WINDOW_WID//2 - 5 
WINDOW_CUSHION_Y = WINDOW_HEI//2 
# WINDOW GUIDE CUSHION, the breathing room between the sprite between
# the window follows and the edge of the window.

SPACES = ' ' * 50
S_LINE = ' ' * WINDOW_WID
BUBBLE = [["╱","⎺","╲"],["|"],["╲","_","╱"]]
# /⎺⎺⎺⎺⎺⎺⎺\
#| message |
# \_______/

# Dictionary of chars (keys) and their opposites (values)
FLIP_CHARS = {'\\':'/','/':'\\','[':']',']':'[','{':'}','}':'{','<':'>',
    '>':'<','(':')',')':'(','◐':'◑','◑':'◐','↙':'↘','↘':'↙','כ':'c',
    'c':'כ','◭':'◮','◮':'◭','╱':'╲','╲':'╱','↖':'↗','↗':'↖','⌋':'⌊',
    '⌊':'⌋'}
H_FLIP_CHARS = {'\\':'/','/':'\\','↙':'↖','↘':'↗','כ':'c',
    'c':'כ','◭':'◮','◮':'◭','╱':'╲','╲':'╱','↖':'↙','↗':'↘',"_":"⎺",
    "⎺":"_","'":".",".":"'","A":"V","V":"A","M":"W","W":"M"}

COLOR_ESC = "\033[48;5;"
DEFAULT_COLOR = COLOR_ESC + "16m"
DEFAULT_TEXT  = "\033[38;5;15m"
def ex_func(obj,arg):
    pass
class Game():
    """
    Creates an empty map and empty sprite list.
    Fill these using map.set_path(path) and objs.set_path(path).
    """
    def __init__(self):
        self.map_dict = {"default":Map()}
        self.map_name = "default"
        self.map = self.map_dict[self.map_name]
        # A pointer to the current map being displayed.
        self.objs = self.map.objs
        self.acts = Acts()
        self.sprites = {"dead":[[" "]]}
        geometry = self.objs.Obj("dead","g",geom="all") # invisible geometry: g
        self.the_dead = set()
        self.mirs = Mirrors()
        self.objs.pallete_objs.add(geometry)
        self.universal_objs = set()
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
        self.disp_data = ""
        self.start_time = 0
        self.fps_max = 60
        self.fps_timer = 0
        self.fps_timer_wait = 0.25
        self.general_action_time = 0
        self.game_speed = 1 # General action calling per second.
        self.total = 0

        self.geom_set_dict= {"all":self.geom_all,
                            "complex":self.geom_complex,
                            "line":self.geom_line,
                            "skeleton":self.geom_skeleton,
                            "background":self.geom_none,
                            None:self.geom_none}
        self.key_dict = {"wasd":
                            {"w":self.move_up,"s":self.move_down,
                            "a":self.move_left,"d":self.move_right,
                            "e":self.run_interacts},
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
        path = solidify_path(path)
        name = None
        curr_sprite = []
        height = 0
        color_coded = False
        where_coded = False
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
                            if where_coded: # The second half of the sprite is actually the color code
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
                        #1H0E1Y0 1T0H1E0R1E
                        color_coded = True
                        inds = find_indices(line,SKIP)
                        name = line[1:inds[1]]
                        where_coded = False
                        if skips == 4:
                            if line[inds[2]+1:inds[3]] == "below":  where_coded = True
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
    def flip_sprite(self,obj):
        assert obj.animate not in [None,"flip"], "This object is not animated."
        obj.face_right = not obj.face_right
        if obj.face_right:
            img = obj.animate["d"]
        else:
            img = obj.animate["a"]
        self.objs.set_img(obj,img)
    def reflect_on_object(self,obj):
        """Take a shiny object and get the text from the map
        that it will reflect."""
        pass

    def run_game(self,debug=True):
        """Combine the map and the objs and begin the main game loop."""
        self.init_map()
        if debug:
            while(not self.quit):
                self.game_loop_debug()
        else:
            while(not self.quit):
                self.game_loop()
        self.end_game()

    def init_map(self,first=True):
        """All that comes before the main game_loop"""
        if first:
            self.start_time = time()
            self.play_theme()
        self.init_objs()
        self.init_render_all()
        self.map.display_timer()
        self.map.print_all()
    def init_objs(self):
        """Create objects from the pallete and place them on coordinates
        as directed by the input map."""
        for obj_data in self.map.input_map:
            x,y,char = obj_data[0],obj_data[1],obj_data[2]
            parent_obj = self.objs.obj_from_char(char)
            new_obj = self.objs.copy(parent_obj,x,y)
            self.objs.init_obj(new_obj)

    def game_loop(self):
        """This is what loops for every game tick.
        It is run by the run_game method."""
        self.frame_start = time()
        self.set_all_movement()
        self.render_all()
        self.map.display_timer()
        self.map.print_all()
        self.run_frame_counter()
    def game_loop_debug(self):
        self.frame_start = time()
        self.set_all_movement()
        self.render_all()
        self.map.display_timer()
        self.map.print_all(self.disp_data)
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
        self.disp_data = "FPS:" + str(self.display_fps)
        self.disp_data +=" Map: " + deconstruct_path(self.map_name)

    def end_game(self):
        """All the comes after the main game_loop"""
        mixer.music.stop()
        self.play_sound("quit")
        end_game = CLEAR+SPACES+"Game Over!\n"
        if len(self.fps_list) > 0:
            fps_avg = str(sum(self.fps_list)/len(self.fps_list))
            end_game += "Average FPS: "+fps_avg+"\n"
        input(f"{end_game}Press ENTER to exit.\n{DEFAULT_COLOR}") # Hide input from the whole game
        print(CLEAR)

    def get_texts(self,path):
        path = solidify_path(path)
        with open(path, 'r',encoding='utf-8') as file:
            line = file.readline()[:-1]
            while(line):
                self.texts.append(line)
                line = file.readline()[:-1]

    # SOUNDS #
    def play_theme(self):
        if len(self.themes)>0:
            mixer.music.load(self.themes[0])
            mixer.music.play(-1)
    def set_theme(self,path:str):
        path = solidify_path(path,".wav")
        self.themes.insert(0,path)
    def add_sound(self, path:str,sound_name:str=""):
        path = solidify_path(path,".wav")
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

    def set_all_movement(self):
        """ Set the movement of every mobile object found in the chunks
        shown in the camera window."""
        self.general_actions()
        self.set_load_chunks()
        self.remove_the_dead()
        for chunk in self.objs.load_chunks:
            for line in chunk.values():
                for obj in line:
                    if not obj.static:
                        # ANIMATION
                        if len(obj.animation)>1:
                            if time() > obj.frame_time:
                                obj.frame_time = time() + obj.framerate
                                self.next_frame(obj)
                        self.get_objs_touching(obj)
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
                        # ALL THAT SHOULD FALL WILL FALL
                        if obj.grav:
                            if time() - obj.move_time["w"] > 3/obj.yspeed:
                                obj.jump = 0
                                # If they haven't moved up in awhile
                            if time() - obj.move_time["g"] > 1/obj.yspeed:
                                if obj.jump > 0:
                                    obj.jump -= 1
                                obj.move_time["g"] = time()
                                if obj.jump == 0:
                                    self.set_movement(obj,0,1)
                        # DAMAGE-TAKING
                        self.take_dmg(obj)
                    if obj.hp <= 0 or obj.y == self.map.height -1: # All non-player mobs, DEATH.
                        if obj.move in ["wasd","dirs"]:
                            self.quit = True
                        self.kill_obj(obj,True)

    def set_load_chunks(self):
        """ Finds the chunks to be shown by the window and returns them."""
        start_x = self.map.camera_x//CHUNK_WID
        end_x = self.map.end_camera_x//CHUNK_WID + 1
        start_y = self.map.camera_y//CHUNK_HEI
        end_y = self.map.end_camera_y//CHUNK_HEI + 1
        self.objs.load_chunks = []
        for y in range(start_y,end_y):
            for x in range(start_x,end_x):
                chunk = self.objs.find_obj_chunk(x,y,True)
                self.objs.load_chunks.append(chunk)

    def general_actions(self):
        if self.general_action_time < time():
            if is_pressed("p"):# PAUSE
                self.general_action_time = time() + self.game_speed
                mixer.music.set_volume(.25)
                wait("p")
                sleep(.5)
                mixer.music.set_volume(1)
            elif is_pressed("q"):# QUIT
                self.quit = True
            elif is_pressed("ctrl+r"):
                self.init_render_all()# RELOAD SCREEN
            elif is_pressed("ctrl+g"):
                self.general_action_time = time() + self.game_speed
                self.map.color_on = not self.map.color_on
    def next_frame(self,obj):
        self.objs.set_img(obj,obj.animation[obj.frame])
        obj.frame += 1
        if obj.frame == len(obj.animation):
            obj.animation = [obj.img]
    def player_actions(self,player):
        # PLAYER MOVEMENT:
        for key in self.key_dict[player.move].keys():
            if is_pressed(key):
                self.key_dict[player.move][key](player)
        self.run_acts(player)
        self.map.camera_star = player # UPDATE: Only needs to be done once.
        coords = "("+str(player.x)+","+str(player.y)+")"
        self.disp_data += coords
    
    def get_objs_touching(self,obj):
        xs,xf,ys,yf = self.get_xy_range(obj)
        obj.init_touching()
        chunks = [self.objs.find_obj_chunk(obj.x,obj.y)]
        if (obj.y+(obj.width()//2))%CHUNK_HEI > CHUNK_HEI//2:
            chunks.append(self.objs.find_obj_chunk(obj.x+CHUNK_WID,obj.y)) #chunk right
        else:
            chunks.append(self.objs.find_obj_chunk(obj.x-CHUNK_WID,obj.y)) #chunk left
        for chunk in chunks:
            line_above = self.objs.find_obj_chunk(obj.x,ys)[ys%CHUNK_HEI]
            line = chunk[obj.y%CHUNK_HEI]
            line_below = self.objs.find_obj_chunk(obj.x,yf)[yf%CHUNK_HEI]
            for tobj in line_above:
                if xs < tobj.x + tobj.width() and xf > tobj.x:
                    obj.touching["up"].add(tobj)
            for tobj in line_below:
                if xs < tobj.x + tobj.width() and xf > tobj.x:
                    obj.touching["down"].add(tobj)
            for tobj in line:
                if xs < tobj.x + tobj.width() and xf > tobj.x:
                    obj.touching["inside"].add(tobj)
                elif tobj.x == xf:
                        obj.touching["right"].add(tobj)
                elif tobj.x + tobj.width() -1 == xs:
                    obj.touching["left"].add(tobj)
        return xs,xf,ys,yf


    # Synonymous functions
    def move_left(self,obj):
        self.objs.set_img(obj,obj.animate["a"])
        obj.face_right = False
        if time() - obj.move_time["a"] > 1/obj.xspeed:
            obj.move_time["a"] = time()
            self.set_movement(obj,-1)
    def move_right(self,obj):
        self.objs.set_img(obj,obj.animate["d"])
        obj.face_right = True
        if time() - obj.move_time["d"] > 1/obj.xspeed:
            obj.move_time["d"] = time()
            self.set_movement(obj,1)
    def move_down(self,obj):
        self.objs.set_img(obj,obj.animate["s"])
        obj.face_down = True
        if time() - obj.move_time["s"] > 1/obj.yspeed:
            obj.move_time["s"] = time()
            if obj.grav:
                obj.jump = 0
            self.set_movement(obj,0,1)
    def move_up(self,obj):
        self.objs.set_img(obj,obj.animate["w"])
        obj.face_down = False
        if time() - obj.move_time["w"] > 1/obj.yspeed:
            obj.move_time["w"] = time()
            if not obj.grav:
                self.set_movement(obj,0,-1)
            elif not self.can_move(obj,0,1): # If on top of something.
                obj.jump = obj.max_jump
                self.set_movement(obj,0,-1)
                self.play_sound("jump")
            elif obj.jump > 0:
                self.set_movement(obj,0,-1)
    
    def kill_obj(self,obj,sound:bool=False): # DEATH
        self.objs.set_img(obj,"dead")
        self.remove_geom(obj)
        obj.geom=None
        self.the_dead.add(obj)
        if sound:
            self.play_sound("death")

    def run_interacts(self,obj):
        """This is run when a player's given interact button is pressed.
        Objects without geometry cannot be presently acted upon."""
        if time() - obj.move_time["i"] > self.game_speed:
            obj.move_time["i"] = time()
            for act in self.acts.acts:
                if not act.locked and act.type == "interact":
                    if obj.char != act.item_char:
                        if obj.face_down:
                            for tobj in obj.touching["down"]:
                                self.run_act_on_target_obj(obj,tobj,act)
                        else:
                            for tobj in obj.touching["up"]:
                                self.run_act_on_target_obj(obj,tobj,act)
                        if obj.face_right:
                            for tobj in obj.touching["right"]:
                                self.run_act_on_target_obj(obj,tobj,act)
                        else:
                            for tobj in obj.touching["left"]:
                                self.run_act_on_target_obj(obj,tobj,act)
                        for tobj in obj.touching["inside"]:
                            self.run_act_on_target_obj(obj,tobj,act)
                    else:
                        act.func(obj,act.arg) #interact with oneself (inventory?)
    def run_act_on_target_obj(self,obj,tobj,act):
        if tobj.char == act.item_char:
            if act.act_on_self:
                act.func(obj,act.arg)
            else:
                act.func(tobj,act.arg)

    def run_acts(self,obj):
        """ Check all sides of an object for objects
        that can be interacted with."""
        xs,xf,ys,yf = self.get_xy_range(obj)
        for act in self.acts.acts:
            if not act.locked: 
                if act.type == "location":
                    # ARG: LOCATION TO REACH, [X,Y] FORM
                    # To focus only on a certain x or y, set the other to -1.
                    if act.map == self.map_name:
                        if ys <= act.loc_arg[1] < yf or act.loc_arg[1] == -1:
                            if xs <= act.loc_arg[0] < xf or act.loc_arg[0] == -1:
                                act.func(obj,act.arg)
                elif act.type == "touch":
                    for direction in obj.touching.values():
                        for tobj in direction:
                            if act.item_char == tobj.char:
                                act.func(obj,act.arg)

    def get_xy_range(self,obj):
        """Finds the range around an object"""
        xs = obj.x - 1
        xf = obj.x + obj.width()
        yf = obj.y + 1
        if obj.geom in ["all","complex"]:
            ys = yf - obj.height()
        else:
            ys = obj.y - 1
        return xs,xf,ys,yf

    # These functions are put into act_set_dict, for quicker lookup than if statements.
    def act_change_sprite(self,obj,arg):
        """ARG: dictionary of old img key and new img value"""
        self.objs.set_img(obj,arg[obj.img])
    def act_animate(self,obj,arg):
        """ARG: list of frames. Default frame time of 1 fps."""
        obj.frame = 0
        self.objs.set_img(obj,arg[obj.frame])
        obj.animation = arg
    def act_change_color(self,obj,arg:dict):
        obj.set_color(arg[obj.color])
        self.objs.set_img(obj,obj.img)
    def act_change_geom(self,obj,arg:dict):
        obj.geom = arg[obj.geom]
        self.objs.set_img(obj,obj.img)
    def act_change_theme(self,obj,arg:str):
        mixer.music.stop()
        self.set_theme(arg)
        self.play_theme()
    def act_message(self,obj,arg):
        if arg == int(arg):
            try:msg = self.texts[arg]
            except IndexError:msg = ""
        else:msg = arg
        self.map.set_disp_msg(msg)
    def act_rotate(self,obj,arg:int):
        for i in range(arg):
            obj.rotate_right()
            self.objs.set_sprite(obj,obj.img)
            obj.animate = {"w":obj.img,"a":obj.img,"s":obj.img,"d":obj.img}
    def act_quit(self,obj,arg):
        self.quit = True
    def act_sound(self,obj,arg:str):
        # ARG: sound path
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
    def act_kill(self,obj,arg=0):
        obj.hp = arg
    def act_teleport(self,obj,arg):
        """Arg is a list of x,y coords"""
        self.teleport_obj(obj,arg[0],arg[1])
    def act_change_map(self,actor,arg:list):
        """ arg = [new_x,new_y,new_map] or arg = [new_map].
        Find the map in map_dict, or create it. Also centers camera on the 
        actor object. Does not care what map it's coming from."""
        self.map.print_to_black()
        if len(arg)>4: #str
            path = arg
        else: # list type
            path = arg[-1]
            self.remove_render_one(actor)
        new_map_path = solidify_path(path)
        if new_map_path in self.map_dict.keys(): # Is map created?
            self.map_name = deconstruct_path(path)
            self.map = self.map_dict[new_map_path]
            self.objs = self.map.objs
        else: # Create new map and add it to the map list.
            self.create_new_map(new_map_path)
        if len(arg)<4: # Add actor to new map and center camera on them.
            actor.x = arg[0]
            actor.y = arg[1]
            self.map.center_camera(actor.x,actor.y)
            self.set_render_one(actor)
            self.add_render_one(actor)
        self.set_sprites_in_objs()
        self.map.print_from_black()

    def create_new_map(self,path):
        """Creates the map from a given path, populating it with object sprites
        found in travel objects. Sets this new map to the game's current map."""
        for obj in self.objs.pallete_objs:
            self.universal_objs.add(obj) # Collect objects from the pallete
        self.map_dict[path] = Map(self.universal_objs)
        self.map_name = deconstruct_path(path)
        self.map = self.map_dict[path]
        self.objs = self.map.objs
        self.set_sprites_in_objs()
        self.set_map_path(path,True)
        self.init_map(False)

    def take_dmg(self,obj):
        """ Check all sides of an object for enemy chars
        on the geom."""
        for direction in obj.touching.keys():
            for enemy in obj.touching[direction]:
                if direction in enemy.dmg_dirs:
                    if enemy.char in obj.enemy_chars:
                        obj.hp -= enemy.dmg

    def set_default_color(self,color):
        self.map.background_color = color
        self.objs.default_color = color
    def teleport_obj(self,obj,x:int=0,y:int=0):
        """Moves an object to a given location if no geometry is there."""
        obj.move_x = x - obj.x
        obj.move_y = y - obj.y
        if x > obj.x:   obj.move_x *= -1
        if y < obj.y:   obj.move_y *= -1
        if obj.move in ["wasd","dirs"]:
            self.map.center_camera(obj.x+obj.width()//2,obj.y-obj.height()//2)
    def set_movement(self,obj,move_x = 0,move_y = 0):
        """Start at 0, see how close we can get to move_y and move_x."""
        max_found = False
        obj.move_x = 0
        obj.move_y = 0
        x_change = 0
        y_change = 0
        if move_x != 0:
            x_change = (move_x)//(abs(move_x))
        if move_y != 0:
            y_change = (move_y)//(abs(move_y))
        while not max_found:
            if not self.can_move(obj,x_change,y_change) or (obj.move_y == move_y and obj.move_x == move_x):
                max_found = True
            else:
                if obj.move_x != move_x:
                    obj.move_x += x_change
                if obj.move_y != move_y:
                    obj.move_y += y_change
                elif obj.move_y == move_y and obj.move_x == move_x:
                    max_found = True
        if obj.move_x!=0 and obj.move_y!=0:
            self.objs.render_objs.add(obj)
    def can_move(self, obj,x_change,y_change=0):
        """Check if there are any characters in the area that 
        the obj would take up. Takes literal change in x and y.
        Returns True if character can move in that diRECTion."""
        yf = y_change + obj.y
        ys = yf - obj.height()
        xs = x_change + obj.x
        xf = xs + obj.width()
        if x_change > 0:      xs = obj.x + obj.width()
        elif x_change < 0:    xf = obj.x
        if obj.geom not in ["line","skeleton"]:
            if y_change < 0:
                yf = obj.y - obj.height()
            elif y_change > 0:
                ys = obj.y + 1
        else:
            ys = yf
        for y in range(ys,yf+1):
            for x in range(xs,xf):
                if self.map.geom[y][x]:
                    return False
        return True
    
    # These functions are put into geom_set_dict, for quicker lookup than if statements.
    def geom_all(self,obj,boolean = 1):
        """Creates a hollow box of geometry (hollow is obviously faster than not)"""
        for y in range(obj.y - obj.height() +1,obj.y +1):
            x_end = min([obj.x + obj.width()-2,len(self.map.geom[y])])
            for x in [obj.x,x_end]:
                self.map.set_xy_geom(x, y,boolean)
        for x in range(obj.x, min([obj.x + obj.width(),len(self.map.geom[y])])):
            for y in [obj.y - obj.height() +1,obj.y]:
                self.map.set_xy_geom(x, y,boolean)
    def geom_complex(self,obj,boolean = 1):
        # Based on all characters of a sprite that are not blank.
        [[self.map.set_xy_geom(x + obj.x, obj.y - y,boolean) 
        for x in range( min([obj.width(), len(self.map.geom[y])-obj.x]) ) 
        if SKIP not in obj.sprite[y][x]]
        for y in range(obj.height())]
    def geom_line(self,obj,boolean = 1):
        [self.map.set_xy_geom(x + obj.x, obj.y, boolean)
        for x in range( min([obj.width(), len(self.map.geom[-1])-obj.x]) )]
    def geom_skeleton(self,obj,boolean = 1):
        [self.map.set_xy_geom(x + obj.x, obj.y, boolean)
        for x in range( min([obj.width(), len(self.map.geom[-1])-obj.x]) )
        if SKIP not in obj.sprite[-1][x]]
    def geom_none(self,obj,boolean=0):
        pass
    
    def remove_rend(self,obj):
        start_y = obj.y-obj.height()+1
        for y in range(start_y,obj.y+1):
            start_x = find_non(obj.sprite[y-start_y],SKIP) + obj.x
            for x in range(start_x, min([obj.x + obj.width(), self.map.width ])):
                char = obj.sprite[y-start_y][x-obj.x]
                if SKIP not in char:
                    self.map.remove_xy_rend(x,y,char)
    def remove_geom(self,obj):
        self.geom_set_dict[obj.geom](obj,0)
    def remove_the_dead(self):
        for obj in self.the_dead:
            chunk = self.objs.find_obj_chunk(obj.x,obj.y)
            i = self.objs.find_obj_index(obj,chunk)
            if i!=-1:
                chunk[obj.y%CHUNK_HEI].pop(i)
        self.the_dead = set()

    def init_render_all(self):
        self.map.init_rend()
        self.map.init_geom()
        for chunky in self.objs.chunks.values():
            for chunkx in chunky.values():
                for line in chunkx.values():
                    i = 0
                    while i < len(line):
                        obj = line[i]
                        if obj.img != "dead":
                            self.init_render_obj(obj)
                        self.geom_set_dict[obj.geom](obj)
                        if obj.geom == "background" or obj.img == "dead":
                            line.pop(i)
                        elif obj.geom == "all" and obj.static and obj.char not in self.acts.acted_obj_chars:
                            #This is an object that will never be used and cannot be walked through.
                            line.pop(i)
                        else:
                            i+=1
        self.objs.render_objs = set()
    def init_render_obj(self,obj):

        obj.top_y = obj.y-obj.height()+1
        obj.top_x = obj.x+obj.width()-1
        start_y = obj.top_y
        end_y = min([obj.y+1,self.map.height-1])
        if obj.geom!="background":
            for y in range(start_y,end_y):
                start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.x
                end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.x+1,self.map.width])
                for x in range(start_x,end_x):
                    char = obj.sprite[y-start_y][x-obj.x]
                    if SKIP not in char:
                        self.map.rend[y][x].append(char) # The only difference.
        else:
            for y in range(start_y,end_y):
                start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.x
                end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.x+1,self.map.width])
                for x in range(start_x,end_x):
                    char = obj.sprite[y-start_y][x-obj.x]
                    if SKIP not in char:
                        self.map.rend[y][x][0] = char
    def render_all(self):
        """ This creates the output AND geometry
        maps out of all object sprites."""
        self.set_load_chunks()
        for obj in self.objs.render_objs:
            self.render_one(obj)
        self.render_map_mirrors()
        self.move_camera()
        self.objs.render_objs = set()

    def render_map_mirrors(self):
        map_name = deconstruct_path(self.map_name)
        if map_name in self.mirs.mirrors:
            for mir in self.mirs.mirrors[map_name]:
                mir_type = self.mirs.types[mir.mirror_name]
                if mir_type.color > -1:
                    mir_color = color_by_num(mir_type.color)
                    colored = True
                else:colored=False
                for y in range(0,mir.y2-mir.y1+1):
                    for x in range(0,mir.x2-mir.x1+1):
                        rend_x = mir.x1+(x*mir_type.x_mult)+mir.copy_x
                        rend_y = mir.y1+(y*mir_type.y_mult)+mir.copy_y
                        char =       self.map.rend[rend_y][rend_x][-1][-1]
                        if colored:
                            color = mir_color
                        else:
                            color = self.map.rend[rend_y][rend_x][-1][:-1]
                        color = brighten(color)
                        if mir_type.flip_horizontal:
                            if char in H_FLIP_CHARS:
                                char = H_FLIP_CHARS[char]
                        self.map.rend[mir.y1+y][x+mir.x1][0] = color + char

    def render_one(self,obj):
        self.remove_render_one(obj)
        self.set_render_one(obj)
        self.add_render_one(obj)

    def remove_render_one(self,obj):
        self.remove_rend(obj)
        self.remove_geom(obj)
        self.objs.remove_obj(obj)
    def set_render_one(self,obj):
        obj.set_obj_coords()
        self.objs.set_sprite(obj)
    def add_render_one(self,obj):
        self.objs.append_obj_ordered(obj)
        self.add_rend(obj)
        self.add_geom(obj)

    def move_camera(self):
        # CAMERA MOVEMENT:
        move_x, move_y = 0,0
        player = self.map.camera_star 
        if "x" in self.camera_follow:
            if self.map.width > self.map.end_camera_x < player.x + WINDOW_CUSHION_X:
                move_x = 1
            elif self.map.camera_x + WINDOW_CUSHION_X > player.x and self.map.camera_x > 0:
                move_x = -1
        if "y" in self.camera_follow:
            if self.map.height > self.map.end_camera_y < player.y - player.height() + WINDOW_CUSHION_Y:
                move_y = 1
            elif self.map.camera_y + WINDOW_CUSHION_Y > player.y - player.height() and self.map.camera_y > 0:
                move_y = -1
        self.map.move_camera(move_x,move_y)
        #self.map.center_camera(player.x,player.y)

    def add_geom(self,obj):
        self.geom_set_dict[obj.geom](obj)
    def add_rend(self,obj):
        start_y = obj.y+1-obj.height()
        end_y = min([obj.y+1,self.map.height-1])
        # Find all the objects that are in front of the character
        objs_ahead = self.find_objs_ahead(obj)
        for y in range(start_y,end_y):
            start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.x
            end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.x+1,self.map.width])
            # Don't attempt to print out of bounds
            for x in range(start_x,end_x):
                covered = False
                for bobj in objs_ahead:
                    back_x = x - bobj.x
                    back_y = y - bobj.y + bobj.height()
                    # Check if part of the bobj is at this coordinate
                    if -1 < back_x < bobj.width() and -1 < back_y < bobj.height():
                        covered = True
                        break
                char = obj.sprite[y-start_y][x-obj.x]
                if SKIP not in char: # If this is not a blank character
                    if covered:
                        index = max([len(self.map.rend[y][x])-1,1])
                        self.map.rend[y][x].insert(index,char)
                    else:
                        self.map.rend[y][x].append(char)

    def find_objs_ahead(self,obj):
        """Looks at the object's chunk and the one under it for objects
        that appear to cover up the main object."""
        objs_ahead = set()
        chunks = [self.objs.find_obj_chunk(obj.x,obj.y)]
        chunks_below = []
        #if obj.y%CHUNK_HEI > CHUNK_HEI//2:
        chunks_below.append(self.objs.find_obj_chunk(obj.x,obj.y+CHUNK_HEI))
        #if obj.x%CHUNK_WID < CHUNK_WID//2:
        chunks.append(self.objs.find_obj_chunk(obj.x-CHUNK_WID,obj.y))
        chunks_below.append(self.objs.find_obj_chunk(obj.x-CHUNK_WID,obj.y+CHUNK_HEI))
        #elif obj.x%CHUNK_WID > CHUNK_WID - CHUNK_WID//3:
        #else:
        chunks.append(self.objs.find_obj_chunk(obj.x+CHUNK_WID,obj.y))
        chunks_below.append(self.objs.find_obj_chunk(obj.x+CHUNK_WID,obj.y+CHUNK_HEI))
        for chunk in chunks:
            for linei in range((obj.y+1)%CHUNK_HEI,CHUNK_HEI):
                line = chunk[linei]
                for bobj in line:
                    if bobj.x + bobj.width() > obj.x:
                        if bobj.x < obj.x + obj.width():
                            objs_ahead.add(bobj)
        for chunk in chunks_below:
            for linei in range(CHUNK_HEI):
                line = chunk[linei]
                for bobj in line:
                    if bobj.height() > linei + 2:
                        if bobj.x + bobj.width() > obj.x:
                            if bobj.x < obj.x + obj.width():
                                objs_ahead.add(bobj)
        return objs_ahead

class Map():
    """Three arrays are stored in a Map object: the wasd input 
    map, the output map, and a geom map.
    Set the map path upon initialization"""
    def __init__(self,universal_objs=set()):
        self.path = "" #WILL INCLUDE DIRPATH
        self.background_color = DEFAULT_COLOR
        self.text_color = DEFAULT_TEXT

        self.input_map = list() # Made to store user-made map. 1D list of strings.
        self.rend = [] # Map of what will be rendered. 3-Dimensional.
        self.geom = [] # For checking collision.
        self.print_map = ""
        self.mirrors = []
        self.color_on = True
        self.last_used_color = DEFAULT_COLOR

        self.objs = Objs(universal_objs)

        self.height = WINDOW_HEI
        self.width = WINDOW_WID
        self.camera_x = 0
        self.camera_y = 0 # start_window_y
        self.camera_star = None #The player, usually.
        self.end_camera_y = WINDOW_HEI
        self.end_camera_x = WINDOW_WID
            # These are the map coordinates of the 
            # top-left-most char shown in the window.
            
        self.disp_msg = ""
        self.msg_timer = 0

    def set_path(self,path,directed_path=False):
        """ Stores characters and their coords in the input map,
        using a preset path. Also sets self.width and self.height. """
        if not directed_path:
            path = solidify_path(path)
        # Adds parent directory of running program
        self.path = path
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
            for y in range(self.height):
                line = list()
                for x in range(self.width):
                    line.append(0)
                self.geom.append(line)
        else:self.clear_geom()
    def clear_geom(self):
        for y in range(self.height):
            for x in range(self.width):
                self.geom[y][x] = 0
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
        """Displays the proper area of self.rend. No longer includes
        newline escapes. Appending to a new screen list is oddly faster
        than editing a screen list."""
        self.screen = []
        if self.color_on:
            [[self.get_print_pixel(self.rend[row][x][-1],x) for x in range(self.camera_x,self.end_camera_x)] for row in range(self.camera_y,self.end_camera_y)]
        else:
            [[self.get_print_pixel(self.rend[row][x][-1][-1],x) for x in range(self.camera_x,self.end_camera_x)] for row in range(self.camera_y,self.end_camera_y)]
        self.add_message()
        self.add_data(data)
        self.print_map = RETURN + self.text_color + "".join(self.screen)
        print(self.print_map)
    def get_print_pixel(self,color_char_pair,x):
        """Filters a colored character to not call
        the same color escape code as has been most
        recently called."""
        if len(color_char_pair)==1:
            color = self.background_color
            char = color_char_pair
        else:
            color = color_char_pair[:-1]
            char = color_char_pair[-1]

        if color != self.last_used_color:
            self.last_used_color = color
            char = color + char
        self.screen.append(char)
    def add_message(self):
        if len(self.disp_msg) > 0:
            start = int(len(self.screen)*((WINDOW_HEI-len(self.disp_msg)-.5)/WINDOW_HEI))
            row_down = int(len(self.screen)*(1/WINDOW_HEI))
            half_msg_len = len(self.disp_msg[0])//2-1
            i = start
            for row in self.disp_msg:
                for c in row:
                    self.screen[i-half_msg_len]=str(c)
                    i += 1
                start += row_down
                i = start
    def add_data(self,data):
        if len(data)>0:
            i = int(len(self.screen)*((WINDOW_HEI-1)/WINDOW_HEI))
            self.screen[i-1] += self.background_color
            for c in data:
                self.screen[i]=c
                i +=1
            self.screen[i] += self.background_color
    def display_timer(self):
        if len(self.disp_msg) > 0:
            if self.msg_timer < time():
                self.disp_msg = ""
    def print_to_black(self):
        """Clears the screen line by line. Moves
        theme volume from 100 to 0%."""
        print(DEFAULT_COLOR + RETURN,end="")
        volume = 1
        for line in range(WINDOW_HEI):
            volume -= 1/WINDOW_HEI
            print(S_LINE)
            mixer.music.set_volume(volume)
            sleep(.03)
    def print_from_black(self):
        print(RETURN,end="")
        volume = 0
        for row in range(self.camera_y,self.end_camera_y):
            line = []
            for x in range(self.camera_x,self.end_camera_x):
                line.append(self.rend[row][x][-1])
            print("".join(line))
            volume += 1/WINDOW_HEI
            mixer.music.set_volume(volume)
            sleep(.03)
        mixer.music.set_volume(1)
        
    def set_xy_geom(self,x,y,boolean=1):
        """Sets boolean value at a given position on map"""
        self.geom[y][x] = boolean
    def get_xy_geom(self,x,y):
        """Returns what boolean value is at this position."""
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
        half_wid = WINDOW_WID//2
        half_hei = WINDOW_HEI//2
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
        self.end_camera_x = self.camera_x + WINDOW_WID
        self.end_camera_y = self.camera_y + WINDOW_HEI

class Acts():
    def __init__(self):
        self.acts = []
        self.acted_obj_chars = set()
        # This is used to find which objects are
        # never used and can be removed as objects.
    def new(self,func,name="default",type="interact", item_char="",
        arg=None,map="default",act_on_self=False,locked = False, loc_arg = []):
        if map != "default":
            map = deconstruct_path(map)
        new_act = self.Act(func,name,type,item_char,arg,map,act_on_self,locked,loc_arg)
        self.acts.append(new_act)

        self.acted_obj_chars.add(item_char)
        self.acted_obj_chars.add(item_char)

    class Act():
        def __init__(self,func,name="default",type="interact",
        item_char="",arg=None,map="",act_on_self=False,locked=False,loc_arg = []):
            self.func = func
            self.name = name
            self.type = type # location, item, survive, die, interact
            self.item_char = item_char # The char of the object that was interacted with.
            self.act_on_self= act_on_self              
            self.arg = arg # could be the new skin,
            self.map = map
            self.locked = locked
            self.loc_arg = loc_arg
class Mirrors():
    def __init__(self):
        self.mirrors = dict() #world_name:list of mirrors
        self.types = dict()
    def new_type(self,name:str,flip_sprites:bool=False,color:int=-1,
        flip_horizontal:bool=False,flip_vertical:bool=False,
        ripple:bool=False,brighten:int=0):
        self.types[name] = self.Mirror_Type(flip_sprites,color,
            flip_horizontal,flip_vertical,ripple,brighten)
    def new(self,world_name,mirror_name,x1,y1,x2,y2,copy_x,copy_y):
        world_name = deconstruct_path(world_name)
        if world_name not in self.mirrors:
            self.mirrors[world_name]=[]
        self.mirrors[world_name].append(self.Mirror(mirror_name,x1,y1,x2,y2,copy_x,copy_y))
    class Mirror():
        """This is for instances of rectangular areas of land that are
        reflective. It is assumed that the location being mirrored has
        the same dimensions as the mirror."""
        def __init__(self,mirror_name,x1,y1,x2,y2,copy_x,copy_y):
            self.mirror_name = mirror_name
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.copy_x = copy_x
            self.copy_y = copy_y
    class Mirror_Type():
        """Create reflection templates to use here, either on the
        map or on objects. Using a color sets the whole reflection
        to that color. The brighten variable makes the reflected text
        backgrounds brighter if a positive integer, or darker if
        negative. When flip_sprites is on, the game will look for
        objects in the reflection area and find their sprites and find
        out if those sprites have other sides."""
        def __init__(self,flip_sprites:bool=False,color:int=-1,
        flip_horizontal:bool=False,flip_vertical:bool=False,
        ripple:bool=False,brighten:int=0):
            self.flip_sprites = flip_sprites
            self.color = color
            self.flip_horizontal = flip_horizontal
            self.flip_vertical = flip_vertical
            self.ripple = ripple
            self.brighten = brighten

            if flip_horizontal: self.y_mult = -1
            else:               self.y_mult = 1
            if flip_vertical:   self.x_mult = -1
            else:               self.x_mult = 1
class Objs():
    def __init__(self,universal_objs=set()):
        """Stores objects in their chunks and sprites AND pallete_objs
        that may or may not be used on the given map."""
        self.chunks = dict()
        # Key-value pairs of y's to x's.
        # Each x is a list of objects (a chunk).
        self.load_chunks = []
        # The list of chunks that will be edited and/or shown.
        self.render_objs = set()
        self.pallete_objs = universal_objs # These are all the o.g. objs.
        self.sprites = dict()
        self.max_sprite_height= 1
        self.max_sprite_width = 1
        self.default_color = DEFAULT_COLOR
    
    def set_img(self,obj,img):
        self.render_objs.add(obj)
        obj.img = img
    def set_sprite(self,obj):
        """Change the sprite of an object."""
        obj.sprite = []
        [obj.sprite.append(list(row)) for row in self.sprites[obj.img]]
        self.set_sprite_color(obj)
        obj.rotate = 0
        obj.img = obj.img
    def set_sprite_color(self,obj):
        chars = [SKIP]
        if obj.geom == "skeleton":
            chars.append(BLANK)
        for y in range(obj.height()):
            for x in range(obj.width()):
                char = obj.sprite[y][x]
                if chars[-1] == char:
                    char = SKIP # Turn any BLANKS into SKIPS
                if char != SKIP:
                    char = obj.color + char
                obj.sprite[y][x] = char
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
                elif char[-1] in FLIP_CHARS:
                    char = char[:-1] + FLIP_CHARS[char[-1]]
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
    def find_obj_index(self,obj,chunk=None):
        """Looks for an object within a chunk by id and y coord. Returns -1
        if not found."""
        if chunk == None:
            chunk = self.find_obj_chunk(obj.x,obj.y)
        line = chunk[obj.y%CHUNK_HEI]
        i=0
        while i < len(line):
            currid = id(line[i])
            if id(obj) == currid:
                return i
            i+= 1
        return -1
    def find_obj_chunk(self,x,y,divided=False):
        """ Confirms that a chunk exists or creates it.
        Returns the chunk x and y. """
        if not divided:
            x = x//CHUNK_WID
            y = y//CHUNK_HEI
        if y not in self.chunks:
            self.chunks[y] = dict()
        if x not in self.chunks[y]:
            self.chunks[y][x] = dict()
            for y2 in range(CHUNK_HEI):
                self.chunks[y][x][y2] = list()
        return self.chunks[y][x]
    def append_obj_ordered(self,obj):
        """This is for a ready-made object who must be placed in the right spot
        within the objs list."""
        #for xy in ([obj.x,obj.y],[obj.top_x,obj.top_y]):
        xy = [obj.x,obj.y]
        chunk = self.find_obj_chunk(xy[0],xy[1])
        line = chunk[xy[1]%CHUNK_HEI]
        i = 0
        while i < len(line):
            next_obj = line[i]
            if next_obj.x >= xy[0]:
                break
            i+=1
        chunk[xy[1]%CHUNK_HEI].insert(i,obj)
    def remove_obj(self,obj):
        """Remove the obj twice, once from the top coords, and once
        from the bottom ones."""
        #for xy in ([obj.x,obj.y],[obj.top_x,obj.top_y]):
        xy = [obj.x,obj.y]
        chunk = self.find_obj_chunk(xy[0],xy[1])
        line = chunk[xy[1]%CHUNK_HEI]
        i = self.find_obj_index(obj,chunk)
        if len(line) > 0:
            line.pop(i)
    def init_obj(self,obj,rotate=0):
        obj.rotate_right(rotate)
        self.set_sprite(obj)
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
        self.append_obj_ordered(obj)
    def add_to_pallete(self,obj):
        obj_clone = self.copy(obj) #reset coords
        self.pallete_objs.add(obj_clone)
    def new(self,img, char, x=-1,y=-1, geom = "all",
    move = None, xspeed = 1, yspeed = 1, hp =1,face_right=True,
    face_down=False, grav=False,dmg = 1, enemy_chars=[],
    dmg_dirs=[], set_rotate=0, animate=None,txt=-1,max_jump=1,
    color="",data=dict()):
        """Creates an Obj and appends it to the objs list. This should
        only be called by the module-user (you)."""
        obj = self.Obj(img, char, x,y, geom, move,xspeed,yspeed,
            hp,face_right,face_down,grav,dmg,enemy_chars,dmg_dirs,
            animate,txt,max_jump,color,data)
        self.add_to_pallete(obj)

    def copy(self,o,newx=-1,newy=-1):
        """Returns a duplicate of an object."""
        obj = self.Obj(o.img, o.char, newx,newy, o.geom, o.move, o.xspeed, o.yspeed,
            o.hp, o.face_right, o.face_down, o.grav, o.dmg, o.enemy_chars, o.dmg_dirs,
            o.animate,o.txt,o.max_jump,o.color,o.data)
        return obj
    class Obj():
        def __init__(self,img, char, x=-1,y=-1, geom = "all",
        move = None, xspeed = 1,yspeed = 1,hp =1,face_right=True,
        face_down=False,grav:bool=False,dmg = 1,enemy_chars=[],dmg_dirs=[],
        animate=None,txt:int=-1,max_jump=1,color="",data=dict()):
            self.static = False
            self.move = move # None, leftright, wasd, dirs.
            self.grav = grav
            if move == None and not grav:
                self.static = True
            #else:
            self.xspeed = xspeed
            self.yspeed = yspeed
            self.move_x = 0
            self.move_y = 0
            self.direction = 0 # NOT IMPLEMENTED
            self.velocity = 0 # NOT IMPLEMENTED
            self.acceleration = 0 # NOT IMPLEMENTED
            self.max_jump = max_jump
            self.jump = 0 # based on yspeed

            if not self.static:
                #wasd: controls, i:interact, g:gravity (falling)
                self.move_time = {"w":0,"a":0,"s":0,"d":0,"i":0,"g":0}
                self.init_touching()
                # Store pointers to objects that are touching this one.
            self.img = img
            self.img = img
            self.sprite = [] # Must be set through Objs function new().
            self.geom = geom # Options of: None, line, complex, skeleton, background, or all.
            self.x = x
            self.y = y
            self.top_x = x
            self.top_y = y
            self.char = char
            self.hp = hp
            self.enemy_chars = enemy_chars
            self.dmg = dmg
            self.dmg_dirs = dmg_dirs

            self.animate = animate # Edited in the objs.append_obj function
            self.idle_animation = [img] # When doing NOTHINg. NOT IMPLEMENTED
            self.animation = [img]
            self.framerate = ANIMATE_FPS
            self.frame_time = 0
            self.frame = 0

            self.color = self.set_color(color)
            # "flip" is default, mirrors the image for every change between right and left.
            # Otherwise, if it's not None it becomes a dictionary: {w,a,s,d:sprite images.}            
            self.txt = txt # line number from textsheet
            self.reflect_x = 0
            self.reflect_y = 0
            self.face_right = face_right # Left: False, Right: True
            self.face_down = face_down # Up: False, Down: True
            self.rotate = 0 # 0 through 3
            self.data = data

        def init_touching(self):
            self.touching = {"up":set(),"down":set(),"left":set(),"right":set(),"inside":set()}
        def set_color(self,color):
            if type(color) == type(42):
                self.color = color_by_num(color)
            else:
                self.color = color # The literal escape code (or blank), not the number.
            return self.color
            
        def width(self,y=0):
            return len(self.sprite[y])
        def height(self):
            return len(self.sprite)
        def set_obj_coords(self):
            self.top_x += self.move_x
            self.top_y += self.move_y
            self.x += self.move_x
            self.y += self.move_y
            self.move_x = 0
            self.move_y = 0

        def rotate_right(self,rotate):
            """Rotates the object sprite 90 degrees 
            times the rotate var."""
            while rotate != self.rotate:
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
    if x < 16:
        x = PRE_16_COLORS[x]
    return (COLOR_ESC + str(x) + "m")
def num_by_color(x):
    if len(x) > 3:
        return (x[len(COLOR_ESC):-1])
    else:
        return x
def print_color_numbers():
    """For Debugging: Returns a sheet of all color numbers highlighted
    by their respective color."""
    spaces = " "
    black_words = "\033[38;5;" + str(BLACK_INT) + "m"
    white_words = "\033[38;5;" + str(WHITE_INT) + "m"
    for x in range(1,256):
        color = COLOR_ESC + str(x) + "m"
        try:spaces = " " * (9 - int(log(x,10)))
        except:pass
        print(f"{black_words}{color}{x}{white_words}{x}{spaces}{spaces}",end="")
        if (x-15)%6 == 0:
            print()
WHITE_INT = 231
BLACK_INT = 16 # SAME AS 232
PRE_16_COLORS = {1:160,2:34,3:172,4:20,5:90,6:68,7:252,8:243,
                9:167,10:40,11:192,12:32,13:127,14:44,15:WHITE_INT}
SHADE = 6
JUMP_SHADE = 36
def brighten(color_code:str,positive=True):
    """Takes a color escape code, returns a color escape code that
    is either darker(-) or brighter(+)."""
    if positive:change = 1
    else:change = -1
    if len(color_code)>len(COLOR_ESC):
        color = int(color_code[len(COLOR_ESC):color_code.find("m")])
    else:
        color = 232
    if color < BLACK_INT:
        return brighten(color_by_num(PRE_16_COLORS[color]))
    elif color > WHITE_INT: #MONOCHROME
        color += change
        if color <= WHITE_INT:
            color = BLACK_INT
        elif color > 255:
            color = WHITE_INT
    else:
        root = (color-BLACK_INT)%JUMP_SHADE
        if positive:
            if root >= JUMP_SHADE - SHADE:
                color = WHITE_INT
            else:
                color += (change*SHADE)
        else:
            if root < SHADE:
                color += (change*JUMP_SHADE)
            else:
                color += (change*SHADE)
        color = min([WHITE_INT,color])
        color = max([BLACK_INT,color])
    return color_by_num(color)

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
def linked_list(list1):
    """Create a linked list (dict) with a closed loop ending from a given list."""
    llist = dict()
    if len(list1) > 1:
        for i in range (len(list1)-1):
            llist[list1[i]] = list1[i+1]
        llist[list1[i+1]] = list1[i+1]
    else:
        llist[list1[0]] = list1[0]
    return llist

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
def solidify_path(path,suffix=".txt"):
    if DIRPATH not in path:
        path = DIRPATH + path
    if suffix not in path:
        path += suffix
    return path
def deconstruct_path(path):
    path = path[path.rfind("/")+1:]
    if "." in path:
        path = path[:path.rfind(".")]
    return path