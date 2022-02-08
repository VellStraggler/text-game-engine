from pynput import keyboard
import time, threading

# Helpful in debugging information.
many_space = ' ' * 50
many_line = '\n' * 50

def grid_patcher(array:list):
    """
    TO BE USED ON MAP AND SPRITE ARRAYS.
    Adds spaces until the array is rectangular, then returns the list
    patched with spaces.
    """
    #find longest y:
    longest_y = 0
    #the length of output_map is the extent of y
    for y in range(0,len(array)):
        if len(array[y]) > longest_y:
            longest_y = len(array[y])
    #make all columns the same length
    for row in array:
        for s in range(0,longest_y - len(row)):
            row.append(" ")
    return array

#KEY LISTENING
def on_press(key):
    #must be called AFTER keyboard is 
    if key == keyboard.Key.esc:
        return False
    try: k = key.char
    except: k = key.name #for buttons like "left" or "space"
    if k in ['a','left']:
        pass
    elif k in ['w','up']:
        pass
    elif k in ['s','down']:
        pass
    elif k in ['d','right']:
        pass
    elif k == 'q':
        quit()

def can_be_read(filename:str):
    """Boolean function, check if file can be opened"""
    try:
        with open(filename,'r') as file:
            return True
    except: return False

class GameObject():
    """Initialization creates a map and a sprite list"""
    def __init__(self):
        self.map = Map()
        self.sprites = Sprites()

    def run_map(self):
        #Start up key listener.
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        
        # Begin the printing loop.
        # For now, game will be running within a terminal.
        while(True):
            self.map.print_all()

class Map():
    """Three arrays are stored in a Map object: the user input map, the output map, and a collision map.
    Set the map path upon initialization"""

    def __init__(self):
        self.path = ""
        self.input_map = [] # The input_map will always be exactly what is in the map file.
        self.output_map = [] # Requires data from the input map as well as sprites
        self.collision_map = [] # Requires data from the output map

    def translate(self):
        self.store_map()
        # Calls an array OUTSIDE the class.
        self.output_map = grid_patcher(self.input_map)

    def store_map(self):
        """
        Stores text from file as 2D array or list: [[x1,x2,x3],[x1,x2,x3]]
        Reads from the preset path, saves to input_map
        """
        with open(self.path,'r') as file:
            currentline = file.readline() # stores first line as string
            while currentline:
                xlist = [] # Begin a new row of items
                currentline = currentline[:-1] # Remove newline calls.
                for char in currentline:
                    xlist.append(char)
                self.input_map.append(xlist) # Add row to the input_map
                currentline = file.readline()
            
    def print_all(self):                     # \/ leaves space for variables
        for i in range(0,len(self.output_map) + 3):
            print('\033[A\033[F') # This will remove the previous printing of the map.
        for yrow in self.output_map:
            for yitem in yrow:
                # UPDATE: Add check to see if it's any different from the new character
                print(yitem,end="")
            print()
        print()
            
    def set_x_y(self,x,y,character):
        try:
            self.output_map[y][x] = character
        except:
            pass # For when this point would not print within the map.

    def draw_sprites(self,spritedict:dict):
        """looks at map, replaces characters with sprites"""
        for item in spritedict.items():
            for y in range(len(self.output_map)):
                for x in range(len(self.output_map[y])):
                    if item.input_char == self.output_map[x][y]:
                        self.add_array(item)

class Sprites():
    def __init__(self,sprites_path = ""):
        self.sprites_path = sprites_path
        self.sprites = []
    def get_sprites(self):
        lines = []
        with open(self.sprites_path, 'r',encoding='utf-8') as file:
            currentline = file.readline()
            while(currentline):
                if len(currentline) > 0:
                    if currentline[0] != '$':
                        lines.append(currentline)
            currentline = file.readline()
    def add(self,sprite):
        self.sprites.append(sprite)
    
class Sprite():
    def __init__(self,array="", input_char = "", coords = [-1,-1]):
        self.array = array
        self.originx = coords[0]
        self.originy = coords[1]
        self.geometry = "default"
        self.movement = False
        self.input_char = input_char 

    def set_origin(self,x,y):
        self.originx = x
        self.originy = y

    def set_xy_char(self,x,y,newchar):
        """
        Change a character at a given coordinate.
        """
        try:    self.array[y,x] = newchar
        except: pass
    def char(self,x:int,y:int):
        """
        Returns the character stored here in a sprite array.
        """
        try:    return self.array[y][x]
        except: return " "

    def topleft(self):
        """
        Return coordinate values [x,y] of topleft character in sprite.
        NOT in reference to map coordinates.
        """
        return [0,0]
    def bottomright(self):
        """
        Return coordinate values [x,y] of bottomright character in sprite.
        NOT in reference to map coordinates.
        """
        return [len(self.array)-1,len(self.array[len(self.array)-1])-1]

    def compile(self, lines:list):
        output_map = self.Map()
        sprites_file = ""
        
        #output_map.read_sprites(sprite_dict)
        #filter out any sprites that don't have a mapping character
        mappable_sprites = []
        for value in self.sprite_dict.values():
            # Check to see if this sprite has a map character
            if len(value.input_char)>0:
                mappable_sprites.append(value)
        for sprite in mappable_sprites:
        # GO through each character in the map, by ROW, then COLUMN
            for mapy in range(0,len(output_map.output_map)):
                for mapx in range(0,len(output_map.output_map[mapy])):
                    # Check if a sprite's map character is present on the map.
                    if output_map.output_map[mapy][mapx] == sprite.input_char:
                        output_map.output_map[mapy][mapx] = " "
                        # If it is, replace an area around that point with the sprite array.
                        for spritey in range(sprite.topleft()[0],sprite.bottomright()[0] + 1):
                            for spritex in range(sprite.topleft()[1],sprite.bottomright()[1] + 1):
                                # Only change the character if it has not already been changed
                                char_to_use = sprite.char(spritex,spritey)
                                if char_to_use != " " or (sprite.char(spritex-1,spritey) != " " and sprite.char(spritex+1,spritey) != " "):
                                    xpos = mapx + spritex - (sprite.bottomright()[1] // 2)
                                    ypos = mapy + spritey - sprite.bottomright()[0]
                                    if ypos >= 0 and xpos >= 0:
                                        output_map.set_x_y(xpos, ypos, char_to_use)
        
        return output_map