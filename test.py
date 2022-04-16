from textengine import CLEAR
from time import sleep
def move(x=0,y=0):
    """Moves the cursor from its current position"""
    if x < 0:
        x *= -1
        print(f"\033[{x}D",end='')
    elif x > 0:
        print(f"\033[{x}C",end="")
    if y < 0:
        y *= -1
        print(f"\033[{y}B",end='')
    elif y > 0:
        print(f"\033[{y}A",end="")

print(CLEAR,"This is a long sentence!",end="")
for x in range(10):
    move(10,-x)
    print("!",end='')
for x in range(10):
    move(-x,10)
    print("!",end='')