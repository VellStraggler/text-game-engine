from tkinter import *
import tkinter
from textengine import *
import PIL.Image as PImage

START = '1.0'
TEXT_HEIGHT_MULT = 1.55
HEIGHT_MULT = 2.4

class SpriteMaker:
    def __init__(self, root:Tk):
        # Root
        self.root = root
        self.root.title("TXTEngine Sprite Editor (Ver: 0.2)")
        self.g = Game()
        for r in range(16):
            root.grid_rowconfigure(r, weight=1, minsize=10)
        for c in range(22):
            root.grid_columnconfigure(c, weight=1, minsize=10)

        self.height_multiplier = DoubleVar(value=HEIGHT_MULT) #1.41 looks good in map, but 2 is realistic sizing

        # Sprite Arrays
        self.sprite_width = IntVar(value=16)
        self.sprite_height = IntVar(value=8)
        self.text_array = []
        self.hex_color_array = []
        self.text_color_array = []
        for y in range(self.sprite_height.get()):
            sprite_row = []
            hex_color_row = []
            text_color_row = []
            for x in range(self.sprite_width.get()):
                sprite_row.append(" ")
                hex_color_row.append("black")
                text_color_row.append("white")
            self.text_array.append(sprite_row)
            self.hex_color_array.append(hex_color_row)
            self.text_color_array.append(text_color_row)
        # color index dictionary
        self.reset_color_indices()



        # Canvas
        self.pixel_width = 36
        self.pixel_height = int(self.pixel_width * self.height_multiplier.get())
        self.canvas_width = self.sprite_width.get() * self.pixel_width
        self.canvas_height = self.sprite_height.get() * self.pixel_height
        self.canvas = Canvas(root, width=self.canvas_width, height=self.canvas_height,bg="white")

        self.canvas_width_scale = Scale(self.root, from_=1, to=60, 
                                        variable=IntVar(value=self.pixel_width), 
                                        command=self.resize_canvas_pixel_ratio,
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
        self.canvas.bind("<Button-1>", self.left_click)       # Left click
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
        self.curr_hex_color = self.default_color
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

        # Create Color Choices from Image Read
        self.esc_to_rgb_color = dict()
        """populated by Image Read"""
        self.hex_to_esc_color = dict()
        self.hex_to_esc_color['black'] = 0
        self.colors_start_num = 16
        self.color_box_size = 10   # size of each square
        self.color_columns = 6     # squares per row
        color_rows = 40
        self.all_colors = Canvas(root, height=self.color_box_size*color_rows, 
                                 width=self.color_box_size*self.color_columns)
        self.read_colors_from_image()

        self.all_colors.bind("<ButtonRelease-1>", self.select_from_all_colors)
        self.all_colors.bind("<ButtonRelease-3>", self.select_from_all_text_colors)

        # Erase Button
        clear_b = Button(root, text='Erase All',command=self.clear_sprite)

        # Color-only mode
        self.is_bg_only = BooleanVar(value=False)
        self.is_text_only = BooleanVar(value=False)
        self.set_mode_text = "Text & Color"
        self.set_mode_dict = {"Text & Color":"Color-Only",
                              "Color-Only":"Text-Only",
                              "Text-Only":"Text & Color"}
        self.set_mode_button = Button(root, text=self.set_mode_text, command=self.set_mode)

        sprite_width_slide = Scale(self.root, from_=1, to=60, 
                                        variable=IntVar(value=self.sprite_width.get()), 
                                        command=self.resize_canvas_width,
                                        orient=HORIZONTAL)
        sprite_height_slide = Scale(self.root, from_=1, to=60, 
                                        variable=IntVar(value=self.sprite_height.get()), 
                                        command=self.resize_canvas_height,
                                        orient=VERTICAL)
        
        self.sprite_file_entry = Text(self.root, width=20,height=1)
        self.sprite_file_entry.insert("1.0","mariokart/karts copy")
        
        sprite_file_name_button = Button(self.root, text = 'Set Sprite File', command=self.set_sprite_path)

        self.current_sprite_name = "example-name"
        self.sprite_name = Label(self.root, width=20, height=1, text=self.current_sprite_name)

        last_sprite = Button(self.root, text="< Last Sprite", command=self.last_sprite)
        next_sprite = Button(self.root, text="Next Sprite >", command=self.next_sprite)

        # Grid Item Placement
        self.canvas_width_scale.grid(row=0, column=0, rowspan=2)
        self.all_colors.grid(        row=0, column=4, rowspan=16)
        self.canvas.grid(            row=1, column=6, rowspan=16, columnspan=16)
        sprite_height_slide.grid(    row=1, column=5, rowspan=3)
        sprite_width_slide.grid(     row=0, column=6)
        self.sprite_file_entry.grid(      row=0, column=7)
        sprite_file_name_button.grid(row=0, column=8)
        self.sprite_name.grid(       row=0, column=9)
        last_sprite.grid(            row=0, column=10)
        next_sprite.grid(            row=0, column=11)

        self.copy_button.grid(       row=2, column=0)
        self.type_mode.grid(         row=3, column=0)
        self.replace_mode.grid(      row=4, column=0)
        clear_b.grid(                row=5, column=0)
        self.set_mode_button.grid(   row=6, column=0)
        self.char_preview.grid(      row=13, column=1, rowspan=3, columnspan=3)
        
        self.draw_preview()
        self.re_ratio()

    def set_mode(self):
        self.set_mode_text = self.set_mode_dict[self.set_mode_text]
        self.set_mode_button.config(text=self.set_mode_text)
        if self.set_mode_text == "Color-Only":
            self.is_bg_only.set(True)
            self.is_text_only.set(False)
        elif self.set_mode_text == "Text-Only":
            self.is_bg_only.set(False)
            self.is_text_only.set(True)
        else:
            self.is_bg_only.set(False)
            self.is_text_only.set(False)

    def read_colors_from_image(self):
        image_file = PImage.open("chars_and_colors/colors_by_number.png")
        image = image_file.load()
        # FIXME: skip legacy colors for now
        color_width = 200
        color_height = 20
        start_coord = [70,70] # midnight blue
        num = self.colors_start_num
        for y in range(40):
            for x in range(6):
                xcoord, ycoord = color_width*x, color_height*y

                raw_color = image[start_coord[0] + xcoord, start_coord[1] + ycoord]
                rgb = (raw_color[0], raw_color[1], raw_color[2])
                self.esc_to_rgb_color[num] = rgb
                hex_color = self.get_rgb_to_hex(rgb)
                self.hex_to_esc_color[hex_color] = num


                xcoord2, ycoord2 = x * self.color_box_size, y * self.color_box_size
                self.all_colors.create_rectangle(
                    xcoord2, ycoord2, xcoord2 + self.color_box_size, ycoord2 + self.color_box_size,
                    fill=hex_color, outline="")
                num+=1

    def flip_colors(self,event):
        old_bg = self.curr_hex_color
        self.set_color(self.text_color)
        self.set_text_color(old_bg)

    def get_rgb_to_hex(self, rgb:list):
        return "#%02x%02x%02x" % rgb   # convert RGB → "#RRGGBB"
        # if isinstance(rgb,list):
        # return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def select_from_all_text_colors(self, event):
        self.select_color_bg_fg(event, False)
    def select_from_all_colors(self, event):
        self.select_color_bg_fg(event, True)

    def select_color_bg_fg(self, event, is_background):
        x,y = event.x//self.color_box_size, event.y//self.color_box_size
        index = x + self.colors_start_num + (y * self.color_columns)
        rgb_code = self.esc_to_rgb_color[index]
        hex_code = self.get_rgb_to_hex(rgb_code)
        if is_background:
            self.set_color(hex_code)
        else:
            self.set_text_color(hex_code)
        print(index)

    def last_sprite(self):
        if self.sprite_index == 0:
            self.sprite_index = len(self.sprite_names)
        self.sprite_index = (self.sprite_index - 1)
        self.set_sprite()
        
    def next_sprite(self):
        self.sprite_index = (self.sprite_index + 1)%len(self.sprite_names)
        self.sprite_name.config(text= self.sprite_names[self.sprite_index])
        self.set_sprite()

    def set_sprite(self):
        # self.resize_canvas_dimensions(self.sprite_width.get(), self.sprite_height.get())
        self.current_sprite_name = self.sprite_names[self.sprite_index]
        self.current_sprite = self.sprites[self.current_sprite_name]
        self.sprite_name.config(text= self.current_sprite_name)
        self.sprite_height.set(len(self.current_sprite))
        self.sprite_width.set(len(self.current_sprite[0]))
        # print("".join(self.current_sprite[0]))
        # print(self.sprite_height.get())
        # print(self.sprite_width.get())
        self.re_ratio(False)
        self.text_array = []
        self.hex_color_array = []
        self.text_color_array = []
        for y in self.current_sprite:
            line = []
            hline = []
            tline = []
            for x in y:
                line.append(x)
                hline.append("black")
                tline.append("white")
            self.text_array.append(line)
            self.hex_color_array.append(hline)
            self.text_color_array.append(tline)
        self.draw_canvas_from_memory()

    def set_sprite_file_name(self):
        self.read_sprites(self.sprite_file_entry.get(START, END).replace("\n","") + ".txt")

    def read_sprites(self, path):
        """DOES NOT READ COLOR, SPRITE ONLY"""
        self.sprites = dict()
        with open(path, 'r',encoding='utf-8') as file:
            lines = file.readlines()
        header_lines = []
        for i,line in enumerate(lines):
            if "$" in line:
                header_lines.append(i)
                lines[i] = lines[i][1:]
        for i in range(len(header_lines)-1):
            header = str(lines[header_lines[i]])
            name = header[:header.index("$")]
            header = header[header.index("$") + 1:]
            end = header_lines[i+1]
            if len(header) > 2:
                end = (header_lines[i] + header_lines[i+1])//2 + 1
            sprite_array = []
            for y in range(header_lines[i]+1, end):
                sprite_array.append(lines[y][:-1])
            self.sprites[name] = sprite_array
        # for sname,sprite in self.sprites.items():
        #     print(sname,"\n",sprite,"\n")
        

    def set_sprite_path(self):
        self.set_sprite_file_name()
        self.sprite_names = list(self.sprites.keys())
        self.sprite_index = 0
        self.sprite_name.config(text= self.sprite_names[self.sprite_index])
        self.set_sprite()

        self.draw_canvas_from_memory()

    def re_ratio(self, redraw=True):
        value = self.pixel_width
        self.resize_canvas_pixel_ratio(value, redraw)

    def set_char(self, c):
        self.last_key = c
        self.draw_preview()

    def clear_sprite(self):
        for y in range(self.sprite_height.get()):
            for x in range(self.sprite_width.get()):
                self.hex_color_array[y][x] = self.default_color
                self.text_array[y][x] = " "
                self.text_color_array[y][x] = self.default_text_color
        self.reset_color_indices()
        self.draw_canvas_from_memory()

    def reset_color_indices(self):
        """Resets/creates esc_to_color_index.
        0 ('black' in hex) is always at index 0"""
        self.esc_to_color_index = dict()
        self.esc_to_color_index[0] = 0

    def init_hover_outline(self):
        self.hover_outline = self.canvas.create_rectangle(0,0,self.pixel_width,self.pixel_height,
                                                          outline="gray")

    def set_color(self, value):
        self.curr_hex_color = value
        self.draw_preview()

    def set_text_color(self,value):
        self.text_color = value
        self.draw_preview()

    def copy(self):
        # create an empty string array to be filled with escape colors
        final_esc_colors = ["0"] * len(self.esc_to_color_index.keys())
        # refer to the esc_to_color_index to populate final_esc_colors
        for esc_color in self.esc_to_color_index.keys():
            i = self.esc_to_color_index[esc_color]
            final_esc_colors[i] = str(esc_color)
        final_esc_colors_str = ",".join(final_esc_colors[1:]) # skip black
        # create header sprite data
        header = "$" + self.current_sprite_name + "$" + final_esc_colors_str + "$below$\n"
        # FIXME: can be ignored if not last sprite
        footer = "$$"

        text = ""
        colors = ""
        for y in range(len(self.text_array)):
            text_row = []
            color_row = []
            for x in range(len(self.text_array[y])):
                text_row.append(self.text_array[y][x])
                hex_color = self.hex_color_array[y][x]
                esc_color = self.hex_to_esc_color[hex_color]
                color_index = self.esc_to_color_index[esc_color]
                color_row.append(str(color_index))
            text += ("".join(text_row)) + "\n"
            colors += ("".join(color_row)) + "\n"
            
        copy_text = header + text + colors + footer
        root.clipboard_append(copy_text)
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
            # outline moves with type mode
            # this is to remove the previous outline

            self.last_x, self.last_y = self.get_next_typing_coord_over(self.last_x, self.last_y)

            # update where the outline draws from too
            self.last_outline = (self.last_x, self.last_y)
            self.press_x, self.press_y = self.get_next_typing_coord_over(self.last_x, self.last_y)
            self.key_draw(self.last_x, self.last_y)
        elif self.is_replace_mode.get():
            self.key_draw(self.last_x, self.last_y)
        self.draw_outline()

    def get_next_typing_coord_over(self, x, y):
        x += self.pixel_width
        if x >= self.pixel_width * self.sprite_width.get():
            x = 1
            y += self.pixel_height
            if y >= self.pixel_height * self.sprite_height.get():
                y = 1
        return x,y

    def deselect(self, event):
        self.press_x, self.press_y = -100, -100
        self.draw_outline()

    def draw_outline(self):
        """ should be called last as it overlays the canvas"""
        # draw over previous outline
        old_text_x, old_text_y = self.get_text_coords(self.last_outline[0], self.last_outline[1])
        self.draw_canvas_from_memory(old_text_x, old_text_y, old_text_x+1, old_text_y+1)

        x,y = self.get_rounded_coords(self.press_x, self.press_y)
        bg_x,bg_y = self.get_text_coords(self.press_x, self.press_y)
        bg_color = self.hex_color_array[bg_y][bg_x]
        outline_color = "white"
        if bg_color == "white":
            outline_color = "black"
        self.canvas.create_rectangle(x, y, x+self.pixel_width, y+self.pixel_height,
                                     outline=outline_color)
        
    def resize_canvas_width(self, new_width):
        self.resize_canvas_dimensions(int(new_width), self.sprite_height.get())

    def resize_canvas_height(self, new_height):
        self.resize_canvas_dimensions(self.sprite_width.get(), int(new_height))

    def resize_canvas_dimensions(self, new_width:int, new_height:int):
        copy_width = int(self.sprite_width.get())
        if copy_width > int(new_width):
            copy_width = new_width
        copy_height = int(self.sprite_height.get())
        if copy_height > int(new_height):
            copy_height = new_height

        # create new arrays for use
        new_text_array = [[" "] * new_width for _ in range(new_height)]
        new_bg_array   = [["black"] * new_width for _ in range(new_height)]
        new_fg_array   = [["white"] * new_width for _ in range(new_height)]
        
        # copy from the previous array
        for y in range(copy_height):
            for x in range(copy_width):
                new_text_array[y][x] = self.text_array[y][x]
                new_bg_array[y][x] = self.hex_color_array[y][x]
                new_fg_array[y][x] = self.text_color_array[y][x]

        # reassign arrays to new arrays
        self.text_array = new_text_array
        self.hex_color_array = new_bg_array
        self.text_color_array = new_fg_array

        self.sprite_height.set(new_height)
        self.sprite_width.set(new_width)

        self.re_ratio()


    def resize_canvas_pixel_ratio(self, value, redraw=True):
        """Ratio is based on pixel width for a single character"""
        self.pixel_width = int(value)
        self.pixel_height = int(self.pixel_width * self.height_multiplier.get())
        self.canvas_width = self.sprite_width.get() * self.pixel_width
        self.canvas_height = self.sprite_height.get() * self.pixel_height
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)

        if redraw:
            self.draw_canvas_from_memory()
    
    def draw_canvas_from_memory(self, start_x = 0, start_y = 0, end_x = None, end_y = None):
        """Redraws the whole canvas by default"""
        if end_x == None:
            end_x = self.sprite_width.get()
            end_y = self.sprite_height.get()
            # Erase everything below
            self.canvas.delete("all")
            self.init_hover_outline()
            

        temp_key = self.last_key
        temp_color = self.curr_hex_color
        temp_text_color = self.text_color
        temp_last_pos = [self.last_x,self.last_y]
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                self.last_key = self.text_array[y][x]
                self.curr_hex_color = self.hex_color_array[y][x]
                self.text_color = self.text_color_array[y][x]
                self.key_draw(x*self.pixel_width,y*self.pixel_height)
        self.last_key = temp_key
        self.curr_hex_color = temp_color
        self.text_color = temp_text_color
        self.last_x = temp_last_pos[0]
        self.last_y = temp_last_pos[1]


    def left_click(self, event):
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
                                           self.preview_width*self.height_multiplier.get(),fill=self.curr_hex_color)
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
        if self.is_bg_only.get():
            self.last_key = self.text_array[texty][textx]
        elif self.is_text_only.get():
            self.curr_hex_color = self.hex_color_array[texty][textx]
        char_used = self.last_key
        # store as space if you can't read the text (same color as background)
        if self.curr_hex_color == self.text_color:
            char_used = " "
        self.text_array[texty][textx] = char_used
        self.hex_color_array[texty][textx] = self.curr_hex_color
        self.text_color_array[texty][textx] = self.text_color

    def record_color_as_used(self):
        """'black' counts as a hex color"""
        if self.curr_hex_color not in self.hex_to_esc_color.keys():
            self.hex_to_esc_color[self.curr_hex_color] = self.hex_to_esc_color(self.curr_hex_color)
        # don't overwrite any colors index after writing
        esc_color = self.hex_to_esc_color[self.curr_hex_color]
        if esc_color not in self.esc_to_color_index.keys():
            self.esc_to_color_index[esc_color] = len(self.esc_to_color_index)

    def key_draw(self, ex,ey):
        # Draw a rectangle of a certain dimension at the given rounded coordinate
        if ex is None:
            return
        x,y = self.get_rounded_coords(ex, ey)
        self.store_current_char(x,y)
        self.record_color_as_used()

        self.canvas.create_rectangle(x, y, x+self.pixel_width, y+self.pixel_height, fill=self.curr_hex_color,outline=self.curr_hex_color)
        self.canvas.create_text(x+(self.pixel_width/2),
                                y+(self.pixel_height/2),text=self.last_key,
                                font=("Consolas", int(self.pixel_width*TEXT_HEIGHT_MULT), "normal"),
                                fill=self.text_color, anchor=CENTER)
        
        self.last_x = ex
        self.last_y = ey

        # print("\nescape to index:", self.esc_to_color_index.items())
        # print("hex to escape:", self.hex_to_esc_color.items())

    def on_move(self, event):
        x,y = self.get_rounded_coords(event.x, event.y)
        if self.is_bg_only.get():
            # get the character we're hovering over
            tx,ty = self.get_text_coords(x,y)
            hover_char = self.text_array[ty][tx]
            if self.last_key != hover_char:
                self.last_key = hover_char
                self.draw_preview()
        elif self.is_text_only.get():
            tx,ty = self.get_text_coords(x,y)
            hover_color = self.hex_color_array[ty][tx]
            if self.curr_hex_color != hover_color:
                self.curr_hex_color = hover_color
                self.draw_preview()


        self.canvas.coords(self.hover_outline,
                           x, y, x + self.pixel_width, y + self.pixel_height)
        self.canvas.tag_raise(self.hover_outline)
        

    def release(self, event):
        self.release_x, self.release_y = event.x, event.y
        self.draw_canvas_from_memory()

        # move cursor along if in type mode
        if self.is_type_mode.get():
            # update where the outline draws from too
            self.last_outline = self.get_next_typing_coord_over(self.last_x, self.last_y)
            self.press_x, self.press_y = self.get_next_typing_coord_over(self.last_x, self.last_y)
            self.key_draw(self.last_x, self.last_y)

        self.draw_outline()

    def entered(self, _):
        self.canvas.itemconfigure(self.hover_outline, state= "normal")
    def left(self, _):
        self.canvas.itemconfigure(self.hover_outline, state= "hidden")

    def root_click(self, event):
        if event.widget is not self.canvas:
            self.deselect(event)

root = Tk()
app = SpriteMaker(root)
root.mainloop()