from os import system
from textengine import print_color_numbers
system("")
from math import log
def print_colors_with_gradients():
    """For Debugging: Returns a sheet of all color numbers highlighted
    by their respective color."""
    spaces = " "
    color_base = "\033[48;5;"
    fore_base = "\033[38;5;"
    gradient = " ░▒▓"
    for x in range(256):
        color = color_base + str(x) + "m"
        for fore in range(256):
            foreground = fore_base + str(fore) + "m"
            print(f"{foreground}{color}{gradient}",end="")
        if (x-15)%6 == 0:
            print()
        
#print_colors_with_gradients()
print_color_numbers()
input()