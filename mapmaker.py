from time import time, sleep
import keyboard as keys
from tkinter import *
import tkinter.font as font
import threading
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
        self.rect_select = False
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
    
    def get_length(self):
        return len(self.inp_win.get(START,END))

    def main_loop(self):
        """This runs a loop that checks for changes and updates the map."""
        while not keys.is_pressed(QUIT):
            self.run_key_command()
            char = self.inp_win.get('insert-1c')
            map_x,map_y = self.get_cursor_coords()
            length = self.get_length()
            if length > MAX_LEN + 1:
                self.inp_win.delete(INSERT)
                # edge case: past last index
                if (map_y >= len(self.map)):
                    self.increase_height()
                self.map[map_y][map_x] = char
            replacer = char
            for x in range(1,MAX_LEN-length+2):
                map_x,map_y = self.get_cursor_coords()
                if x%self.sprite_width.get() != 0:
                    if self.rect_select:
                        replacer = BLANK
                    else:
                        replacer = self.map[map_y][map_x]
                else:
                    replacer = char
                self.map[map_y][map_x] = replacer
                self.inp_win.insert(self.inp_win.index(INSERT), replacer)
            self.win.update()
            if self.update:
                self.update_win()
                self.update = False

    def get_cursor_coords(self, offset = 0):
        """Gets the cursor location on inp_win, converts it into map
        coordinates, accounting for camera position."""
        loc = self.get_cursor_index() + offset
        return self.__get_cursor_coords_by_index(loc)
    
    def __get_cursor_coords_by_index(self, loc):
        map_y = loc//WID + self.ycam
        map_x = loc - (WID*(loc//WID)) + self.xcam - 1
        return map_x,map_y
    
    def get_cursor_index(self):
        return int((str(self.inp_win.index(INSERT)).split('.'))[1])

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

        if self.rotated:
            self.rotate_map()


        self.set_file_name()
        with open(self.file_name,"w") as file:
            for y in self.map:
                line = []
                for x in y:
                    line.append(x)
                line = "".join(line)
                file.write(line + "\n")
        self.update_win()
    def create_new_file(self):
        self.press_save()

    def rotate_map(self):
        self.rotated = not self.rotated
        max_length = 0
        for y in self.map:
            if len(y) > max_length:
                max_length = len(y)
        
        while len(self.map) < max_length:
            self.increase_height()
        
        while len(self.map) > max_length:
            self.increase_width()

        map_copy = [row[:] for row in self.map]

        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                new_y = x
                new_x = y
                map_copy[new_y][new_x] = self.map[y][x]
        
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                self.map[y][x] = map_copy[y][x]

        if self.rotated:
            print("The map is rotated.")
        else:
            print("The map is not rotated.")

        self.update_win()

        print(self.map[1][0])

    def run_key_command(self):
        """This checks for commands that are pressed."""
        if keys.is_pressed("backspace"):
            x,y = self.get_cursor_coords(1)
            self.map[y][x] = " "
            self.update_win()


        if time() - self.key_time > self.key_speed: 
            self.key_time = time()
            if keys.is_pressed("ctrl+s"):
                self.press_save()
            elif keys.is_pressed("ctrl+r"):
                self.rotate_map()
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
        self.cam_msg.configure(text="Camera: " + str(self.xcam) + "," + str(self.ycam))
        self.wid_hei.configure(text="Map Dimensions: " + str(len(self.map[0])) + ", " + str(len(self.map)))
        self.update = True

    def update_win(self):
        save_loc = self.inp_win.index("insert")
        # clear screen
        self.inp_win.delete(START,'end')
        full_text = []
        y_end = self.ycam + HEI
        x_end = self.xcam + WID
        for y in range(self.ycam, y_end):
            for x in range(self.xcam, x_end):
                full_text.append(self.map[y][x])
        full_text = "".join(full_text)
        # write screen
        self.inp_win.insert(START,full_text)
        # Set cursor loc to previous spot.
        self.inp_win.mark_set("insert", save_loc)

    def clear_map(self):
        # Only clears the visible map
        for y in range(self.ycam,self.ycam+HEI):
            for x in range(self.xcam,self.xcam+WID):
                self.map[y][x] = BLANK
        self.update_win()

    def reset_map(self):
        self.map = self.init_map()
        self.update_win()
        self.update_camera()

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
        window_geometry = str(int(WID * 8.5))+"x590+250+25"
        self.win.geometry(window_geometry)
        self.win.resizable(False, False) 
        canvas = Canvas(self.win)
        canvas.master.title('TXTEngine Map Editor (Ver: 1.2)')

        # Buttons Above:
        self.file_name_entry = Entry(self.win)
        self.file_name_entry.grid(row = 1, column = 1,pady=10)

        file_name_button = Button(self.win, text = 'Set Map File')
        file_name_button.configure(command=self.set_path)
        file_name_button.grid(row = 1, column = 2)

        save = Button(self.win, text='Save')
        save.configure(command=self.press_save)
        save.grid(row=1,column=7)

        clear_e = Button(self.win, text='Clear Map',command=self.clear_map)
        clear_e.grid(row=1, column=8)

        reset_map = Button(self.win, text='Reset Map',command=self.reset_map)
        reset_map.grid(row=1, column=9)

        # Input Window:
        self.inp_win = Text(self.win, width=WID, height=HEI)
        self.inp_win.insert(START,(BLANK * MAX_LEN))
        self.inp_win.grid(row = 2, column = 1,columnspan=9,padx=25, pady=10)
        self.inp_win.mark_set("insert",START)

        # Buttons Below:
        self.cam_msg = Message(self.win,text="Camera: " + str(self.xcam)  + ", " + str(self.ycam))
        self.cam_msg.grid(row=3,column=1)

        self.wid_hei = Label(self.win,text="Map Dimensions: " + str(WID) + ", " + str(HEI))
        self.wid_hei.grid(row=3,column=2)

        rotate_button = Button(self.win,text="Rotate",command=self.rotate_map)
        rotate_button.grid(row=3,column=4)

        sprite_msg = Message(self.win,text="Sprite Width:",anchor="w")
        sprite_msg.grid(row=3, column=5, sticky="e")
        s = IntVar()
        self.sprite_width = Scale(self.win, variable=s, from_=1, to=15, orient=HORIZONTAL)  
        self.sprite_width.grid(row=3,column=6, sticky="w")

        rects_msg = Label(self.win,text="Rectangular Selection:")
        rects_msg.grid(row=3,column=7, sticky="e")
        rect_select = Button(self.win,text=str(self.rect_select),command=lambda:self.set_rect_select(rect_select))
        rect_select.grid(row=3,column=8, sticky="w")

        # for notices, added information
        self.usr_msg = Label(self.win, text="")
        self.usr_msg.grid(row=3,column=9)

    def set_rect_select(self,rect_select):
        self.rect_select = not self.rect_select
        rect_select.configure(text=str(self.rect_select))
        self.set_usr_msg("Not implemented")

    def set_usr_msg(self, msg):
        self.usr_msg.configure(text=msg)
        delay = 800 + int(50 * len(msg))  # 1s + 0.1s per char
        self.win.after(delay, lambda: self.__age_usr_msg(msg))

    def __age_usr_msg(self, msg):
        if len(msg) > 0:
            msg = msg[:-1]
            self.usr_msg.configure(text=msg)
            self.win.after(100, lambda: self.__age_usr_msg(msg))


m = MapMaker()
m.create_window()
m.main_loop()