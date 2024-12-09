from math import log

CLEAR = "\033[2J"
# DIRPATH = dirname(__file__) + "/"
# DIRPATH = "C:/Users/david/OneDrive/Desktop/Programs_on_Standby/Programming/textengine/"
DIRPATH = "C:/Users/david/code_projects/my-projects/textgameengine/"

BLANK = ' '
SKIP = '$'
CUR = '\033[A\033[F'
MAX_TICK = 16
ANIMATE_FPS = 1/8
CHUNK_WID = 32
CHUNK_HEI = 16

WINDOW_WID = 110 #110, 60 for baby screen with 250 fps, 189 for fullscreen (and 30 fps)
WINDOW_HEI = 29  #29, 49 for fullscreen
# Based on the Windows Terminal window at default size.
INFO_HEI=2
RETURN = CUR * (WINDOW_HEI+INFO_HEI)
WINDOW_CUSHION_X = WINDOW_WID//2 - 5 
WINDOW_CUSHION_Y = WINDOW_HEI//2 
# WINDOW GUIDE CUSHION, the breathing room between the sprite between
# the window follows and the edge of the window.

SPACES = ' ' * 50
S_LINE = ' ' * WINDOW_WID
BUBBLE = [["╱","⎺","╲"],["|"],["╲","_","╱"]]
# /⎺⎺⎺⎺⎺⎺⎺\
#| message |
# \_______/

# Dictionary of chars (keys) and their opposites (values)
FLIP_CHARS = {'\\':'/','/':'\\','[':']',']':'[','{':'}','}':'{','<':'>',
    '>':'<','(':')',')':'(','◐':'◑','◑':'◐','↙':'↘','↘':'↙','כ':'c',
    'c':'כ','◭':'◮','◮':'◭','╱':'╲','╲':'╱','↖':'↗','↗':'↖','⌋':'⌊',
    '⌊':'⌋'}
H_FLIP_CHARS = {'\\':'/','/':'\\','↙':'↖','↘':'↗','כ':'c',
    'c':'כ','◭':'◮','◮':'◭','╱':'╲','╲':'╱','↖':'↙','↗':'↘',"_":"⎺",
    "⎺":"_","'":".",".":"'","A":"V","V":"A","M":"W","W":"M"}

COLOR_ESC = "\033[48;5;"
DEFAULT_COLOR = COLOR_ESC + "16m"
DEFAULT_TEXT  = "\033[38;5;15m"
NEW_SETTING = {"color":"mono","mono":"geom","geom":"color"}



def find_non(string,bad_c):
    """Returns the index of the first non-case of a character in a
    string. Returns 0 if not found"""
    for c in range(len(string)):
        if string[c]!=bad_c:
            return c
    return 0
def rfind_non(string,bad_c):
    """Starting from the end of a string, this returns the index of
    the first non-case of a character in a string. Returns 0 if not found"""
    for c in range(len(string)-1,-1,-1):
        if string[c]!=bad_c:
            return c
    return len(string)-1
def find_count(string,character):
    """Finds the number of times a given character occurs in a string."""
    count = 0
    for c in string:
        if c == character:
            count += 1
    return count
def find_indices(string,character):
    """Returns a list of indices of the occurrences of a given character in a string."""
    indices = list()
    i = 0
    for c in string:
        if c == character:
            indices.append(i)
        i+=1
    return indices
def linked_dict(list1:list,closed=False):
    """Create a linked list dictionary with a closed loop ending from a given list."""
    llist = dict()
    if len(list1) > 1:
        for i in range (len(list1)-1):
            llist[list1[i]] = list1[i+1]
        if closed:
            llist[list1[i+1]] = list1[i+1]
        else:
            llist[list1[i+1]] = list1[0]
    else:
        llist[list1[0]] = list1[0]
    return llist

def ms_gothic(line:str):
    line_dict = {'\\':'╲','│':'|','/':'╱'}
    line = [x for x in line]
    for x in range(len(line)):
        if line[x] in line_dict.keys():
            line[x] = line_dict[line[x]]
    return "".join(line)
def replace_spaces(line:str):
    """All spaces before and after other characters are replaced
    by the constant SKIP."""
    s1,s2 = True,True
    start,end = "",""
    for x in range((len(line)+1)//2):
        char = line[x]
        if char != BLANK or not s1: s1 = False
        else:   char = SKIP
        start = start + char

        char = line[len(line)-x-1]
        if char != BLANK or not s2: s2 = False
        else:   char = SKIP
        end = char + end
    if len(line)%2==0:
        return start + end
    else:
        return start[:-1] + end
def solidify_path(path,suffix=".txt"):
    if DIRPATH not in path:
        path = DIRPATH + path
    if suffix not in path:
        path += suffix
    return path
def deconstruct_path(path):
    path = path[path.rfind("/")+1:]
    if "." in path:
        path = path[:path.rfind(".")]
    return path

def color_by_num(x):
    if x < 16:
        x = PRE_16_COLORS[x]
    return (COLOR_ESC + str(x) + "m")
def num_by_color(x):
    if len(x) > 3:
        return (x[len(COLOR_ESC):-1])
    else:
        return x
def print_color_numbers():
    """For Debugging: Returns a sheet of all color numbers highlighted
    by their respective color."""
    spaces = " "
    black_words = "\033[38;5;" + str(BLACK_INT) + "m"
    white_words = "\033[38;5;" + str(WHITE_INT) + "m"
    for x in range(1,256):
        color = COLOR_ESC + str(x) + "m"
        try:spaces = " " * (9 - int(log(x,10)))
        except:pass
        print(f"{black_words}{color}{x}{white_words}{x}{spaces}{spaces}",end="")
        if (x-15)%6 == 0:
            print()
WHITE_INT = 231
BLACK_INT = 16 # SAME AS 232
PRE_16_COLORS = {1:160,2:34,3:172,4:20,5:90,6:68,7:252,8:243,
                9:167,10:40,11:192,12:32,13:127,14:44,15:WHITE_INT}
SHADE = 6
JUMP_SHADE = 36
def brighten(color_code:str,positive=True):
    """Takes a color escape code, returns a color escape code that
    is either darker(-) or brighter(+)."""
    if positive:change = 1
    else:change = -1
    if len(color_code)>len(COLOR_ESC):
        color = int(color_code[len(COLOR_ESC):color_code.find("m")])
    else:
        color = 232
    if color < BLACK_INT:
        return brighten(color_by_num(PRE_16_COLORS[color]))
    elif color > WHITE_INT: #MONOCHROME
        color += change
        if color <= WHITE_INT:
            color = BLACK_INT
        elif color > 255:
            color = WHITE_INT
    else:
        root = (color-BLACK_INT)%JUMP_SHADE
        if positive:
            if root >= JUMP_SHADE - SHADE:
                color = WHITE_INT
            else:
                color += (change*SHADE)
        else:
            if root < SHADE:
                color += (change*JUMP_SHADE)
            else:
                color += (change*SHADE)
        color = min([WHITE_INT,color])
        color = max([BLACK_INT,color])
    return color_by_num(color)