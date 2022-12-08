from tkinter import Tk, Canvas, Frame, BOTH, NW
import imageio.v2 as iio
from os.path import dirname
DIRPATH = dirname(__file__) + "/"
SCALE = 2
CHAR_HEI = 6
CHAR_WID = 3
WINDOW_HEI = 29 * SCALE * CHAR_HEI
WINDOW_WID = 110 * SCALE * CHAR_WID
IMG_CHRS = "\/_-⎺█.';?!#[](){}│|↗↙↘↖ABCDEFGHIJKLMNOPQRSTUVWXYZ13456789" + "⅃" + "r" + '"' + ":═=ox><^v▀▄i⟘┤├,`n$$$$"
SPECIAL_CASE_CHRS = {"╲":0,"╱":1,"—":3,"0":38,"p":39,"2":49}
def string_to_dict(string):
    newdict = dict()
    for i in range(len(string)):
        newdict[string[i]] = i 
    return newdict
def add_to_dict_from_dict(supplier:dict, receiver:dict):
    for key in supplier.keys():
        receiver[key] = supplier[key]
    return receiver
IMG_CHRS_DICT = add_to_dict_from_dict(SPECIAL_CASE_CHRS,string_to_dict(IMG_CHRS))

CHAR_SHEET_PATH = DIRPATH + "pixel_char_sheet_18.png"

class Graphics(Frame):
    def __init__(self):
        super().__init__()
        self.chars_img = iio.imread(CHAR_SHEET_PATH)
        self.ci_width = len(self.chars_img[0])
        self.ci_height = len(self.chars_img) #images are always rectangular
        self.initUI()
    def initUI(self):
        self.master.title("Texillica ver. 2")
        self.pack(fill = BOTH, expand = 1)
        self.canvas = Canvas(self)
        self.canvas.pack(fill = BOTH, expand = 1)
        self.rect_count = 0

    def interpret_char(self, char:chr):
        """Take a character and return its sister boolean, image array from the
        pixel_char_sheet."""
        if char not in IMG_CHRS_DICT.keys():
            char = "#"
        index = IMG_CHRS_DICT[char]
        base_x = (index * CHAR_WID)%self.ci_width
        base_y = (((index * CHAR_WID)//self.ci_width)*CHAR_HEI)%self.ci_height
        img_array = []
        for y in range(base_y,base_y+CHAR_HEI):
            img_line = list()
            for x in range(base_x,base_x+CHAR_WID):
                img_line.append(int(bool(self.chars_img[y][x][1])))
                #Takes only the green value, something black does not have but blue does
                #Turns it into a boolean
            img_array.append(img_line)
        return img_array
    def print_char_img(self,char_img,base_x,base_y):
        for x in range(len(char_img[0])):
            make_block = False
            top_x = base_x + (x*SCALE)
            bot_x = base_x + ((x+1)*SCALE)
            for y in range(len(char_img)):
                if not char_img[y][x]: #black
                    if not make_block:
                        make_block = True
                        top_y = base_y + (y*SCALE)
                    bot_y = base_y + ((y+1)*SCALE)
                elif make_block:
                    self.canvas.create_rectangle(top_x, top_y, bot_x, bot_y,fill="black",width=0)
                    self.rect_count += 1
                    make_block = False
            if make_block:
                self.canvas.create_rectangle(top_x, top_y, bot_x, bot_y,fill="black",width=0)
                self.rect_count += 1
                make_block = False

    def print_frame(self,char_list):
        """Take a string that's usually printed in-terminal, and
        instead print them on the canvas."""
        self.canvas.delete("all") # Remove previous frame, faster than white box fill
        x = 0
        y = 0
        c_count = 0
        self.rect_count = 0
        for c in char_list:
            if c_count == 110:
                y += SCALE*CHAR_HEI
                x = 0
                c_count = 0
            else:
                if c != " ":
                    char_img = self.interpret_char(c)
                    self.print_char_img(char_img,x,y)
                x += SCALE*CHAR_WID
            c_count += 1
        print(self.rect_count)
        self.canvas.pack(fill = BOTH, expand = 1)
        self.canvas.update()