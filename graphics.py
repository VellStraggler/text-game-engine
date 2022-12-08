from textengine import WINDOW_HEI as TXT_WIN_HEI
from textengine import WINDOW_WID as TXT_WIN_WID
from tkinter import Tk, Canvas, Frame, BOTH, NW
import imageio.v2 as iio
SCALE = 5
CHAR_HEI = 9
CHAR_WID = 3
WINDOW_HEI = TXT_WIN_HEI * SCALE * CHAR_HEI
WINDOW_WID = TXT_WIN_WID * SCALE * CHAR_WID
IMG_CHRS = "\/_-⎺$,$$$$`[](){}│|↗↙↘↖ABCDEFGHIJKLMNOPQRSTUVWXYZ13456789$$\":=ox><^v$$▀▄i⟘┤├.';?!#"
def string_to_dict(string):
    newdict = dict()
    for i in range(len(string)):
        newdict[string[i]] = i
    return newdict
IMG_CHRS_DICT = string_to_dict(IMG_CHRS)
print(IMG_CHRS_DICT)

class Graphics(Frame):
    def __init__(self):
        super().__init__()
        self.pixel_chars_img = iio.imread("./pixel_char_sheet.png")
        self.initUI()
    def initUI(self):
        self.master.title("Texillica ver. 2")
        self.pack(fill = BOTH, expand = 1)
        canvas = Canvas(self)
        canvas.pack(fill = BOTH, expand = 1)
        for offset in range(25):
            for y in range(len(self.pixel_chars_img)):
                for x in range(len(self.pixel_chars_img[y])):
                    if sum(self.pixel_chars_img[y][x]) == 0:
                        canvas.create_rectangle(x*SCALE + offset,y*SCALE,(x+1)*SCALE + offset,(y+1)*SCALE,width=0,fill="black")
                    else:
                        canvas.create_rectangle(x*SCALE + offset,y*SCALE,(x+1)*SCALE + offset,(y+1)*SCALE,width=0,fill="yellow")
            # more actions
            canvas.update()
    def interpret_char(char:chr):
        """Take a character and return its sister image from the
        pixel_char_sheet."""
        

def main():
    root = Tk()
    graphics = Graphics()
    root.geometry(str(WINDOW_WID) + "x" + str(WINDOW_HEI) + "+250+0")
    root.mainloop()

if __name__ == '__main__':
    main()