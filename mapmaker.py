from time import time
import keyboard as keys
from tkinter import *
import tkinter.font as font
from os.path import exists
WID = 110
HEI = 30
BLANK = ","
QUIT = "esc"
MAX_LEN = (WID * HEI) - 0
class MapMaker():
    """This reads a map file and allows changes."""
    def __init__(self):
        self.map = self.init_map()
        self.file_name= ""
        self.win = Tk()
        self.key_time = 0
        self.key_speed = 0.3
        self.non_blanks = False
        self.rotated = False
        self.xcam = 0
        self.ycam = 0

    def init_map(self):
        """Initializes a map to default dimesions of
        WID * HEI."""
        map = []
        for y in range(HEI):
            map.append(list(BLANK * WID))
        return map

    def main_loop(self):
        """This runs a loop that checks for changes and updates the map."""
        while not keys.is_pressed(QUIT):
            self.run_key_command()
            char = BLANK
            assert type(self.map) == type(list()), "What the heck3."
            map_x,map_y = self.get_cursor_loc()
            length = len(self.inp_win.get('1.0',END))
            char = self.inp_win.get('insert-1c')
            if length > MAX_LEN:
                try: 
                    self.inp_win.delete('insert')
                    self.map[map_y][map_x] = char
                except: pass
            replacer = char
            for x in range(1,MAX_LEN-length+1):
                map_x,map_y = self.get_cursor_loc()
                if x%self.sprite_width.get() != 0:
                    replacer = BLANK
                else:
                    replacer = char
                self.inp_win.insert(self.inp_win.index('insert'), replacer)
                self.map[map_y][map_x] = replacer
            self.win.update()
        self.press_save()

    def get_cursor_loc(self):
        loc = int((str(self.inp_win.index(INSERT)).split('.'))[1])
        map_y = loc//WID + self.xcam
        map_x = loc - (WID*(map_y)) + self.ycam
        return map_x,map_y
    def increase_width(self):
        """ This increases the width of the map by 1."""
        for y in range(len(self.map)):
            self.map[y].append(BLANK)

    def increase_height(self):
        """ This increases the width of the map by 1."""
        line = list(BLANK * len(self.map[0]))
        self.map.append(line)

    def press_save(self):
        """ This writes the map to the file.
        It also creates the file if it does not exist."""
        assert type(self.map) == type(list()), "What the heck2."
        if self.file_name == "":
            self.file_name = self.map_file.get()
        with open(self.file_name,"w") as file:
            for y in self.map:
                line = ""
                for x in y:
                    line += x
                file.write(line + "\n")

    def create_new_file(self):
        self.press_save()

    def rotate_map(self):
        if self.rotated:
            print("The map is rotated.")
        else:
            print("The map is not rotated.")

    def zoom(self,_in):
        if _in:
            print("Zooming in")
        else:
            print("Zooming out")

    def run_key_command(self):
        """This checks for commands that are pressed."""
        assert type(self.map) == type(list()), "What the heck1."
        if time() - self.key_time > self.key_speed: 
            self.key_time = time()
            if keys.is_pressed("alt"):
                self.rotate_map()
            elif keys.is_pressed("ctrl+z"):
                self.zoom(True)
            elif keys.is_pressed("ctrl+x"):
                self.zoom(False)
            elif keys.is_pressed("up arrow"): # Arrows control camera.
                if self.xcam > 0:
                    self.xcam -= 1
            elif keys.is_pressed("ctrl+down arrow"):
                self.xcam += 1
                if self.xcam + HEI > len(self.map):
                    self.map = self.increase_height()
            elif keys.is_pressed("ctrl+right arrow"):
                self.ycam += 1
                if self.ycam + WID > len(self.map[0]):
                    self.map = self.increase_width()
            elif keys.is_pressed("ctrl+left arrow"):
                if self.ycam > 0:
                    self.ycam -= 1

    def update_win(self):
        self.inp_win.delete('1.0','end')
        full_text = ""
        for y in range(self.ycam,self.ycam+HEI):
            for x in range(self.xcam,self.xcam+WID):
                full_text += self.map[y][x]
        self.inp_win.insert('1.0',full_text)

    def clear_map(self):
        for y in range(self.ycam,self.ycam+HEI):
            for x in range(self.xcam,self.xcam+WID):
                self.map[y][x] = BLANK
        self.update_win()

    def set_path(self,file_name):
        if ".txt" not in file_name:
            file_name = file_name + ".txt"
        self.file_name = file_name
        if exists(file_name):
            with open(file_name,'r') as file:
                self.map = list()
                newline = list(file.readline()[:-1])
                while newline:
                    self.map.append(newline)
                    newline = list(file.readline()[:-1])
        else:
            self.create_new_file()
        self.update_win()


    def create_window(self):
        self.win.geometry("940x700+250+25")
        canvas = Canvas(self.win)
        canvas.master.title('TXTEngine Map Editor (Ver: 1.0)')

        # Buttons Above:
        self.map_file = Entry(self.win)
        self.map_file.grid(row = 1, column = 1,pady=10)

        open_map_file = Button(self.win, text = 'Set Map File')
        open_map_file.configure(command=lambda: self.set_path(self.map_file.get()))
        open_map_file.grid(row = 1, column = 2)

        save = Button(self.win, text='Save')
        save.configure(command=self.press_save)
        save.grid(row=1,column=8,columnspan=1)

        clear_e = Button(self.win, text='Clear Map',command=self.clear_map)
        clear_e.grid(row=1, column=9)

        #f = font.Font(family="monospace",size=11)

        # Input Window:
        self.inp_win = Text(self.win, width=WID, height=HEI)
        #self.inp_win['font'] = f
        self.inp_win.insert('1.0',(BLANK * MAX_LEN))
        self.inp_win.grid(row = 2, column = 1,columnspan=9,padx=25)

        # Buttons Below:
        zoom_msg = Message(self.win,text="Zoom out:")
        zoom_msg.grid(row=3,column=1,pady=10)

        v = IntVar()
        zoom = Scale(self.win, variable=v, from_=1, to=9, orient=HORIZONTAL)  
        zoom.grid(row=3,column=2)

        rotate = Button(self.win,text="Rotate",command=self.rotate_map)
        rotate.grid(row=3,column=3)

        sprite_msg = Message(self.win,text="Sprite Width:",anchor="w")
        sprite_msg.grid(row=3,column=4)

        s = IntVar()
        self.sprite_width = Scale(self.win, variable=s, from_=1, to=9, orient=HORIZONTAL)  
        self.sprite_width.grid(row=3,column=5)

        blanks_msg = Message(self.win,text="Replace chars:")
        blanks_msg.grid(row=3,column=8)

        non_blanks = Button(self.win,text="No",command=lambda:self.yes_to_no(non_blanks))
        non_blanks.grid(row=3,column=9)

    def yes_to_no(self,non_blanks):
        if self.non_blanks:
            self.non_blanks = False
            non_blanks.configure(text="No")
        else:
            self.non_blanks = True
            non_blanks.configure(text="Yes")

m = MapMaker()
m.create_window()
m.main_loop()
    # Button to rotate map
    # Zooming in/out
    # Terminal-style text