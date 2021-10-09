import tkinter as tk
from pynput import keyboard
import time, threading

def main():
    #get the name of the code to be used.
    code_file_name = 'textengine/example_code.txt'
    print(f'Using file path: {code_file_name}')
    #run this input loops until the file is usable
    '''
    while not can_be_read(code_file_name):
        print('Error: Incorrect File Name')
        code_file_name = input('Enter "example_code.txt": ')
    '''
    #read code line by line
    lines = store_code(code_file_name)
    
    #compile code
    map_array = compile(lines)

    #Start up key listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    #begin the printing loop
    #For now, game will be running within a terminal
    class printThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            print('Thread two running...')
        def run(self):
            while(True):
                map_array.print_all()
                time.sleep(.5)

    p_thread = printThread()
    p_thread.start()

class MapObject():
    def __init__(self):
        self.map_path = ''
        self.map_array = []

    def set_path(self,map_path):
        self.map_path = map_path
        self.store_map()
        self.map_patcher()

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
            

    def map_patcher(self):
        #adds spaces until the array is rectangular
        #find longest y:
        longest_y = 0
        #the length of map_array is the extent of y
        for y in range(0,len(self.map_array)):
            if len(self.map_array[y]) > longest_y:
                longest_y = len(self.map_array[y])
        #make all columns the same length
        for row in self.map_array:
            for s in range(0,longest_y - len(row)):
                row.append(" ")

    def print_all(self):
        for yrow in self.map_array:
            for yitem in yrow:
                print(yitem,end="")
            print()
    #function that takes a sprite from a spritesobject, as well as the 3 coords, adds it to the final printing
    #DAVID

            
class SpritesObject():
    #MATTHEW
    #one item is a dictionary of all sprites
    #remove \n from every line
    #sprite key name stores a 2d array of sprite and 3 lists of xy coords (the bottom center, top left, the bottom right)
        #e.g. 'character': [[['\\',' ','/'] , [' ','X',' '] , ['/',' ','\\']], [coordinatex,coordinatey], [corner coords...], []]
    #another item is the reverse data ($DATA$)
        #when a character turns, function will be called that looks at reverse data and
        #"is character in any string in the list"
        #"does it equal the first item? else switch to opposite item"
    #function to grab coordinates
    #function to grab sprite corners coordinates (top left, bottom right)
    #function to grab sprite itself
    pass

class VarObject():
    #DAVID
    #stores a variable and what it equals
    #it could equal a map, spritelist, sprite, a number
    #if it is a map,sprites, or sprite, it stores a classobject

class ClassObject():
    #DAVID
    #class type: map, sprite, sprites
    #xy, geometry, movement, collision FOR SPRITE ONLY

def compile(lines):
    #Store variables in a dictionary
    map_array = MapObject()
    sprite_array = SpritesObject()
    ()
    print(len(lines))
    for i in range(0,len(lines)):
        words = lines[i].split()
        if len(words) > 1:
            if words[1] == '=':
                #FOR VARIABLE DECLARATIONS
                if words[2].find(")") == len(words[2])-1:
                    #FOR CLASSES
                    #map, sprites, sprite
                    classtype = words[2][:words[2].find("(")]
                    if classtype == "sprite":
                        #DAVID
                        #Most common occurrence probably
                        #only do this if sprite sheet is declared
                        #have this refer to spritesobject
                        print(classtype)
                    elif classtype == "map":
                        #locate map file
                        mapname = dollar_word(words[2])
                        #create Map Object of file
                        map_array.set_path(mapname)
                        print(f'Map Found using path: {mapname}')
                    elif classtype == "sprites":
                        #MATTHEW
                        #take path, try to read
                        #if it can be read, iterate through, save everything to sprite_array
                        #i would put a function call here from the spriteobject class
                        #this same function will store information in $DATA$ 
                        print(classtype)
                    else: print(f'Error: Class type not recognized: Line {lines[i]}')
                elif words[0] == 'window_resolution':
                    print(f'Note: Resolution Found: {words[2]}')
                else:
                    print(f'No Assignment found on line {i}')
            else: print(f'Error: All lines of code should include an "=" assignment')
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
    if k in ['w', 'a', 's', 'd', 'left', 'right', 'up', 'down']:
        print('Key pressed: ' + k)

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