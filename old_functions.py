W_WID = 110
W_HEI = 30
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