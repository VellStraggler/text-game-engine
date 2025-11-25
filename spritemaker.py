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
        for c in range(22):
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
        self.pixel_width = 36
        self.pixel_height = int(self.pixel_width * self.height_multiplier.get())
        self.canvas_width = self.sprite_width * self.pixel_width
        self.canvas_height = self.sprite_height * self.pixel_height
        self.canvas = Canvas(root, width=self.canvas_width, height=self.canvas_height,bg="white")

        self.canvas_width_scale = Scale(self.root, from_=1, to=60, 
                                        variable=IntVar(value=self.pixel_width), 
                                        command=self.resize_canvas,
                                        orient=HORIZONTAL)  

        # Mouse Position
        self.last_x = 0
        self.last_y = 0
        self.press_x = 0
        self.press_y = 0
        self.release_x = 0
        self.release_y = 0
        self.last_outline = [0,0]
        self.move_x, self.move_y = 0,0
        self.mouse_inside = False

        self.hover_outline = self.canvas.create_rectangle(0,0,self.pixel_width,self.pixel_height,
                                                          outline="gray")
        self.canvas.itemconfigure(self.hover_outline, state= "hidden")
        self.canvas.tag_raise(self.hover_outline)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.activate)       # Left click
        self.canvas.bind("<B1-Motion>", self.draw)         # Drag while left-click held
        self.canvas.bind("<ButtonRelease-1>", self.release)  # Release mouse button
        self.canvas.bind("<Motion>", self.on_move)
        self.canvas.bind("<Enter>", self.entered)
        self.canvas.bind("<Leave>", self.left)
        self.canvas.bind("<Button-3>",self.flip_colors)
        self.root.bind("<Button-1>", self.root_click)


        self.last_key = "#"
        self.root.bind("<Key>", self.key_pressed)
        self.default_color = "black"
        self.default_text_color = "white"
        self.current_color = self.default_color
        self.text_color = self.default_text_color

        # Type Mode
        self.is_type_mode = BooleanVar(value=False)
        self.type_mode = Checkbutton(root, text="Type Mode", variable= self.is_type_mode)

        # Replace Mode
        self.is_replace_mode = BooleanVar(value=False)
        self.replace_mode = Checkbutton(root, text="Replace Mode", variable=self.is_replace_mode)

        # Copy Button
        self.copy_button = Button(root, text="Copy Text", command=self.copy)

        # Special Text
        text_chars = "◤◥╱╲⎺│¯◉◕◔◓◑◐◨◧▼▲▶◀▄"
        self.special_text_buttons = []
        tc_columns = 10
        for i in range(len(text_chars)):
            button = Button(text=text_chars[i], command=lambda c = text_chars[i]: self.set_char(c))
            button.grid(row=(i%tc_columns), column =(i//tc_columns)+1)
            self.special_text_buttons.append(button)

        # Preview Character
        self.preview_width = 60
        self.char_preview = Canvas(root,width=self.preview_width, height=self.preview_width*self.height_multiplier.get())

        # Color Choices
        image_file = PImage.open("chars_and_colors/colors_by_number.png")
        image = image_file.load()
        # FIXME: skip legacy colors for now
        self.colors_start_num = 16
        color_width = 200
        color_height = 20
        start_coord = [70,70] # midnight blue
        self.color_dict = dict()
        num = self.colors_start_num
        for x in range(6):
            for y in range(40):
                color = image[start_coord[0] + (color_width*x), start_coord[1] +(color_height*y)]
                self.color_dict[num] = (color[0], color[1], color[2])
                num+=1
        
        # print(color_dict)
        self.color_box_size = 10   # size of each square
        self.color_columns = 40       # squares per row
        self.all_colors = Canvas(root, height=self.color_box_size*self.color_columns, 
                                 width=self.color_box_size*(200//self.color_columns))


        for i, (num, rgb) in enumerate(self.color_dict.items()):
            tk_color = "#%02x%02x%02x" % rgb   # convert RGB → "#RRGGBB"

            y = (i % self.color_columns) * self.color_box_size
            x = (i // self.color_columns) * self.color_box_size

            self.all_colors.create_rectangle(
                x, y, x + self.color_box_size, y + self.color_box_size,
                fill=tk_color, outline=""
            )

        self.all_colors.bind("<ButtonRelease-1>", self.select_from_all_colors)
        self.all_colors.bind("<ButtonRelease-3>", self.select_from_all_text_colors)

        # Erase Button
        clear_b = Button(root, text='Erase All',command=self.clear_sprite)

        # Grid Item Placement
        self.canvas_width_scale.grid(row=0, column=0, rowspan=2)
        self.all_colors.grid(        row=0, column=4, rowspan=16)
        self.canvas.grid(            row=0, column=5, rowspan=16, columnspan=16)
        self.copy_button.grid(       row=2, column=0)
        self.type_mode.grid(         row=3, column=0)
        self.replace_mode.grid(      row=4, column=0)
        clear_b.grid(                row=5, column=0)
        self.char_preview.grid(      row=13, column=1, rowspan=3, columnspan=3)
        
        self.draw_preview()
        self.resize_canvas(self.pixel_width)

    def flip_colors(self,event):
        old_bg = self.current_color
        self.set_color(self.text_color)
        self.set_text_color(old_bg)

    def rgb_to_hex(self, rgb):
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def select_from_all_text_colors(self, event):
        self.select_color_bg_fg(event, False)
    def select_from_all_colors(self, event):
        self.select_color_bg_fg(event, True)

    def select_color_bg_fg(self, event, is_background):
        y,x = event.x//self.color_box_size, event.y//self.color_box_size
        index = x + self.colors_start_num + (y * self.color_columns)
        rgb_code = self.color_dict[index]
        hex_code = self.rgb_to_hex(rgb_code)
        if is_background:
            self.set_color(hex_code)
        else:
            self.set_text_color(hex_code)

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
        self.draw_outline()

    def deselect(self, event):
        self.press_x, self.press_y = -100, -100
        self.draw_outline()


    def draw_outline(self):
        """ should be called last as it overlays the canvas"""
        # overwrite previous outline
        old_text_x, old_text_y = self.get_text_coords(self.last_outline[0], self.last_outline[1])
        self.draw_canvas_from_memory(old_text_x, old_text_y, old_text_x+1, old_text_y+1)

        x,y = self.get_rounded_coords(self.press_x, self.press_y)
        bg_x,bg_y = self.get_text_coords(self.press_x, self.press_y)
        bg_color = self.color_array[bg_y][bg_x]
        outline_color = "white"
        if bg_color == "white":
            outline_color = "black"
        self.canvas.create_rectangle(x, y, x+self.pixel_width, y+self.pixel_height,
                                     outline=outline_color)

    def resize_canvas(self, value):
        self.pixel_width = int(value)
        self.pixel_height = int(self.pixel_width * self.height_multiplier.get())
        self.canvas_width = self.sprite_width * self.pixel_width
        self.canvas_height = self.sprite_height * self.pixel_height
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)

        self.draw_canvas_from_memory()
    
    def draw_canvas_from_memory(self, start_x = 0, start_y = 0, end_x = None, end_y = None):
        """Redraws the whole canvas by default"""
        if end_x == None:
            end_x = self.sprite_width
            end_y = self.sprite_height

        temp_key = self.last_key
        temp_color = self.current_color
        temp_text_color = self.text_color
        temp_last_pos = [self.last_x,self.last_y]
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
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

        self.last_outline = self.press_x, self.press_y
        self.press_x, self.press_y = event.x, event.y
        self.draw(event)
        self.draw_outline()

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
        self.last_outline = self.press_x, self.press_y
        self.press_x, self.press_y = event.x, event.y
        self.draw_outline()

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

    def on_move(self, event):
        x,y = self.get_rounded_coords(event.x, event.y)
        self.canvas.coords(self.hover_outline,
                           x, y, x + self.pixel_width, y + self.pixel_height)
        self.canvas.tag_raise(self.hover_outline)
        
        # self.draw_outline()

    def release(self, event):
        self.release_x, self.release_y = event.x, event.y
        self.draw_canvas_from_memory()
        self.draw_outline()

    def entered(self, event):
        self.canvas.itemconfigure(self.hover_outline, state= "normal")
    def left(self, event):
        self.canvas.itemconfigure(self.hover_outline, state= "hidden")

    def root_click(self, event):
        if event.widget is not self.canvas:
            self.deselect(event)

root = Tk()
app = SpriteMaker(root)
root.mainloop()