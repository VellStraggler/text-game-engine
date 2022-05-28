from time import time
import keyboard as keys
from tkinter import *
import tkinter.font as font
from os.path import exists
WID = 120
HEI = 29
BLANK = " "
QUIT = "esc"
START = '1.0'
DEF_FILE_NAME = "default"
MAX_LEN = (WID * HEI)
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
        self.update = False

        self.xcam = 0
        self.ycam = 0
        #These refer to the coords of the top-left corner
        # of the map camera.

    def init_map(self):
        """Initializes a map to default dimesions of
        WID * HEI. Called once on initiation"""
        map = []
        for y in range(HEI):
            map.append(list(BLANK * WID))
        return map

    def main_loop(self):
        """This runs a loop that checks for changes and updates the map."""
        while not keys.is_pressed(QUIT):
            self.frame_start = time()
            self.run_key_command()
            char = BLANK
            map_x,map_y = self.get_cursor_coords()
            length = len(self.inp_win.get(START,END))
            char = self.inp_win.get('insert-1c')
            if length > MAX_LEN + 1:
                self.inp_win.delete(INSERT)
                self.map[map_y][map_x] = char
            replacer = char
            for x in range(1,MAX_LEN-length+2):
                map_x,map_y = self.get_cursor_coords()
                if x%self.sprite_width.get() != 0:
                    if self.non_blanks:
                        replacer = BLANK
                    else:
                        replacer = self.map[map_y][map_x]
                else:
                    replacer = char
                self.map[map_y][map_x] = replacer
                self.inp_win.insert(self.inp_win.index('insert'), replacer)
            self.win.update()
            if self.update:
                self.update_win()
                self.update = False
    
    def print_fps(self):
        try:print(f"FPS: {(1/(time()-self.frame_start)):.2f}")
        except ZeroDivisionError: pass

    def get_cursor_coords(self):
        """Gets the cursor location on inp_win, converts it into map
        coordinates, accounting for camera position."""
        loc = int((str(self.inp_win.index(INSERT)).split('.'))[1])
        map_y = loc//WID + self.ycam
        map_x = loc - (WID*(loc//WID)) + self.xcam - 1
        return map_x,map_y

    def increase_width(self):
        """ This increases the width of the map by 1."""
        for y in self.map:
            y.append(BLANK)
        self.press_save()

    def increase_height(self):
        """ This increases the width of the map by 1."""
        line = list(BLANK * len(self.map[0]))
        self.map.append(line)
        self.press_save()

    def patch_map(self):
        """Makes arrays rectangular, that they are filled with arrays of
        uniform length."""
        assert len(self.map) > 0, "Error: Empty self.map put in."
        max_length = WID
        while len(self.map) < HEI:
            self.map.append(list(BLANK)) # Add extra rows to the minimum of HEI.
        for y in range(0,len(self.map)):
            if len(self.map[y]) > max_length:
                max_length = len(self.map[y]) # Get the maximum length
        # Makes all columns the max length.
        for row in self.map:
            assert type(row) == type(list()), "Only strings and lists can be in the array"
            for col in range(max_length - len(row)):
                row.append(BLANK)

    def press_save(self):
        """ This writes the map to the file.
        It also creates the file if it does not exist."""
        self.set_file_name()
        with open(self.file_name,"w") as file:
            for y in self.map:
                line = ""
                for x in y:
                    line = line + str(x)
                file.write(line + "\n")
        self.update_win()
    def create_new_file(self):
        self.press_save()

    def rotate_map(self):
        self.rotated = not self.rotated
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
        if time() - self.key_time > self.key_speed: 
            self.key_time = time()
            if keys.is_pressed("ctrl+s"):
                self.press_save()
            elif keys.is_pressed("ctrl+r"):
                self.rotate_map()
            elif keys.is_pressed("ctrl+z"):
                self.zoom(True)
            elif keys.is_pressed("ctrl+x"):
                self.zoom(False)
        if keys.is_pressed("ctrl+up arrow"): # Arrows control camera.
            if self.ycam > 0:
                self.ycam -= 1
                self.update_camera()
        elif keys.is_pressed("ctrl+down arrow"):
            self.ycam += 1
            if self.ycam + HEI > len(self.map):
                self.increase_height()
            self.update_camera()
        if keys.is_pressed("ctrl+right arrow"):
            self.xcam += 1
            if self.xcam + WID > len(self.map[0]):
                self.increase_width()
            self.update_camera()
        elif keys.is_pressed("ctrl+left arrow"):
            if self.xcam > 1:
                self.xcam -= 2
                self.update_camera()
            elif self.xcam > 0:
                self.xcam -= 1
                self.update_camera()

    def update_camera(self):
        """Updates the variables on the GUI that change when the
        camera moves. Sets update_win to be called at end of frame."""
        self.cam_msg.configure(text=str(self.xcam) + "," + str(self.ycam))
        self.wid_hei.configure(text="Map Dimensions: " + str(len(self.map[0])) + ", " + str(len(self.map)))
        self.update = True

    def update_win(self):
        save_loc = self.inp_win.index("insert")
        self.inp_win.delete(START,'end')
        full_text = ""
        for y in range(self.ycam,self.ycam+HEI):
            for x in range(self.xcam,self.xcam+WID):
                full_text = full_text + self.map[y][x]
        self.inp_win.insert(START,full_text)
        # Set cursor loc to previous spot.
        self.inp_win.mark_set("insert", save_loc)

    def clear_map(self):
        for y in range(self.ycam,self.ycam+HEI):
            for x in range(self.xcam,self.xcam+WID):
                self.map[y][x] = BLANK
        self.update_win()

    def set_file_name(self):
        """Gets you the file name from the get_file_name button, makes it
        usable."""
        file_entry = self.file_name_entry.get()
        if file_entry == "":
            self.file_name_entry.insert(0,DEF_FILE_NAME)
        if ".txt" not in file_entry:
            file_entry = file_entry + ".txt"
        if self.file_name == "" or self.file_name != file_entry:
            # If stored file_name is blank or not the same as file_entry,
            # store file_entry as new file_name
            self.file_name = file_entry

    def set_path(self):
        self.xcam = 0
        self.ycam = 0
        self.set_file_name()
        if exists(self.file_name):
            with open(self.file_name,'r') as file:
                self.map = list()
                newline = list(file.readline()[:-1])
                while newline:
                    self.map.append(newline)
                    newline = list(file.readline()[:-1])
            self.patch_map()
        else:
            self.create_new_file()
        self.update_camera()
        self.update_win()

    def create_window(self):
        window_geometry = str(int(WID * 8.5))+"x700+250+25"
        self.win.geometry(window_geometry)
        canvas = Canvas(self.win)
        canvas.master.title('TXTEngine MapEditor (Ver: 1.1)')

        # Buttons Above:
        self.file_name_entry = Entry(self.win)
        self.file_name_entry.grid(row = 1, column = 1,pady=10)

        file_name_button = Button(self.win, text = 'Set Map File')
        file_name_button.configure(command=self.set_path)
        file_name_button.grid(row = 1, column = 2)

        save = Button(self.win, text='Save')
        save.configure(command=self.press_save)
        save.grid(row=1,column=8,columnspan=1)

        clear_e = Button(self.win, text='Clear Map',command=self.clear_map)
        clear_e.grid(row=1, column=9)

        # Input Window:
        self.inp_win = Text(self.win, width=WID, height=HEI)
        self.inp_win.insert(START,(BLANK * MAX_LEN))
        self.inp_win.grid(row = 2, column = 1,columnspan=9,padx=25)
        self.inp_win.mark_set("insert",START)

        # Buttons Below:
        self.cam_msg = Message(self.win,text=str(self.xcam)  + ", " + str(self.ycam))
        self.cam_msg.grid(row=3,column=1)

        self.wid_hei = Message(self.win,text="Map Dimensions: " + str(WID) + ", " + str(HEI))
        self.wid_hei.grid(row=4,column=1)

        zoom_msg = Message(self.win,text="Zoom out:")
        zoom_msg.grid(row=3,column=2,pady=10)

        v = IntVar()
        zoom = Scale(self.win, variable=v, from_=1, to=10, orient=HORIZONTAL)  
        zoom.grid(row=3,column=3)

        rotate = Button(self.win,text="Rotate",command=self.rotate_map)
        rotate.grid(row=3,column=4)

        sprite_msg = Message(self.win,text="Sprite Width:",anchor="w")
        sprite_msg.grid(row=3,column=5)

        s = IntVar()
        self.sprite_width = Scale(self.win, variable=s, from_=1, to=15, orient=HORIZONTAL)  
        self.sprite_width.grid(row=3,column=6)

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