from textengine import COLORS as C
from math import log

spaces = " "
color_base = "\033[48;5;"
for x in range(16,256):
    color = color_base + str(x) + "m"
    try:spaces = " " * (3 - int(log(x,10)))
    except:pass
    print(f"{color}{x}{spaces}{C['default']}",end="")
    if (x-15)%6 == 0:
        print()