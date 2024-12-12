import math
from linked import Linked
from statics import color_by_number, ANIMATE_FPS, BLANK, CHUNK_HEI, CHUNK_WID, DEFAULT_COLOR, FLIP_CHARS, SKIP

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
    
    def set_img(self,obj,img=None):
        if img == None: img = obj.img
        self.render_objs.add(obj)
        obj.img = img

    def set_sprite(self,obj):
        """Change the sprite of an object.
        Deprecated method. use obj.set_sprite()"""
        obj.set_sprite(self.sprites)
    
    def set_sprite_color(self,obj):
        """Deprecated method. Use obj.set_sprite_color()"""
        obj.set_sprite_color()

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
        xy = [obj.x,obj.y]
        chunk = self.find_obj_chunk(xy[0],xy[1])
        line = chunk[xy[1]%CHUNK_HEI]
        i = self.find_obj_index(obj,chunk)
        if len(line) > 0:
            line.pop(i)
    def init_obj(self,obj):
        self.set_sprite(obj)
        if obj.animate == "flip":
            original = obj.img
            flipped_img = reversed(obj.img)
            self.sprites[flipped_img] = self.get_flipped_sprite(self.sprites[obj.img],obj)
            obj.animate = {"w":obj.img,"a":flipped_img,"s":obj.img,"d":original}
        elif obj.animate == None:
            obj.animate = {"w":obj.img,"a":obj.img,"s":obj.img,"d":obj.img}
        elif obj.animate == "sneaky":
            # First frame MUST be right-facing
            # and to be the reverse of facing left.
            # It looks for the object image with "-w" and "-s" added at the end
            assert (obj.img + "-w") in self.sprites.keys(), "img_name-w required."
            assert (obj.img + "-s") in self.sprites.keys(), "img_name-s required."
            facing_up = obj.img + "-w"
            facing_down = obj.img + "-s"
            facing_left = obj.img + "-a"
            self.sprites[facing_left] = self.get_flipped_sprite(self.sprites[obj.img],obj)
            obj.animate = {"w":facing_up,"a":facing_left,"s":facing_down,"d":obj.img}
        else:
            # Animation given is a Linked List of sprite names
            obj.animation = obj.animate
            obj.animate = None
            # This is where an idle animation is put in.
        self.append_obj_ordered(obj)
    def add_to_pallete(self,obj):
        obj_clone = self.copy(obj) #reset coords
        self.pallete_objs.add(obj_clone)

    def new(self,img, char, x=-1,y=-1, geom = "all",
        move = None, xspeed = 1, yspeed = 1, hp =1,face_right=True,
        face_down=False, grav=False,dmg = 1, enemy_chars=[],
        dmg_dirs=[], animate=None,txt=-1,max_jump=1,
        color="",data=dict(), rotation=0):
        """Creates an Obj and appends it to the objs list."""
        obj = self.Obj(img, char, x,y, geom, move,xspeed,yspeed,
            hp,face_right,face_down,grav,dmg,enemy_chars,dmg_dirs,
            animate,txt,max_jump,color,data, rotation)
        self.add_to_pallete(obj)

    def copy(self,o,new_x=-1,new_y=-1):
        """Returns a duplicate of an object."""
        obj = self.Obj(o.img, o.char, new_x,new_y, o.geom, o.move, o.xspeed, o.yspeed,
            o.hp, o.face_right, o.face_down, o.grav, o.dmg, o.enemy_chars, o.dmg_dirs,
            o.animate,o.txt,o.max_jump,o.color,o.data, o.rotation)
        return obj
    
    class Obj():
        def __init__(self,img:str, char:str, x:int = -1, y:int = -1, geom:str = "all",
        move = None, xspeed:int = 1, yspeed:int = 1, hp:int = 1, face_right:bool = True,
        face_down:bool = False, grav:bool = False, dmg = 1,enemy_chars:list = [],
        dmg_dirs:list=[], animate = None,txt:int = -1, max_jump = 1, color = "",
        data:dict = dict(), rotation:int = 0):
            
            # For TextEngine Devs: 
            # Any changes made to the variables here must also be reflected in
            # Game.new_object, Objs.new, objs.copy

            self.static = False
            self.move = move # None, leftright, wasd, dirs.
            self.grav = grav
            if move == None and not grav and animate == None:
                self.static = True
            #else:
            self.xspeed = xspeed
            self.yspeed = yspeed
            self.max_jump = max_jump
            self.move_x = 0
            self.move_y = 0
            if not self.static:
                #wasd: controls, i:interact, g:gravity (falling)
                self.move_time = {"w":0,"a":0,"s":0,"d":0,"i":0,"g":0}
                self.init_touching()
                self.jump = 0 # based on yspeed

                self.direction = 0 # in degrees, 0 to 360
                self.velocity_x = 0
                self.velocity_y = 0
                self.acceleration = .05
                self.friction = .99

            self.img = img
            self.sprite = [] # Must be set through Objs function new().
            self.geom = geom # Options of: None, line, complex, skeleton, background, or all.
            self.x = int(x)
            self.y = int(y)
            self.true_x = x # Float point x coordinate
            self.true_y = y
            self.top_x = x
            self.top_y = y
            self.char = char
            self.hp = hp
            self.enemy_chars = enemy_chars
            self.dmg = dmg
            self.dmg_dirs = dmg_dirs

            self.animate = animate # Edited in the objs.append_obj function
            self.idle_animation = Linked([img]) # When doing NOTHINg. NOT IMPLEMENTED
            self.animation = Linked([img])
            self.framerate = ANIMATE_FPS
            self.frame_time = 0
            self.stunned = False

            self.color = self.interpret_color(color)
            # "flip" is default, mirrors the image for every change between right and left.
            # Otherwise, if it's not None it becomes a dictionary: {w,a,s,d:sprite images.}            
            self.txt = txt # line number from textsheet
            self.reflect_x = 0
            self.reflect_y = 0
            self.face_right = face_right # Left: False, Right: True
            self.face_down = face_down # Up: False, Down: True
            self.rotation = rotation # 0 through 3
            self.data = data

        def accelerate(self, mult:int = 1):
            """Accelerate in current direction"""
            rad = math.radians(self.direction)
            self.velocity_x += math.cos(rad) * self.acceleration * mult
            self.velocity_y += math.sin(rad) * self.acceleration * mult
        
        def apply_friction(self):
            """Slow down over time"""
            self.velocity_x *= self.friction
            self.velocity_y *= self.friction

        def get_image(self):
            # Take length of sprite sheet
            interval = self.animation.len / 360
            # Get rounded sprite image (unless you really do have 360 angles)
            return self.animation.get(int(interval * self.direction))

        def init_touching(self):
            self.touching = {"up":set(),"down":set(),"left":set(),"right":set(),"inside":set()}

        def set_sprite(self, objs_sprites):
            """objs_sprites should come from instantiated Objs"""
            self.sprite = []
            [self.sprite.append(list(row)) for row in objs_sprites[self.img]]
            # [self.sprite.append(list(row)) for row in self.sprites[self.img]]
            self.set_sprite_color()
            self.rotation = 0
            self.img = self.img

        def interpret_color(self,color):
            if type(color) == type(42):
                self.color = color_by_number(color)
            else:
                self.color = color # The literal escape code (or blank), not the number.
            return self.color
        
        def set_sprite_color(self):
            chars = [SKIP]
            if self.geom == "skeleton":
                chars.append(BLANK)
            for y in range(self.height()):
                for x in range(self.width()):
                    char = self.sprite[y][x]
                    if chars[-1] == char:
                        char = SKIP # Turn any BLANKS into SKIPS
                    if char != SKIP:
                        char = self.color + char
                    self.sprite[y][x] = char
            
        def width(self,y=0):
            return len(self.sprite[y])
        def height(self):
            return len(self.sprite)
        def set_obj_coords(self):
            self.top_x += self.move_x
            self.top_y += self.move_y
            self.x += self.move_x
            self.y += self.move_y
            """if self.move_x != 0:
                self.true_x = self.x
            if self.move_y != 0:
                self.true_y = self.y"""
            self.move_x = 0
            self.move_y = 0

        def set_rotation(self,rotate:int = 0):
            """Rotates the object sprite 90 degrees 
            times the rotate var."""
            while rotate != self.rotation:
                self.rotation = (self.rotation + 1)%4
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
