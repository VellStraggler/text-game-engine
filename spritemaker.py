from tkinter import *
import tkinter
# import textengine as tx
import PIL.Image as PImage

class SpriteMaker:
    def __init__(self, root:Tk):
        # Root
        self.root = root
        self.root.title("TXTEngine Sprite Editor (Ver: 0.1)")
        for r in range(16):
            root.grid_rowconfigure(r, weight=1, minsize=10)
        for c in range(32):
            root.grid_columnconfigure(c, weight=1, minsize=10)

        self.height_multiplier = DoubleVar(value=1.41)
        # Sprite Arrays
        self.sprite_width = 16
        self.sprite_height = 8
        self.sprite_array = []
        self.color_array = []
        self.text_color_array = []
        for y in range(self.sprite_height):
            sprite_row = []
            color_row = []
            text_color_row = []
            for x in range(self.sprite_width):
                sprite_row.append(" ")
                color_row.append("black")
                text_color_row.append("white")
            self.sprite_array.append(sprite_row)
            self.color_array.append(color_row)
            self.text_color_array.append(text_color_row)

        # Canvas
        self.pixel_width = 30
        self.pixel_height = self.pixel_width * self.height_multiplier.get()
        self.canvas_width = self.sprite_width * self.pixel_width
        self.canvas_height = self.sprite_height * self.pixel_height
        self.canvas = Canvas(root, width=self.canvas_width, height=self.canvas_height,bg="white")
        self.canvas.grid(row=0, column=16, rowspan=80, columnspan=80)

        self.canvas_width_scale = Scale(self.root, from_=1, to=30, 
                                        variable=IntVar(value=self.pixel_width), 
                                        command=self.resize_canvas,
                                        orient=HORIZONTAL)  
        self.canvas_width_scale.grid(row=0,column=0)

        # Mouse Position
        self.last_x = 0
        self.last_y = 0

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.activate)       # Left click
        self.canvas.bind("<B1-Motion>", self.draw)         # Drag while left-click held
        self.canvas.bind("<ButtonRelease-1>", self.reset)  # Release mouse button

        self.last_key = "#"
        self.root.bind("<Key>", self.key_pressed)
        self.default_color = "black"
        self.default_text_color = "white"
        self.current_color = self.default_color
        self.text_color = self.default_text_color

        # Type Mode
        self.is_type_mode = BooleanVar(value=False)
        self.type_mode = Checkbutton(root, text="Type Mode", variable= self.is_type_mode)
        self.type_mode.grid(row=3, column=0)

        # Replace Mode
        self.is_replace_mode = BooleanVar(value=False)
        self.replace_mode = Checkbutton(root, text="Replace Mode", variable=self.is_replace_mode)
        self.replace_mode.grid(row=4,column=0)

        # Copy Button
        self.copy_button = Button(root, text="Copy Plain Text to Clipboard", command=self.copy)
        self.copy_button.grid(row=2,column=0)

        # Special Text
        text_chars = "◤◥╱╲⎺│¯◉◕◔◓◑◐◨◧▼▲▶◀▄"
        self.special_text_buttons = []
        tc_columns = 8
        for i in range(len(text_chars)):
            button = Button(text=text_chars[i], command=lambda c = text_chars[i]: self.set_char(c))
            button.grid(row=i//tc_columns, column =(i%tc_columns)+1)
            self.special_text_buttons.append(button)

        # Preview Character
        self.preview_width = 60
        self.char_preview = Canvas(root,width=self.preview_width, height=self.preview_width*self.height_multiplier.get())
        self.char_preview.grid(row=6,column=1,columnspan=7)

        # Hidable Color Choices
        image_file = PImage.open("scripts/text-game-engine/chars_and_colors/colors_by_number.png")
        image = image_file.load()
        # FIXME: skip legacy colors for now
        start_num = 16
        color_width = 200
        color_height = 20
        start_coord = [70,70] # midnight blue
        color_dict = dict()
        num = start_num
        for x in range(6):
            for y in range(40):
                color = image[start_coord[0] + (color_width*x), start_coord[1] +(color_height*y)]
                color_dict[num] = (color[0], color[1], color[2])
                num+=1
        
        # print(color_dict)
        # self.all_colors = Canvas(root, width=200, height=200)
        # self.all_colors.grid(row=0,column=0)

        # box_size = 10   # size of each square
        # cols = 24       # squares per row

        # for i, (num, rgb) in enumerate(color_dict.items()):
        #     tk_color = "#%02x%02x%02x" % rgb   # convert RGB → "#RRGGBB"

        #     x = (i % cols) * box_size
        #     y = (i // cols) * box_size

        #     self.all_colors.create_rectangle(
        #         x, y, x + box_size, y + box_size,
        #         fill=tk_color, outline=""
        #     )

        # Color Palettes
        self.palette_buttons = []
        self.colors =    ["black","white","yellow","red"]
        self.text_colors=["white","black","purple","green"]
        for i,label in enumerate(["background","text color"]):
            palette_label = Label(root, text=label)
            palette_label.grid(row=4+i, column=1)
        for c in range(len(self.colors)):
            button = Button(root, background=self.colors[c], 
                            command= lambda color = self.colors[c]: self.set_color(color))
            button.grid(row=4,column=c+2)
            self.palette_buttons.append(button)
        p_button = Button(root, text="+", command=self.add_color)
        p_button.grid(row=4, column=len(self.colors)+2)
        for c in range(len(self.text_colors)):
            button = Button(root, background=self.text_colors[c], 
                            command= lambda color = self.text_colors[c]: self.set_text_color(color))
            button.grid(row=5,column=c+2)
            self.palette_buttons.append(button)
        p_button = Button(root, text="+", command=self.add_text_color)
        p_button.grid(row=5, column=len(self.text_colors)+2)

        # Erase Button
        clear_b = Button(root, text='Erase All',command=self.clear_sprite)
        clear_b.grid(row=6, column=0)

        # Char Ratio
        # For Debugging only
        # char_ratio = Scale(root, variable=self.height_multiplier, 
        #                    from_=1, to=2, resolution=.01, command=self.re_ratio)
        # char_ratio.grid(row=7,column=0)
        
        self.draw_preview()
        self.resize_canvas(self.pixel_width)

    def re_ratio(self, val):
        value = self.pixel_width
        self.resize_canvas(value)

    def set_char(self, c):
        self.last_key = c
        self.draw_preview()

    def clear_sprite(self):
        for y in range(self.sprite_height):
            for x in range(self.sprite_width):
                self.color_array[y][x] = self.default_color
                self.sprite_array[y][x] = " "
                self.text_color_array[y][x] = self.default_text_color
        self.draw_canvas_from_memory()

    def add_color(self):
        pass

    def add_text_color(self):
        pass

    def set_color(self, value):
        self.current_color = value
        self.draw_preview()

    def set_text_color(self,value):
        self.text_color = value
        self.draw_preview()

    def copy(self):
        text = "\n".join("".join(row) for row in self.sprite_array)
        self.root.clipboard_clear()
        root.clipboard_append(text)
        root.update()

    def key_pressed(self, event):
        """Stores a key pressed and draws it on the last
        available coordinate on the sprite canvas"""
        if event.char == "":
            return
        self.last_key = event.char

        self.draw_preview()
        # move cursor along if in type mode
        if self.is_type_mode.get():
            self.last_x += self.pixel_width
            if self.last_x >= self.pixel_width * self.sprite_width:
                self.last_x = 1
                self.last_y += self.pixel_height
                if self.last_y >= self.pixel_height * self.sprite_height:
                    self.last_y = 1
            self.key_draw(self.last_x, self.last_y)
        elif self.is_replace_mode.get():
            self.key_draw(self.last_x, self.last_y)


    def resize_canvas(self, value):
        self.pixel_width = int(value)
        self.pixel_height = self.pixel_width * self.height_multiplier.get()
        self.canvas_width = self.sprite_width * self.pixel_width
        self.canvas_height = self.sprite_height * self.pixel_height
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)

        self.draw_canvas_from_memory()
    
    def draw_canvas_from_memory(self):
        temp_key = self.last_key
        temp_color = self.current_color
        temp_text_color = self.text_color
        temp_last_pos = [self.last_x,self.last_y]
        for y in range(self.sprite_height):
            for x in range(self.sprite_width):
                self.last_key = self.sprite_array[y][x]
                self.current_color = self.color_array[y][x]
                self.text_color = self.text_color_array[y][x]
                self.key_draw(x*self.pixel_width,y*self.pixel_height)
        self.last_key = temp_key
        self.current_color = temp_color
        self.text_color = temp_text_color
        self.last_x = temp_last_pos[0]
        self.last_y = temp_last_pos[1]

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

    def draw_preview(self):
        self.char_preview.create_rectangle(0,0,self.preview_width,
                                           self.preview_width*self.height_multiplier.get(),fill=self.current_color)
        self.char_preview.create_text(self.preview_width/2,self.preview_width*self.height_multiplier.get()/2,text=self.last_key,fill=self.text_color,
                                      font=("Consolas", int(self.preview_width), "bold"))
    def draw(self,event):
        if event.x is None:
            return
        self.key_draw(event.x, event.y)

    def store_current_char(self,x,y):
        """Takes mouse coords, not array coords"""
        textx,texty = self.get_text_coords(x, y)
        char_used = self.last_key
        # store as space if you can't read the text (same color as background)
        if self.current_color == self.text_color:
            char_used = " "
        self.sprite_array[texty][textx] = char_used
        self.color_array[texty][textx] = self.current_color
        self.text_color_array[texty][textx] = self.text_color

    def key_draw(self, ex,ey):
        # Draw a rectangle of a certain dimension at the given rounded coordinate
        if ex is None:
            return
        x,y = self.get_rounded_coords(ex, ey)
        self.store_current_char(x,y)

        self.canvas.create_rectangle(x, y, x+self.pixel_width, y+self.pixel_height, fill=self.current_color,outline=self.current_color)
        self.canvas.create_text(x+(self.pixel_width/2),
                                y+(self.pixel_height/2),text=self.last_key,
                                font=("Consolas", int(self.pixel_width), "normal"),
                                fill=self.text_color, anchor=CENTER)
        
        self.last_x = ex
        self.last_y = ey

    def reset(self, event):
        self.draw_canvas_from_memory()
        # pass

root = Tk()
app = SpriteMaker(root)
root.mainloop()