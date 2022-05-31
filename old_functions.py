W_WID = 110
W_HEI = 30

ZER = '\033[H'
RIT = '\033[1C'
BLANK = " "
def grid_patcher(array:list,map=False):
    """Makes arrays rectangular, that they are filled with arrays of
     uniform length."""
    assert len(array) > 0, "Error: Empty array put in."
    max_length = 0
    if map:
        max_length = W_WID
        while len(array) < W_HEI:
            array.insert(0,[BLANK])
    # The length of out_map is the extent of y.
    for y in range(0,len(array)):
        if len(array[y]) > max_length:
            max_length = len(array[y])
    # Makes all columns the same length.
    for row in array:
        for s in range(0,max_length - len(row)):
            if type(row) == type(list()): 
                row.append(BLANK)
            elif type(row) == type(str()):
                row = row + BLANK
            else:
                assert False, "Only strings and lists can be in the array"
    return array

def replace_chars(self,obj,new_char):
    """ Replaces the characters of an object on the
    INPUT_MAP with new_char."""
    new_obj = self.obj_from_char(new_char)
    assert new_obj.height() == 1, "New object's gotta be short."
    if obj.height()%new_obj.height()==0 and obj.width()%new_obj.width()==0:
        for y in range(obj.height()):
            for x in range(obj.width()//new_obj.width()):
                nx = obj.origx + (x * new_obj.width())
                ny = obj.origy - obj.height() + 1 + y
                if self.curr_map.get_xy_rend(nx,ny) != BLANK:
                    self.curr_map.set_xy_rend(nx,ny,new_char)

def flip_sprite_old(self):
    """Flips the sprite of an image vertically (left to right)"""
    self.face_right = not self.face_right
    for y in range(self.height()):
        for x in range(self.width()//2+self.width()%2):
            hold = self.array[y][x]
            if hold in FLIP_CHARS.keys():
                hold = FLIP_CHARS[hold]
            self.array[y][x] = self.array[y][self.width()-x-1]
            if self.array[y][x] in FLIP_CHARS.keys():
                self.array[y][x] = FLIP_CHARS[self.array[y][x]]
            self.array[y][self.width()-x-1] = hold

def add_color(self,obj,char,row=1):
    if char != SIGN:
        if char != "_" or row != 0:
            char = obj.color + char + self.default_color
    return char

def add_to_sparse(self,x,y,char):
        obj = self.objs.copy(self.obj_from_char(char),x,y)
        i = 0
        max = len(self.objs.objs)
        while i < max-1:
            if self.objs.objs[i].origy < y:
                i+=1
            elif self.objs.objs[i].origy == y and self.objs.objs[i].origx < x:
                i+=1
            else:
                self.objs.objs.insert(i,obj)
                i = max
        self.curr_map.sparse_map.insert(0,[x,y,char])

def move_cursor(x=0,y=0):
    """Moves the cursor from its current position"""
    if x < 0:
        x *= -1
        print(f"\033[{x}D",end='',flush=True)
    elif x > 0:
        print(f"\033[{x}C",end="",flush=True)
    if y < 0:
        y *= -1
        #print(f"\033[{y}B",end='')
        print(f"\033[{y}A",end="",flush=True)
    elif y > 0:
        print("\n"*y,flush=True)

def render_obj_old(self,obj):
    """Print a sprite at its object's origin."""
    start_y = obj.origy+1-obj.height()
    end_y = min([obj.origy+1,self.map.height-1])
    start_x = find_non(obj.sprite[-1],SKIP) + obj.origx
    if obj.geom!="background":
        thing_behind = False
        thing_ahead = False
        for x in range(start_x,start_x+obj.width()):
            if len(self.map.rend[end_y-2][x]) > 1:
                thing_behind = True
                # If the row above the baseline of an object has a thickness greater than one, something is behind the object.
            if len(self.map.rend[end_y][x]) > 1:
                thing_ahead = True
            if len(self.map.rend[end_y-1][x]) > 1:
                thing_ahead = True
                # If the row below the baseline of an object has a thickness greater than one, something is in front.
            """If something is ahead and behind, we will insert under the top layer. When there are just two layers and until we hit three or one, we will append.
            If nothing is ahead, we will always append. Same if nothing is behind.
            """
        if not thing_ahead:
            for y in range(start_y,end_y):
                start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.origx
                end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.origx,self.map.width-1])+1
                for x in range(start_x,end_x):
                    char = obj.sprite[y-start_y][x-obj.origx]
                    if SKIP not in char:
                        self.map.rend[y][x].append(char)
        else:
            obj_ahead_found = thing_behind
            for y in range(start_y,end_y):
                start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.origx
                end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.origx,self.map.width-1])+1
                # Don't attempt to print out of bounds
                for x in range(start_x,end_x):
                    char = obj.sprite[y-start_y][x-obj.origx]
                    layers = len(self.map.rend[y][x])
                    if layers == 3 or layers == 1:
                        obj_ahead_found = True
                    if SKIP not in char: # If this is not a blank character
                        if layers > 1 and obj_ahead_found:
                                self.map.rend[y][x].insert(-1,char)
                        else:
                            self.map.rend[y][x].append(char)
    else: # Add to background. Working!
        for y in range(start_y,end_y):
            start_x = find_non(obj.sprite[y-start_y],SKIP)+obj.origx
            end_x = min([rfind_non(obj.sprite[y-start_y],SKIP)+obj.origx,self.map.width-1])+1
            for x in range(start_x,end_x):
                char = obj.sprite[y-start_y][x-obj.origx]
                if SKIP not in char: # If this is not a blank character
                    if self.map.rend[y][x][0] == BLANK:
                        self.map.rend[y][x][0] = char

    # Add any text above the object sprite
    # Only works on static objects thus far.
    """if obj.txt > -1:
        txt = self.texts[obj.txt]
        out_y = obj.origy - obj.height() - 1
        out_x = obj.origx + (obj.width())//2 - len(txt)//2
        [self.map.set_xy_rend(out_x+i,out_y,-1,txt[i]) for i in range(len(txt))]"""

