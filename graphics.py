from tkinter import Tk, Canvas, Frame, BOTH, NW
import imageio.v2 as iio
from os.path import dirname
import threading
DIRPATH = dirname(__file__) + "/"
SCALE = 2
CHAR_HEI = 6 # see create_line_char_dirs
CHAR_WID = 3
WINDOW_HEI = 29 * SCALE * CHAR_HEI
WINDOW_WID = 110 * SCALE * CHAR_WID
IMG_CHRS = "\/_-⎺█.';?!#[](){}│|↗↙↘↖ABCDEFGHIJKLMNOPQRSTUVWXYZ13456789" + "⅃" + "r" + '"' + ":═=ox><^v▀▄i⟘┤├$$n$$$$" 
def create_line_char_dirs():
    """DEPENDENT ON CHAR_HEI and CHAR_WID BEING 6 AND 3."""
    line_chr_indices = {0:[0,7],1:[3,4],20:[3,6],21:[1,4],22:[0,5],23:[2,7]}
    pt_to_xy = {0:[0,0],1:[0,2],2:[0,3],3:[0,5],4:[2,0],5:[2,2],6:[2,3],7:[2,5]}
    for key in line_chr_indices.keys():
        pt_pair = line_chr_indices[key]
        xy1 = pt_to_xy[pt_pair[0]]
        xy2 = pt_to_xy[pt_pair[1]]
        xyxy = [xy1[0] * SCALE, xy1[1] * SCALE, xy2[0] * SCALE, xy2[1] * SCALE]
        line_chr_indices[key] = xyxy
    return line_chr_indices
# Takes 2 points from below for making a diagonal line
# 0  .  4
# .  .  .
# 1  .  5
# 2  .  6
# .  .  .    
# 3  .  7
LINE_CHR_INDICES = create_line_char_dirs()
SPECIAL_CASE_CHRS = {"╲":0,"╱":1,"—":3,"0":38,"p":39,"2":49,",":20,"`":22}
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

        self.char_imgs = dict() # {index:img_array}
        self.make_char_imgs()
        self.char_rect_orders = dict() # {char:rect_order}
        self.make_rect_orders()

        self.initUI()
    def initUI(self):
        self.master.title("Texillica ver. 2")
        self.pack(fill = BOTH, expand = 1)
        self.canvas = Canvas(self)
        self.canvas.pack(fill = BOTH, expand = 1)
        self.rect_count = 0

    def make_char_imgs(self):
        for c in IMG_CHRS_DICT.keys():
            self.make_char_img(c)
        
    def make_char_img(self, char:chr):
        """Take a character and create its sister boolean, image array from the
        pixel_char_sheet."""
        index = IMG_CHRS_DICT[char]
        if index not in self.char_imgs.keys():
            base_x = (index * CHAR_WID)%self.ci_width
            base_y = (((index * CHAR_WID)//self.ci_width)*CHAR_HEI)%self.ci_height
            img_array = []
            for y in range(base_y,base_y+CHAR_HEI):
                img_line = list()
                [img_line.append(int(bool(self.chars_img[y][x][1]))) for x in range(base_x,base_x+CHAR_WID)]
                    #Takes only the green value, something black does not have but blue does
                    #Turns it into a boolean
                img_array.append(img_line)
            self.char_imgs[index] = img_array
        return self.char_imgs[index]

    def get_char_img(self, char:chr):
        """Return an image array from the IMG_CHRS_DICT index of the char."""
        index = IMG_CHRS_DICT[char]
        return self.char_imgs[index]

    def make_rect_orders(self):
        for c in IMG_CHRS_DICT.keys():
            char_img = self.get_char_img(c)
            self.make_rect_order(c,char_img)
    def make_rect_order(self,char,char_img):
        if char not in self.char_rect_orders.keys():
            char_rect_order = []
            for x in range(len(char_img[0])):
                left_x = (x*SCALE)
                right_x = left_x + SCALE
                for y in range(len(char_img)):
                    if not char_img[y][x]: #black
                        top_y = (y*SCALE)
                        bot_y = top_y + SCALE
                        char_rect_order.append(Rect(left_x, top_y, right_x, bot_y))
            self.char_rect_orders[char] = char_rect_order
        return self.char_rect_orders[char]
    def get_rect_order(self,char):
        """Returns an array of rectangles."""
        return self.char_rect_orders[char]

    def add_char_rects(self,char,base_x,base_y,char_img_orders):
        """Adds the base coordinates to the sprite rectangles."""
        rect_order = self.get_rect_order(char)
        [char_img_orders.append(Rect(r.left + base_x, r.top + base_y, r.right + base_x, r.bot + base_y)) for r in rect_order]
        return char_img_orders
    
    def create_line_char(self, c, x, y):
        index = IMG_CHRS_DICT[c]
        coords = LINE_CHR_INDICES[index]
        self.canvas.create_line(coords[0] + x, coords[1] + y, coords[2] + x, coords[3] + y, width=SCALE) #black by default
        self.rect_count += 1

    def create_rect(self, rect):
        self.canvas.create_rectangle(rect.left, rect.top, rect.right, rect.bot,fill="black",width=0)
        self.rect_count += 1

    def print_frame(self,char_list):
        """Take a string that's usually printed in-terminal, and
        instead print them on the canvas."""
        self.canvas.delete("all") # Remove previous frame, faster than white box fill
        x, y, c_count, self.rect_count = 0,0,1,0
        char_img_orders = []
        char_list = char_list[110:] #remove escape codes        
        for c in char_list:
            if c_count == 110:
                y += SCALE*CHAR_HEI
                x = 0
                c_count = 0
            if c != " ":
                if c in IMG_CHRS_DICT.keys():
                    if IMG_CHRS_DICT[c] in LINE_CHR_INDICES.keys():
                        self.create_line_char(c, x, y)
                    else:
                        char_img_orders = self.add_char_rects(c,x,y,char_img_orders)
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
                            self.create_rect(rect1)
                            rect_len = 1
                        i += 1
                if not rect1.fulfilled and rect_len > 1:
                    rect1.fulfilled = True
                    self.create_rect(rect1)

        for c in vertical_lines.values():
            if len(c) > 1:
                i = 0
                while i < len(c)-1:
                    rect1 = c[i]
                    rect2 = c[i+1]
                    if not rect1.fulfilled:
                        if rect1.bot == rect2.top:
                            rect1.bot = rect2.bot
                            rect2.fulfilled = True
                            c.pop(i+1)
                        else:
                            rect1.fulfilled = True
                            self.create_rect(rect1)
                            i += 1
                    else:
                        i += 1
                if not rect1.fulfilled:
                    rect1.fulfilled = True
                    self.create_rect(rect1)
            #else: #Probably unnecessary
            #    self.canvas.create_polygon((c[0].left + c[0].right) // 2, (c[0].top + c[0].bot) // 2, fill="black", width=SCALE)
        
        #print("\033[2J" + str(self.rect_count) + " rectangles rendered.")
        self.canvas.pack(fill = BOTH, expand = 1)
        self.canvas.update()