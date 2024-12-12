###################################
#                                 #
#       Texillica Game Engine     #
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
from acts import Acts
from linked import Linked
from map import Map
from mirrors import Mirrors
from statics import ANIMATE_FPS, BLANK, BUBBLE, CHUNK_HEI, CHUNK_WID, CLEAR, COLOR_ESC, DEFAULT_COLOR, DEFAULT_TEXT, FLIP_CHARS, H_FLIP_CHARS, NEW_SETTING, RETURN, S_LINE, SKIP, SPACES, WINDOW_HEI, WINDOW_WID, deconstruct_path, find_count, find_indices, find_non, ms_gothic, replace_spaces, rfind_non, solidify_path, color_by_number

system("") # Allow the terminal to understand escape codes
print(CLEAR) # erase pygame's message.

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
        self.mirrors = Mirrors()
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

        self.fps = 0
        self.display_fps = 0
        self.fps_list = []
        self.display_data = ""
        self.start_time = 0
        self.fps_max = 60
        self.fps_timer = 0
        self.fps_timer_wait = 0.25
        self.game_act_time = 0
        self.game_speed = 1 # General act calling per second.
        self.total = 0
        self.frame_start = time()
        self.prev_frame_start = self.frame_start

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
                            ".":self.run_interacts},
                        "drive":
                            {"w":self.accelerate,"s":self.decelerate,
                             "a":self.rotate_left,"d":self.rotate_right}}

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
                            # $below$ at end of sprite name, this tells you that
                            # the color code is below the text drawing rather than
                            # in it.
                            if line[inds[2]+1:inds[3]] == "below":  where_coded = True
                        colors_raw = line[inds[1]+1:inds[2]]
                        colors_raw = colors_raw.split(",")
                        color_code = [""]
                        for num in colors_raw:
                            color_code.append(color_by_number(int(num)))
                else: # Append to the current sprite image.
                    line = replace_spaces(line)
                    line = ms_gothic(line)
                    curr_sprite.append(list(line))
                    height +=1
                line = file.readline()[:-1] # Removes the \n
        self.set_sprites_in_objs()
    
    # Made for user readability
    def new_object(self, img:str, char:str, x:int = -1, y:int = -1, geom:str = "all",
        move = None, xspeed:int = 1, yspeed:int = 1, hp:int = 1, face_right:bool = True,
        face_down:bool = False, grav:bool = False, dmg = 1,enemy_chars:list = [],
        dmg_dirs:list=[], animate = None,txt:int = -1, max_jump = 1, color = "",
        data:dict = dict(), rotation:int = 0):
        """Forward arguments to objs.new(). The only required variables are img and char.
        Img is a string of the sprite name you will use.
        Char is the text character on the map which represents where your object will be
        drawn."""

        self.objs.new(img, char, x, y, geom, move, xspeed, yspeed, hp, face_right, face_down,
        grav, dmg, enemy_chars, dmg_dirs, animate, txt, max_jump, color, data, rotation)

    # Made for user readability
    def new_action(self,func,name:str="default",type:str="interact", item_char:str="",
        arg=None,map:str ="default",act_on_self:bool=False,locked:bool = False, loc_arg = []):
        """Forward arguments to Acts.new()"""
        self.acts.new(func, name, type, item_char, arg, map, act_on_self, locked, loc_arg)

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
        #self.map.print_all()
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
        self.set_all_movement()
        self.render_all()
        self.map.display_timer()
        self.map.print_all()
        self.run_frame_counter()
    def game_loop_debug(self):
        self.set_all_movement()
        self.render_all()
        self.map.display_timer()
        self.map.print_all(self.display_data)
        self.run_frame_counter(True)

    def run_frame_counter(self,with_avg=False):
        self.prev_frame_start = self.frame_start
        if time() != self.frame_start:
            self.fps = round(1/(time()-self.frame_start),2)
            if with_avg:
                self.fps_list.append(self.fps)
            if time() >= self.fps_timer:
                self.fps_timer = time() + self.fps_timer_wait
                self.display_fps = self.fps
        else:
            self.fps = 999.00 # Cosmetic only.
        self.display_data = "FPS:" + str(self.display_fps)
        self.display_data +=" Map: " + deconstruct_path(self.map_name)
        self.frame_start = time()

    def end_game(self):
        """All the comes after the main game_loop"""
        mixer.music.stop()
        self.play_sound("quit")
        end_game = CLEAR+SPACES+"Game Over!\n"
        if len(self.fps_list) > 0:
            fps_avg = str(round(sum(self.fps_list)/len(self.fps_list),2))
            runtime = str(int(time()-self.start_time))
            end_game += "Average FPS: "+fps_avg+"\n"+"Runtime: "+runtime+" seconds.\n"
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
        self.game_acts()
        self.set_load_chunks()
        self.remove_the_dead()
        for chunk in self.objs.load_chunks:
            for line in chunk.values():
                for obj in line:
                    if not obj.static:
                        # ANIMATION
                        if time() > obj.frame_time:
                            obj.frame_time = time() + obj.framerate
                            self.next_frame(obj)
                        self.get_objs_touching(obj)
                        if obj.move in ["wasd","dirs","drive"]:
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
                        self.set_movement(obj)
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
                                    #self.set_movement(obj,0,1)
                                    pass
                        # DAMAGE-TAKING
                        self.take_dmg(obj)
                    if obj.hp <= 0 or obj.y == self.map.height: # All non-player mobs, DEATH.
                        if obj.move in ["wasd","dirs","drive"]:
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

    def game_acts(self):
        if self.game_act_time < time():
            if is_pressed("p"):# PAUSE
                self.game_act_time = time() + self.game_speed
                mixer.music.set_volume(.25)
                wait("p")
                sleep(.5)
                mixer.music.set_volume(1)
            elif is_pressed("q"):# QUIT
                self.quit = True
            elif is_pressed("ctrl+r"):
                self.init_render_all()# RELOAD SCREEN
            elif is_pressed("ctrl+g"):
                self.game_act_time = time() + self.game_speed
                self.map.setting = NEW_SETTING[self.map.setting]
    def next_frame(self,obj):
        if obj.animation.curr.next is not None or obj.animation.loop:
            self.objs.set_img(obj,obj.animation.next())
        elif obj.animation.stuns:
            obj.stunned = False
    def player_actions(self,player):
        # PLAYER MOVEMENT:
        if not player.stunned:
            for key in self.key_dict[player.move].keys():
                if is_pressed(key):
                    self.key_dict[player.move][key](player)
                    self.set_movement(player)
                    # break # ONLY ALLOW ONE BUTTON AT A TIME
        if(player.move == "drive"):
            # char height is twice the length of char width
            player.true_x += player.velocity_x * 4 * self.get_frame_time() * 2
            self.set_movement(player)
            player.true_y += player.velocity_y * 4 * self.get_frame_time()
            self.set_movement(player)
            player.apply_friction()
            self.objs.set_img(player,player.get_image())
        self.run_acts(player)
        self.map.camera_star = player # UPDATE: Only needs to be done once.
        coords = "("+str(player.x)+","+str(player.y)+")"
        self.display_data += coords
    
    def accelerate(self, obj):
        obj.accelerate()

    def decelerate(self, obj):
        obj.accelerate(-.6)
    
    def rotate_right(self, obj):
        obj.direction = (obj.direction + (200 * self.get_frame_time())) % 360

    def rotate_left(self, obj):
        obj.direction = (obj.direction - (200 * self.get_frame_time())) % 360

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

    def get_frame_time(self):
        return self.frame_start - self.prev_frame_start

    # Synonymous functions
    def move_left(self,obj):
        self.objs.set_img(obj,obj.animate["a"])
        obj.face_right = False
        obj.true_x -= obj.xspeed*(self.get_frame_time())
    def move_right(self,obj):
        self.objs.set_img(obj,obj.animate["d"])
        obj.face_right = True
        obj.true_x += obj.xspeed*(self.get_frame_time())
    def move_down(self,obj):
        self.objs.set_img(obj,obj.animate["s"])
        obj.face_down = True
        obj.true_y += obj.yspeed*(self.get_frame_time())
    def move_up(self,obj):
        self.objs.set_img(obj,obj.animate["w"])
        obj.face_down = False
        obj.true_y -= obj.yspeed*(self.get_frame_time())
    
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

    """Here are pre-made functions that can be put into Acts. Every function made for an
    Act must take 2 arguments which, if used, must be a game object and a more specific arg."""
    def act_change_sprite(self,obj,arg):
        """arg is a Linked List."""
        self.objs.set_img(obj,arg.next())
    def act_animate(self,obj,arg):
        """This sets the object animation to a linked list, but next_frame iterates
        through it."""
        obj.animation = arg
        obj.animation.reset()
        obj.stunned = obj.animation.stuns
        self.objs.set_img(obj,arg.curr.data)
    def act_change_color(self,obj,arg):
        obj.set_color(arg.next())
        self.objs.set_img(obj)
    def act_change_geom(self,obj,arg):
        obj.geom = arg.next()
        self.objs.set_img(obj)
    def act_change_theme(self,obj,arg:str):
        mixer.music.stop()
        self.set_theme(arg)
        self.play_theme()
    def act_message(self,obj,arg):
        """arg can be an integer index of the line of text you want
        from the stored texts file, or it can be a unique string"""
        if isinstance(arg,int):
            try:msg = self.texts[arg]
            except IndexError:msg = ""
        else:msg = arg
        self.map.set_disp_msg(msg)
    def act_rotate(self,obj,arg:int):
        """Rotate the given object by 90 degrees times the rotation (arg)"""
        for i in range(arg):
            obj.rotate_right()
            self.objs.set_sprite(obj,obj.img)
            obj.animate = {"w":obj.img,"a":obj.img,"s":obj.img,"d":obj.img}
    def act_quit(self,obj,arg):
        self.quit = True
    def act_sound(self,obj,arg:str):
        """arg: sound path"""
        self.add_sound(arg,arg)
        self.play_sound(arg)
    def act_unlock(self,obj,arg):
        """arg: name of action to unlock"""
        for targ_act in self.acts.acts:
            if targ_act.name == arg:
                targ_act.locked = False
    def act_lock(self,obj,arg):
        """arg: name of action to lock"""
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
        self.map.print_to_black(mixer)
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
            actor.true_x = arg[0]
            actor.true_y = arg[1]
            self.map.center_camera(actor.x,actor.y)
            self.set_render_one(actor)
            self.add_render_one(actor)
        self.set_sprites_in_objs()
        self.map.print_from_black(mixer)

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
        if obj.move in ["wasd","dirs","drive"]:
            self.map.center_camera(obj.x+obj.width()//2,obj.y-obj.height()//2)
    def set_movement(self,obj):
        """Take the true_x and true_y from obj to get the change in x and y.
        Get as close as to true_x and true_y as possible.
        Start at 0, see how close we can get to move_y and move_x."""
        x_target = int(obj.true_x - obj.x)
        y_target = int(obj.true_y - obj.y)
        obj.move_x = 0
        obj.move_y = 0
        x_change = 0
        y_change = 0
        if x_target != 0:
            x_change = (x_target)//(abs(x_target))
        if y_target != 0:
            y_change = (y_target)//(abs(y_target))
        max_found = False
        while not max_found:
            if self.can_move(obj,x_change,y_change):
                if obj.move_x != x_target:
                    obj.move_x += x_change
                if obj.move_y != y_target:
                    obj.move_y += y_change
            else:
                max_found = True
            if (obj.move_y == y_target and obj.move_x == x_target):
                max_found = True
        if x_target!=0 and y_target!=0:
            self.objs.render_objs.add(obj)
        if x_target!= 0 and obj.move_x==0:#hit a wall
            obj.true_x = obj.x
        if y_target!= 0 and obj.move_y==0:
            obj.true_y = obj.y

    def can_move(self, obj, x_change, y_change=0):
        """Check if there are any characters in the area that 
        the obj would take up. Takes literal change in x and y.
        Returns True if character can move in that diRECTion.""" # Collision
        assert abs(x_change)<2 and abs(y_change)<2,"x and y can only be -1, 0, or 1."
        yf = y_change + obj.y 
        ys = yf - obj.height()
        xs = x_change + obj.x 
        xf = xs + obj.width() 
        if x_change > 0:      xs = obj.x + obj.width()
        elif x_change < 0:    xf = obj.x
        if obj.geom not in ["line","skeleton"]:
            if y_change < 0: # Moving up.
                yf = obj.y - obj.height()
            elif y_change > 0: # Down.
                ys = obj.y + 1
        else:
            ys = yf # Geometry is the bottom line
        if len(self.map.geom) < yf -2 or ys < 0:
            return False
        if len(self.map.geom[0]) < xf -2 or xs < 0:
            return False
        for y in range(ys,yf+1):
            for x in range(xs,xf):
                if (y > len(self.map.geom) -2):
                    return False
                elif (x > len(self.map.geom[y]) -2):
                    return False
                if self.map.geom[y][x]:
                    return False
        return True
    
    # These functions are put into geom_set_dict, for quicker lookup than if statements.
    def geom_all(self,obj,boolean = 1):
        """Creates a hollow box of geometry (hollow is obviously faster than not)"""
        for y in range(obj.y - obj.height() +1,obj.y +1):
            x_end = min([obj.x + obj.width()-1,len(self.map.geom[y])])
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
        if (obj.min_width == None):
            [self.map.set_xy_geom(x + obj.x, obj.y, boolean)
            for x in range( min([obj.width(), len(self.map.geom[-1])-obj.x]) )]
        else:
            [self.map.set_xy_geom(x + obj.x, obj.y, boolean)
            for x in range( min([obj.get_min_width(), len(self.map.geom[-1])-obj.x]) )]
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
                            # This is an object that will never be used and cannot be walked through.
                            line.pop(i)
                        else:
                            i+=1
        self.objs.render_objs = set()
    def init_render_obj(self,obj):
        obj.top_y = obj.y-obj.height()+1
        obj.top_x = obj.x+obj.width()-1
        #start_y = obj.top_y
        end_y = min([obj.y+1,self.map.height-1])
        if obj.geom!="background":
            self.init_render_obj_geom(obj.top_y,end_y,obj,self.init_render_obj_append)
        else:
            self.init_render_obj_geom(obj.top_y,end_y,obj,self.init_render_obj_set)
    def init_render_obj_geom(self,start_y,end_y,obj,func):
        for y in range(start_y,end_y):
            start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.x
            end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.x+1,self.map.width])
            for x in range(start_x,end_x):
                char = obj.sprite[y-start_y][x-obj.x]
                if SKIP not in char:
                    func(y,x,char)
    def init_render_obj_append(self,y,x,char):
        self.map.rend[y][x].append(char)
    def init_render_obj_set(self,y,x,char):
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
        if map_name in self.mirrors.world_mirrors:
            for mir in self.mirrors.world_mirrors[map_name]:
                mir_type = self.mirrors.types[mir.mirror_name]
                if mir_type.color > -1:
                    mir_color = color_by_number(mir_type.color)
                    colored = True
                else:colored=False
                switch = bool(int(time()*3)%2) # Ripple Speed is 3 FPS.
                ripple_amt = int(mir_type.ripple) * -1 #-1 or 0
                for y in range(0,mir.y2-mir.y1+1):
                    switch = not switch
                    for x in range(0,mir.x2-mir.x1+1):
                        rend_x = mir.x1+(x*mir_type.x_mult)+mir.copy_x
                        if switch:
                            rend_x += ripple_amt
                        rend_y = mir.y1+(y*mir_type.y_mult)+mir.copy_y
                        char = self.map.rend[rend_y][rend_x][-1][-1]
                        if colored:
                            color = mir_color
                        else:
                            color = self.map.rend[rend_y][rend_x][-1][:-1]
                        #if char != BLANK:
                        #    color = brighten(color)
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
        player = self.map.camera_star
        #y = player.y-(player.height()//2)
        #self.map.center_camera(player.x+(player.width()//2),y)
        self.map.center_camera(player.x+4,player.y-4)

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