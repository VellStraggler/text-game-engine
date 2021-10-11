from pynput import keyboard
import time, threading

def main():
    #get the name of the code to be used.
    code_file_name = 'textengine/example_code.txt'
    print(many_line)

    #read code line by line
    lines = store_code(code_file_name)

    #compile code and return a map_array for printing
    map_array = compile(lines)

    #Start up key listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    #begin the printing loop
    #For now, game will be running within a terminal
    class printThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            #make sure this works?
        def run(self):
            while(True):
                #This While loop loops through 3 key items: framerate, map_printing, and map_updating
                map_array.print_all()
                time.sleep(.5)
                #update_map()

    p_thread = printThread()
    p_thread.start()

#helpful in debugging information
many_space = ' ' * 50
many_line = '\n' * 50

def grid_patcher(array:list):
    """
    TO BE USED ON MAP ARRAYS AND SPRITE ARRAYS.
    adds spaces until the array is rectangular, then returns the patched list
    """
    #find longest y:
    longest_y = 0
    #the length of map_array is the extent of y
    for y in range(0,len(array)):
        if len(array[y]) > longest_y:
            longest_y = len(array[y])
    #make all columns the same length
    for row in array:
        for s in range(0,longest_y - len(row)):
            row.append(" ")
    return array

class MapObject():
    def __init__(self):
        self.map_path = ''
        self.map_array = []

    def set_path(self,map_path):
        self.map_path = map_path
        self.store_map()
        #calls an array OUTSIDE the class
        self.map_array = grid_patcher(self.map_array)

    def store_map(self):
        #stores text from file as 2D array or list: [[x1,x2,x3],[x1,x2,x3]]
        with open(self.map_path,'r') as file:
            currentline = file.readline() #a string
            while currentline:
                xlist = []
                #remove any newline calls
                currentline = currentline[:-1]
                for char in currentline:
                    xlist.append(char)
                self.map_array.append(xlist)
                currentline = file.readline()
            
    def print_all(self):
        for i in range(0,len(self.map_array)):
            print('\033[A\033[F')
        for yrow in self.map_array:
            for yitem in yrow:
                print(yitem,end="")
            print()
            
    def set_x_y(self,x,y,character):
        try:
            self.map_array[x][y] = character
        except:
            pass

    def read_sprites(self,spritedict):
        #looks at map, replaces characters with sprites
        for item in spritedict.items():
            for y in self.map_array:
                for x in self.map_array:
                    if item.get_map_char() == self.map_array[x][y]:
                        self.add_array(item)

    #NOTE: NOT CALLED
    def add_sprites(self,sprite_list:dict):
        #takes a spritelist, as well as the 3 coords, adds it to the final printing
        #3 coords are stored within each sprite
        #spawnpoint is relative to map, other two coords are relative to the sprite
        for sprite in sprite_list:
            self.add_array(sprite)

    #NOTE: NOT CALLED 
    def add_array(self,sprite):
        for x in range(sprite.topleft()[0],sprite.bottomright()[0]+1):
            for y in range(sprite.topleft()[1],sprite.bottomright()[1]+1):
                try:
                    self.map_array[x+sprite.origin()[0]][y+sprite.origin()[1]] = sprite.array[x][y]
                except:
                    print(f'{many_space}Successfully printed NOT out of range.')

class VarObject():
    def __init__(self,variable, value):
        #stores a variable and what it equals
        self.variable = variable
        self.value = value
        #This is for any variable that is NOT a class
        #eg 4, "hello"

class ClassObject():
    #iterations of this are to be stored in a regular dictionary
    """
    functions: set_xy(coordlist), set_array(array), set_map_char(char), set_movement(boolean),
    origin(), topleft(), bottomright()
    """
    #class type: map, sprite, sprites
    #origin, movement FOR SPRITE ONLY
    def __init__(self,array):
        self.array = array
        #the values below will simply not be called if the Classobject is a map or spritesheet
        self.originx = 6
        self.originy = 6 
        #self.geometry = "default"
        self.movement = False
        self.on_map = "є"

    def get_array(self):
        return self.array
    def set_array(self,array:list):
        self.array = array

    def get_map_char(self):
        return self.on_map
    def set_map_char(self,char):
        self.on_map = char

    def set_movement(self,can_move:bool):
        self.movement = can_move

    def origin(self):
        #return the bottom LEFT coordinate. If length is not odd, picks the left one
        #return list([len(self.array)-1,int((len(self.array[len(self.array)-1])-1))])
        return list(self.originx,self.originy)
    def get_originx(self):
        return int(self.originx)
    def get_originy(self):
        #return int(( len(self.array[len(self.array)-1])-1 ))
        return int(self.originy)
    def set_xy(self,x,y):
        try:
            self.originx = x
            self.originy = y
        except:
            pass
    def get_xy(self,x,y):
        try:
            return self.array[x][y]
        except:
            return ' '

    def topleft(self):
        #get coordinate values, not the character stored in them!
        return [0,0]
    def bottomright(self):
        return [len(self.array)-1,len(self.array[len(self.array)-1])-1]

def compile(lines:list):
    #Store variables in dictionaries
    map_array = MapObject()
    var_container = {}
    #\/ This CAN contain copies of sprites that are named by the user 
    example_instance = ClassObject([['h','o'],['o','h']])
    sprite_dict = {'test':example_instance}
    sprites_file = ''
    #sprite_dict = {'tree':classobjinstance()}
    #classobjinstance.array = []
    for i in range(0,len(lines)):
        words = lines[i].split()
        if len(words) > 1:
            #FOR VARIABLE DECLARATIONS
            if words[1] == '=':
                #FOR CLASSES
                if words[2].find(")") == len(words[2])-1:
                    #map, sprites, sprite
                    classtype = words[2][:words[2].find("(")]
                    if classtype == "sprite":
                        #Most common occurrence probably
                        #only do this if sprite sheet is declared
                        if len(sprite_dict) > 0:
                            is_in_sprites = False
                            #tree = sprite($tree$)
                            var_value = dollar_word(words[2])
                            for key in sprite_dict.items():
                                if var_value == key[0]:
                                    is_in_sprites = True
                            if is_in_sprites:
                                #add duplicate sprite into dictionary under user-made
                                #variable name = words[0]
                                sprite_dict[words[0]] = sprite_dict[var_value]

                    elif classtype == "map":
                        #locate map file
                        mapname = dollar_word(words[2])
                        #create Map Object of file
                        map_array.set_path(mapname)

                    elif classtype == "sprites":
                        #take path, try to read
                        sprites_path = dollar_word(words[2])
                        #if it can be read, iterate through, save everything to sprite_dict
                        sprites_file = store_code(sprites_path)
                        #i would put a function call here from the spriteobject class                        
                        key = ""
                        one_sprite_array = []
                        for line in sprites_file:
                            if line[0] == "$":
                                #turn off sprite-line-reading:
                                if len(one_sprite_array) != 0:
                                
                                    sprite_dict[key] = ClassObject(one_sprite_array)
                                    #reset sprite array for reuse
                                    one_sprite_array = []
                                key = dollar_word(line)
                            else:
                                one_sprite_array.append([char for char in line if char != "\n"])
                        #this same function will store information in $DATA$ 
                    else: print(f'{many_space}Error: Class type not recognized: Line {lines[i]}')
                #ADDING CLASS DATA
                #search for a period. This implies changing class data
                elif words[0].find('.') != -1:
                    #look at word before '.'
                    varname = words[0][:words[0].find('.')]
                    attr = words[0][words[0].find('.')+1:]
                    att_value = words[2]
                    for key in sprite_dict.items():
                        if varname == key[0]:
                            if attr == 'xy' and att_value.find(',') != -1:
                                attx = int(att_value[:att_value.find(',')])
                                atty = int(att_value[att_value.find(',')+1:])
                                key[1].set_xy(attx,atty)
                                print(f'line 258: {attx}, {atty}')
                            elif attr == 'movement':
                                key[1].set_movement(att_value == 'true')
                            elif attr == 'on_map':
                                key[1].set_map_char(dollar_word(att_value))
                #BASIC VARIABLE ASSIGNMENT
                else:
                    var_container[words[0]] = words[2]
            else: print(f'{many_space}Error: All lines of code should include an "=" assignment')
    
    #map_array.read_sprites(sprite_dict)
    
    #goes through each character in the map
    for x in range(0,len(map_array.map_array)-1):
        for y in range(0,len(map_array.map_array[x])-1):
            for value in sprite_dict.values():
                #check if a sprite's map character is present on the map
                if map_array.map_array[x][y] == value.get_map_char():
                    print(f'x:{x}  y:{y} char:{value.get_map_char()}')
                    for x in range(value.topleft()[0],value.bottomright()[0]+1):
                        for y in range(value.topleft()[1],value.bottomright()[1]+1):
                            map_array.set_x_y(x + value.get_originx(),y + value.get_originy(), value.get_xy(x,y))
    #map_array.add_sprites(sprite_dict)
    '''
    for sprite in sprite_dict.values():
        if sprite.map
        for x in range(sprite.topleft()[0],sprite.bottomright()[0]+1):
            for y in range(sprite.topleft()[1],sprite.bottomright()[1]+1):
                #try:
                map_array.set_x_y(x + sprite.originx(),y+sprite.originy(),sprite.get_xy(x,y))
                #except:
                    #print(f'{many_space}Successfully printed NOT out of range.')
                    '''
    print(many_line)
    return map_array

#simple function to find words between $ signs
def dollar_word(word):
    word = word[(word.find('$') + 1):]
    return word[:(word.find('$'))]

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

#FILE READING
def can_be_read(filename):
    #boolean function, check if file can be opened
    try: file = open(filename,'r')
    except: return False
    file.close()
    return True

def store_code(code_file_name):
    lines = []
    #Storing the code line by line
    #Empty lines and comment lines are skipped
    #read-only
    with open(code_file_name, 'r') as code:
        currentline = code.readline()
        while(currentline):
            if len(currentline) > 0:
                if currentline[0] != '#':
                    lines.append(currentline)
            currentline = code.readline()
    return lines
    #returns a list of strings

main()