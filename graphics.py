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

class Rect():
    def __init__(self,left_x, top_y, right_x, bot_y):
        self.left = left_x
        self.top = top_y
        self.right = right_x
        self.bot = bot_y
        self.fulfilled = False

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
    def get_char_img_order_old(self,char_img,base_x,base_y,char_img_orders):
        for x in range(len(char_img[0])):
            make_block = False
            left_x = base_x + (x*SCALE)
            right_x = base_x + ((x+1)*SCALE)
            for y in range(len(char_img)):
                if not char_img[y][x]: #black
                    if not make_block:
                        make_block = True
                        top_y = base_y + (y*SCALE)
                    bot_y = base_y + ((y+1)*SCALE)
                elif make_block:
                    char_img_orders.append(Rect(left_x, top_y, right_x, bot_y))
                    #self.canvas.create_rectangle(left_x, top_y, right_x, bot_y,fill="black",width=0)
                    make_block = False
            if make_block:
                char_img_orders.append(Rect(left_x, top_y, right_x, bot_y))
                #self.canvas.create_rectangle(left_x, top_y, right_x, bot_y,fill="black",width=0)
                make_block = False
        return char_img_orders
    def get_char_img_order(self,char_img,base_x,base_y,char_img_orders):
        for x in range(len(char_img[0])):
            left_x = base_x + (x*SCALE)
            right_x = base_x + ((x+1)*SCALE)
            for y in range(len(char_img)):
                if not char_img[y][x]: #black
                    top_y = base_y + (y*SCALE)
                    bot_y = base_y + ((y+1)*SCALE)
                    char_img_orders.append(Rect(left_x, top_y, right_x, bot_y))
                    self.pixel_count += 1
        return char_img_orders

    def print_frame(self,char_list):
        """Take a string that's usually printed in-terminal, and
        instead print them on the canvas."""
        self.canvas.delete("all") # Remove previous frame, faster than white box fill
        x = 0
        y = 0
        c_count = 0
        self.rect_count = 0
        self.pixel_count = 0
        char_img_orders = []
        for c in char_list:
            if c_count == 110:
                y += SCALE*CHAR_HEI
                x = 0
                c_count = 0
            else:
                if c != " ":
                    char_img = self.interpret_char(c)
                    char_img_orders = self.get_char_img_order(char_img,x,y,char_img_orders)
                x += SCALE*CHAR_WID
            c_count += 1
        vertical_lines = dict()
        horizontal_lines = dict()
        for rect in char_img_orders:
            # Connect vertical lines into singular rectangles
            if rect.left not in vertical_lines.keys():
                vertical_lines[rect.left] = []
            vertical_lines[rect.left].append(rect) # 1. Sort them into columns
            if rect.top not in horizontal_lines.keys():
                horizontal_lines[rect.top] = []
            horizontal_lines[rect.top].append(rect) # 2. Sort them into rows
        for c in horizontal_lines.values():
            if len(c) > 1:
                i = 0
                rect_len = 1
                while i < len(c)-1:
                    rect1 = c[i]
                    rect2 = c[i+1]
                    if rect1.right == rect2.left:
                        rect1.right = rect2.right
                        rect_len += 1
                        rect2.fulfilled = True
                        c.pop(i+1)
                    else:
                        if rect_len > 1:
                            rect1.fulfilled = True
                            self.canvas.create_rectangle(rect1.left, rect1.top, rect1.right, rect1.bot,fill="black",width=0)
                            self.rect_count += 1
                        i += 1

        for c in vertical_lines.values():
            if len(c) > 1:
                i = 0
                rect_len = 1
                while i < len(c)-1:
                    rect1 = c[i]
                    rect2 = c[i+1]
                    if not rect1.fulfilled:
                        if rect1.bot == rect2.top and not rect2.fulfilled:
                            rect1.bot = rect2.bot
                            rect_len += 1
                            rect2.fulfilled = True
                            c.pop(i+1)
                        else:
                            rect1.fulfilled = True
                            self.canvas.create_rectangle(rect1.left, rect1.top, rect1.right, rect1.bot,fill="black",width=0)
                            self.rect_count += 1
                            i += 1
                    else:
                        i += 1
                if not rect1.fulfilled:
                    rect1.fulfilled = True
                    self.canvas.create_rectangle(rect1.left, rect1.top, rect1.right, rect1.bot,fill="black",width=0)
                    self.rect_count += 1
            if not c[0].fulfilled:
                self.canvas.create_rectangle(c[0].left, c[0].top, c[0].right, c[0].bot,fill="black",width=0)
                c[0].fulfilled = True
                self.rect_count += 1

        for rect in char_img_orders:
            if not rect.fulfilled:
                self.canvas.create_rectangle(rect1.left, rect1.top, rect1.right, rect1.bot,fill="black",width=0)
                self.rect_count += 1
        
        print("\033[2J" + "Saved " + str(self.pixel_count - self.rect_count) + " rectangles.")
        self.canvas.pack(fill = BOTH, expand = 1)
        self.canvas.update()