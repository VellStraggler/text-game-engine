from tkinter import *
import tkinter
# import textengine as tx

class SpriteMaker:
    def __init__(self, root:Tk):
        self.root = root
        self.root.title("TXTEngine Sprite Editor (Ver: 0.1)")
        for r in range(8):
            root.grid_rowconfigure(r, weight=1, minsize=10)
        for c in range(16):
            root.grid_columnconfigure(c, weight=1, minsize=10)

        # Storing the Sprite
        self.sprite_width = 16
        self.sprite_height = 8
        self.sprite_array = []
        self.color_array = []
        for y in range(self.sprite_height):
            sprite_row = []
            color_row = []
            for x in range(self.sprite_width):
                sprite_row.append(" ")
                color_row.append("black")
            self.sprite_array.append(sprite_row)
            self.color_array.append(color_row)

        # Create a Canvas
        self.pixel_width = 30
        self.pixel_height = self.pixel_width * 2
        self.canvas_width = self.sprite_width * self.pixel_width
        self.canvas_height = self.sprite_height * self.pixel_height
        self.canvas = Canvas(root, width=self.canvas_width, height=self.canvas_height,bg="white")
        self.canvas.grid(row=0, column=8, rowspan=8, columnspan=8)

        self.canvas_width_scale = Scale(self.root, from_=1, to=30, 
                                        variable=IntVar(value=self.pixel_width), 
                                        command=self.resize_canvas,
                                        orient=HORIZONTAL)  
        self.canvas_width_scale.grid(row=0,column=0)

        # Variables to store last mouse position
        self.last_x = 0
        self.last_y = 0

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.activate)       # Left click
        self.canvas.bind("<B1-Motion>", self.draw)         # Drag while left-click held
        self.canvas.bind("<ButtonRelease-1>", self.reset)  # Release mouse button

        self.last_key = " "
        self.root.bind("<Key>", self.key_pressed)
        self.current_color = "black"
        self.text_color = "white"

        self.is_black = BooleanVar(value=False)
        self.color_lever = Checkbutton(root, text="Black Text", variable= self.is_black, command=self.set_lever)
        self.color_lever.grid(row=1, column=0)

        self.is_type_mode = BooleanVar(value=False)
        self.type_mode = Checkbutton(root, text="Type Mode", variable= self.is_type_mode)
        self.type_mode.grid(row=3, column=0)

        self.copy_button = Button(root, text="Copy Sprite to Clipboard", command=self.copy)
        self.copy_button.grid(row=2,column=0)

        self.palette_buttons = []
        self.colors = ["black","white","yellow","red"]
        for c in range(len(self.colors)):
            button = Button(root, background=self.colors[c], 
                            command= lambda color = self.colors[c]: self.set_color(color))
            button.grid(row=4,column=c+1)
            self.palette_buttons.append(button)
        for c in range(len(self.colors)):
            button = Button(root, background=self.colors[c], 
                            command= lambda color = self.colors[c]: self.set_text_color(color))
            button.grid(row=5,column=c+1)
            self.palette_buttons.append(button)
        
        self.resize_canvas(self.pixel_width)

    def set_color(self, value):
        self.current_color = value

    def set_text_color(self,value):
        self.text_color = value

    def copy(self):
        text = "\n".join("".join(row) for row in self.sprite_array)
        self.root.clipboard_clear()
        root.clipboard_append(text)
        root.update()

    def set_lever(self):
        if not self.is_black.get():
            self.current_color = "black"
            self.text_color = "white"
        else:
            self.current_color = "white"
            self.text_color = "black"

    def key_pressed(self, event):
        """Stores a key pressed and draws it on the last
        available coordinate on the sprite canvas"""
        if event.char == "":
            return
        self.last_key = event.char

        self.key_draw(self.last_x, self.last_y)
        # move cursor along if in type mode
        if self.is_type_mode.get():
            self.last_x += self.pixel_width
            if self.last_x > self.pixel_width * self.sprite_width:
                self.last_x = 1
                self.last_y += self.pixel_height
                if self.last_y > self.pixel_height * self.sprite_height:
                    self.last_y = 1

    def resize_canvas(self, value):
        self.pixel_width = int(value)
        self.pixel_height = self.pixel_width * 2
        self.canvas_width = self.sprite_width * self.pixel_width
        self.canvas_height = self.sprite_height * self.pixel_height
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)

        self.draw_canvas_from_memory()
    
    def draw_canvas_from_memory(self):
        temp_key = self.last_key
        temp_color = self.current_color
        for y in range(self.sprite_height):
            for x in range(self.sprite_width):
                self.last_key = self.sprite_array[y][x]
                self.current_color = self.color_array[y][x]
                self.key_draw(x*self.pixel_width,y*self.pixel_height)
        self.last_key = temp_key
        self.current_color = temp_color

    def activate(self, event):
        # Save the initial position
        self.last_x = event.x
        self.last_y = event.y
        self.draw(event)

    def get_rounded_coords(self,x,y):
        x = int(x/self.pixel_width) * self.pixel_width
        y = int(y/self.pixel_height) * self.pixel_height
        return x,y
    
    def get_text_coords(self,x,y):
        x = int(x/self.pixel_width)
        y = int(y/self.pixel_height)
        return x,y

    def draw(self,event):
        if event.x is None:
            return
        self.key_draw(event.x, event.y)
    def key_draw(self, ex,ey):
        # Draw a rectangle of a certain dimension at the given rounded coordinate
        if ex is None:
            return
        x,y = self.get_rounded_coords(ex, ey)
        textx,texty = self.get_text_coords(x, y)
        self.sprite_array[texty][textx] = self.last_key
        self.color_array[texty][textx] = self.current_color
        self.canvas.create_rectangle(x, y, x+self.pixel_width, y+self.pixel_height, fill=self.current_color,outline=self.current_color)
        if self.current_color== self.text_color:
            if self.current_color == "black":
                self.text_color = "white"
            else:
                self.text_color = "black"
        self.canvas.create_text(x+(self.pixel_width/2),
                                y+(self.pixel_height/2),text=self.last_key,
                                font=("Courier New", int(self.pixel_height*.75), "bold"),
                                fill=self.text_color, anchor=CENTER)
        
        self.last_x = ex
        self.last_y = ey

    def reset(self, event):
        # Reset the last position
        # self.last_x = None
        # self.last_y = None
        pass

    def other(self, root):
        self.file_name_entry = Entry(self.window)
        self.file_name_entry.grid(row = 1, column = 1,pady=10)

        file_name_button = Button(self.window, text = 'Set Sprite File')
        file_name_button.configure(command=self.set_path)
        file_name_button.grid(row = 1, column = 2)

        save = Button(self.window, text='Save')
        save.configure(command=self.press_save)
        save.grid(row=1,column=7)

        clear_e = Button(self.window, text='Clear Sprite',command=self.clear_sprite)
        clear_e.grid(row=1, column=8)

        reset_map = Button(self.window, text='Clear Color',command=self.clear_color)
        reset_map.grid(row=1, column=9)

        # Buttons Below:

        self.wid_hei = Label(self.window,text="Sprite Dimensions: " + str(WID) + ", " + str(HEI))
        self.wid_hei.grid(row=3,column=2)

        # for notices, added information
        self.usr_msg = Label(self.window, text="")
        self.usr_msg.grid(row=3,column=9)


root = Tk()
app = SpriteMaker(root)
root.mainloop()