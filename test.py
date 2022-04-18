from textengine import CLEAR,RETURN,W_HEI,INFO_HEI
from time import sleep
def move_cursor(x=0,y=0):
    """Moves the cursor from its current position"""
    if x < 0:
        x *= -1
        print(f"\033[{x}D",end='',flush=True)
    elif x > 0:
        print(f"\033[{x}C",end="",flush=True)
    if y < 0:
        y *= -1
        #print(f"\033[{y}B",end='')
        print(f"\033[{y}A",end="",flush=True)
    elif y > 0:
        print("\n"*y,flush=True)

import textengine as tx
SIGN = "$"
BLANK = " "

def render_obj(sprite,x,y,color):
    # Print a sprite at its origin.
    print(RETURN,end="",flush=True)
    move_cursor(x,y)
    for row in sprite:
        line = color
        for char in row:
            line = line + char
        print(line)
        move_cursor(x)


sprite =   [["    _/| "],
            ["  ╱ ╱'_╲"],
            [" │_'| _╱"],
            ["   ╱ ⎺╲ "],
            ["  ╱ ╱_[ "],
            [" │_╱   ╲"],
            ["╱______│"]]
print(CLEAR,flush=True)
print("Hello Fools",flush=True)
render_obj(sprite,120,26,tx.COLORS['yellow'])
render_obj(sprite,50,13,tx.COLORS['green'])
render_obj(sprite,50,26,tx.COLORS['green'])
render_obj(sprite,50,13,tx.COLORS['green'])


char = "helpme"
new = char[char.index("m")+1]
print(new)
list2 = ["KILL ME"]
print(list2[0])
print(list2[-1])
list2.append("NOW")
print(list2[-1])