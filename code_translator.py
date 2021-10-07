import tkinter as tk
from pynput import keyboard

def main():
    #get the name of the code to be used.
    code_file_name = input('Enter "code.txt": ')
    #run this input loops until the file is usable
    while not can_be_read(code_file_name):
        print('Error: Incorrect File Name')
        code_file_name = input('Enter "example_code.txt": ')
    #read code line by line
    lines = store_code(code_file_name)
    
    #translate code
    translate(lines)

    #Start up key listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()

    #begin the printing loop
    #For now, game will be running within a terminal

def translate(lines):
    #Store variables in a dictionary
    for line in lines:
        words = line.split(" ")
        if words[1] == '=':
            #FOR VARIABLE DECLARATIONS
            if words[2].find("("):
                #FOR CLASSES
                #map, sprites, sprite
                classtype = words[2][:words[2].find("(")]
                if classtype == "sprite":
                    #Most common occurrence probably
                    print(classtype)
                elif classtype == "map":
                    print(classtype)
                elif classtype == "sprites":
                    print(classtype)
                else: print(f'Error: Class type not recognized: Line {line}')


            
        
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
        currentline = code_file_name.readline()
        if len(currentline) > 0:
            if currentline[0] != '#':
                lines.append(currentline)
    return lines
    #returns a list of strings

def store_map(map_file_name):
    #Store map in 2D Array
    map_array = [[]]
    with open(map_file_name,'r') as file:
        currentline = file.readline()
        y = 0
        while currentline:
            for x in range(0,len(currentline)):
                map_array[y][x] = currentline[x]
            y += 1
            currentline = file.readline()
    return map_array()

main()