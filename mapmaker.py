from time import time
import textengine as tx
import keyboard as keys
from tkinter import *
WID = 110
HEI = 30
BLANK = " "
class MapMaker():
    def __init__(self):
        self.g = tx.Game()
        self.inp_map = []
        self.inp_map = self.g.map.empty_map(self.inp_map)
        self.file_name= ""
        self.win = Tk()
        self.key_time = 0
        self.key_speed = 0.35
        self.non_blanks = False

    def create_text_map(self):
        for item in self.g.map.sparse_map:
            self.inp_map[item[1]][item[0]] = item[2]

    def press_save(self):
        self.create_text_map()
        with open(self.file_name,"w") as file:
            for y in self.inp_map:
                line = ""
                for x in y:
                    line = line + x
                file.write(line + "\n")

    def run_code(self,file_name):
        pass

    def rotate_map(self,g):
        pass

    def zoom(self,_in):
        if _in:
            pass
        else:
            pass

    def run_key_command(self):
        if time() - self.key_time > self.key_speed: 
            self.key_time = time()
            if keys.is_pressed("alt"):
                self.rotate_map()
            elif keys.is_pressed("ctrl+up arrow"):
                self.zoom(True)
            elif keys.is_pressed("ctrl+down arrow"):
                self.zoom(False)
            elif keys.is_pressed("up arrow"): # Arrows control camera.
                self.g.map.window = [self.g.map.window[0]-1,self.g.map.window[1]]
            elif keys.is_pressed("down arrow"):
                self.g.map.window = [self.g.map.window[0]+1,self.g.map.window[1]]
            elif keys.is_pressed("right arrow"):
                self.g.map.window = [self.g.map.window[0],self.g.map.window[1]+1]
            elif keys.is_pressed("left arrow"):
                self.g.map.window = [self.g.map.window[0],self.g.map.window[1]-1]

    def set_path(self,file_name):
        if ".txt" not in file_name:
            file_name = file_name + ".txt"
        self.file_name = file_name
        try:
            self.g.map.set_path(file_name)
        except:
            self.press_save()
            # Creates a new file.


    def create_window(self):
        self.win.geometry("940x700+250+50")
        canvas = Canvas(self.win)
        canvas.master.title('TXTEngine Map Editor (Ver: 1.0)')

        # Buttons Above:
        map_file = Entry(self.win)
        map_file.grid(row = 1, column = 1,pady=10)

        open_map_file = Button(self.win, text = 'Set Map File')
        open_map_file.configure(command=lambda: self.set_path(map_file.get()))
        open_map_file.grid(row = 1, column = 2)

        save = Button(self.win, text='Save')
        save.configure(command=self.press_save)
        save.grid(row=1,column=8,columnspan=1)

        clear_e = Button(self.win, text='Clear Map',command=self.g.map.empty_map)
        clear_e.grid(row=1, column=9)

        # Input Window:
        self.inp_win = Text(self.win, width=WID, height=HEI)
        self.inp_win.insert('1.0',(BLANK *WID *HEI))
        self.inp_win.grid(row = 2, column = 1,columnspan=9,padx=25)

        # Buttons Below:
        zoom_msg = Message(self.win,text="Zoom-out: What the heck.")
        zoom_msg.grid(row=3,column=1,pady=10)

        v = IntVar()
        zoom = Scale(self.win, variable=v, from_=1, to=9, orient=HORIZONTAL)  
        zoom.grid(row=4,column=1)

        rotate = Button(self.win,text="Rotate",command=self.rotate_map)
        rotate.grid(row=3,column=2)

        blanks_msg = Message(self.win,text="Replace non-blanks?")
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

    def main_loop(self):
        while not keys.is_pressed("esc"):
            self.run_key_command()
            # Get cursor location
            loc = int((str(self.inp_win.index(INSERT)).split('.'))[1])
            # Update sparse_map at location, translated to x and y
            map_y = loc//WID -1
            map_x = loc - (WID*(map_y+1)) 
            if len(self.inp_win.get('1.0',END)) > WID * HEI: #A CHARACTER HAS BEEN ADDED.
                self.inp_map[map_y][map_x] = self.inp_win.get('insert-1c')
                print("Y:",map_y,"X:",map_x,"Loc:",loc,"char:",self.inp_win.get('insert-1c'))
                self.inp_win.delete('insert')
            elif len(self.inp_win.get('1.0',END)) < WID * HEI:
                addspace = '1.'+str(loc-(loc % WID)+WID-1)
                self.inp_win.insert( addspace ,' ')
            self.win.update()
        self.press_save(self.file_name)
        
m = MapMaker()
m.create_window()
m.main_loop()
    # Button to rotate map
    # Multi-character Selection
    # Immediate map updating
    # Zooming in/out
    # Map saves
    # Terminal-style text