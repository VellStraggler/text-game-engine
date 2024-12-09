from time import sleep, time
from statics import BLANK, BUBBLE, DEFAULT_COLOR, DEFAULT_TEXT, RETURN, S_LINE, WINDOW_HEI, WINDOW_WID, solidify_path
from objs import Objs


class Map():
    """Three arrays are stored in a Map object: the wasd input 
    map, the output map, and a geom map.
    Set the map path upon initialization"""
    def __init__(self,universal_objs=set()):
        self.path = "" #WILL INCLUDE DIRPATH
        self.background_color = DEFAULT_COLOR
        self.text_color = DEFAULT_TEXT

        self.input_map = list() # Made to store user-made map. 1D list of strings.
        self.rend = [] # Map of what will be rendered. 3-Dimensional.
        self.geom = [] # For checking collision.
        self.print_map = ""
        self.screen = []
        self.mirrors = []
        self.setting = "color"
        self.last_used_color = DEFAULT_COLOR

        self.objs = Objs(universal_objs)

        self.height = WINDOW_HEI
        self.width = WINDOW_WID
        self.camera_x = 0
        self.camera_y = 0 # start_window_y
        self.camera_star = None #The player, usually.
        self.end_camera_y = WINDOW_HEI
        self.end_camera_x = WINDOW_WID
            # These are the map coordinates of the 
            # top-left-most char shown in the window.
            
        self.disp_msg = ""
        self.msg_timer = 0

    def set_path(self,path,directed_path=False):
        """ Stores characters and their coords in the input map,
        using a preset path. Also sets self.width and self.height. """
        if not directed_path:
            path = solidify_path(path)
        # Adds parent directory of running program
        self.path = path
        y = 0
        maxwidth = 0
        with open(path,'r') as file:
            line = file.readline() # stores first line as string
            while line:
                line = line[:-1] # Remove newline calls.
                if len(line) > maxwidth:
                    maxwidth = len(line)
                for x in range(len(line)):
                    char = line[x]
                    if char != BLANK:
                        self.input_map.append([x,y,char])
                y += 1
                line = file.readline()
        self.height = y
        self.width = maxwidth
        self.init_rend()
        self.init_geom()

    def set_disp_msg(self,new_msg):
        self.msg_timer = time() + len(new_msg)/15
        self.disp_msg =[[self.background_color+BUBBLE[0][0]],
                        [self.background_color+BUBBLE[1][0]],
                        [self.background_color+BUBBLE[2][0]]]
        new_msg = BLANK + new_msg + BLANK
        for c in new_msg:
            self.disp_msg[0].append(BUBBLE[0][1])
            self.disp_msg[1].append(c)
            self.disp_msg[2].append(BUBBLE[2][1])
        self.disp_msg[0].append(BUBBLE[0][2])
        self.disp_msg[1].append(BUBBLE[1][0])
        self.disp_msg[2].append(BUBBLE[2][2])

    def init_geom(self):
        """ Create geom map of size self.width by self.height."""
        if len(self.geom) == 0: # If the map is new.
            for y in range(self.height):
                line = list()
                for x in range(self.width):
                    line.append(0)
                self.geom.append(line)
        else:self.clear_geom()
    def clear_geom(self):
        for y in range(self.height):
            for x in range(self.width):
                self.geom[y][x] = 0
    def init_rend(self):
        if len(self.rend) == 0: # If the map is new.
            for y in range(self.height):
                new_row = []
                for x in range(self.width):
                    new_item = [[BLANK]] # z-levels start at 1
                    new_row.append(new_item)
                self.rend.append(new_row)
        else:self.clear_rend()
    def clear_rend(self):
        for y in range(self.height):
            for x in range(self.width):
                self.rend[y][x] = list(BLANK) # Remove all other z-levels

    def print_all(self,data=""):
        """Displays the proper area of self.rend. No longer includes
        newline escapes. Appending to a new screen list is oddly faster
        than editing a screen list."""
        self.screen = []
        if self.setting == "color":
            [[self.get_print_pixel(self.rend[row][x][-1],x) for x in range(self.camera_x,self.end_camera_x)] for row in range(self.camera_y,self.end_camera_y)]
        elif self.setting == "geom":
            [[self.get_print_pixel(str(int(self.geom[row][x])),x) for x in range(self.camera_x,self.end_camera_x)] for row in range(self.camera_y,self.end_camera_y)]
        else:
            [[self.get_print_pixel(self.rend[row][x][-1][-1],x) for x in range(self.camera_x,self.end_camera_x)] for row in range(self.camera_y,self.end_camera_y)]
        self.add_message()
        self.add_data(data)
        self.print_map = RETURN + self.text_color + "".join(self.screen)
        print(self.print_map)
    def get_print_pixel(self,color_char_pair,x):
        """Filters a colored character to not call
        the same color escape code as has been most
        recently called."""
        if len(color_char_pair)==1:
            color = self.background_color
            char = color_char_pair
        else:
            color = color_char_pair[:-1]
            char = color_char_pair[-1]

        if color != self.last_used_color:
            self.last_used_color = color
            char = color + char
        self.screen.append(char)
        return char
    def add_message(self):
        if len(self.disp_msg) > 0:
            start = int(len(self.screen)*((WINDOW_HEI-len(self.disp_msg)-.5)/WINDOW_HEI))
            row_down = int(len(self.screen)*(1/WINDOW_HEI))
            half_msg_len = len(self.disp_msg[0])//2-1
            i = start
            for row in self.disp_msg:
                for c in row:
                    self.screen[i-half_msg_len]=str(c)
                    i += 1
                start += row_down
                i = start
    def add_data(self,data):
        if len(data)>0:
            i = int(len(self.screen)*((WINDOW_HEI-1)/WINDOW_HEI))
            self.screen[i-1] += self.background_color
            for c in data:
                self.screen[i]=c
                i +=1
            self.screen[i] += self.background_color
    def display_timer(self):
        if len(self.disp_msg) > 0:
            if self.msg_timer < time():
                self.disp_msg = ""
    def print_to_black(self, mixer):
        """Clears the screen line by line. Moves
        theme volume from 100 to 0%."""
        print(DEFAULT_COLOR + RETURN,end="")
        volume = 1
        for line in range(WINDOW_HEI):
            volume -= 1/WINDOW_HEI
            print(S_LINE)
            mixer.music.set_volume(volume)
            sleep(.03)
    def print_from_black(self, mixer):
        print(RETURN,end="")
        volume = 0
        for row in range(self.camera_y,self.end_camera_y):
            line = []
            for x in range(self.camera_x,self.end_camera_x):
                line.append(self.get_print_pixel(self.rend[row][x][-1],x))
            print("".join(line))
            volume += 1/WINDOW_HEI
            mixer.music.set_volume(volume)
            sleep(.03)
        mixer.music.set_volume(1)
        
    def set_xy_geom(self,x,y,boolean=1):
        """Sets boolean value at a given position on map"""
        self.geom[y][x] = boolean
    def get_xy_geom(self,x,y):
        """Returns what boolean value is at this position."""
        return self.geom[y][x]
    def set_xy_rend(self,x,y,z,char):
        """Sets char at a given position on map"""
        if self.rend[y][x][z] == BLANK:
            self.rend[y][x][z] = char
        else:
            self.rend[y][x].append(char)
    def remove_xy_rend(self,x,y,char):
        if len(self.rend[y][x]) > 1:
            for z in range(len(self.rend[y][x])):
                if self.rend[y][x][z] == char:
                    self.rend[y][x].pop(z)
                    break
        elif self.rend[y][x][0] == char: # Only one layer.
            self.rend[y][x][0] = BLANK
            
    def get_xy_rend(self,x,y,z=-1):
        return self.rend[y][x][z]

    def center_camera(self,x,y):
        """Takes a coordinate and centers the camera on that point."""
        half_wid = WINDOW_WID//2
        half_hei = WINDOW_HEI//2
        if x + half_wid >= self.width:
            x = self.width - half_wid -1
        elif x - half_wid < 0:
            x = half_wid
        if y + half_hei >= self.height:
            y = self.height - half_hei -1
        elif y - half_hei < 0:
            y = half_hei
        self.camera_x = x - half_wid
        self.camera_y = y - half_hei
        self.end_camera_x = self.camera_x + WINDOW_WID
        self.end_camera_y = self.camera_y + WINDOW_HEI
