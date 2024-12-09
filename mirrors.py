from statics import deconstruct_path

class Mirrors():
    def __init__(self):
        self.mirrors = dict() #world_name:list of mirrors
        self.types = dict()
    def new_type(self,name:str,flip_sprites:bool=False,color:int=-1,
        flip_horizontal:bool=False,flip_vertical:bool=False,
        ripple:bool=False,brighten:int=0):
        self.types[name] = self.Mirror_Type(flip_sprites,color,
            flip_horizontal,flip_vertical,ripple,brighten)
    def new(self,world_name,mirror_name,x1,y1,x2,y2,copy_x,copy_y):
        world_name = deconstruct_path(world_name)
        if world_name not in self.mirrors:
            self.mirrors[world_name]=[]
        self.mirrors[world_name].append(self.Mirror(mirror_name,x1,y1,x2,y2,copy_x,copy_y))
    class Mirror():
        """This is for instances of rectangular areas of land that are
        reflective. It is assumed that the location being mirrored has
        the same dimensions as the mirror."""
        def __init__(self,mirror_name,x1,y1,x2,y2,copy_x,copy_y):
            self.mirror_name = mirror_name
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.copy_x = copy_x
            self.copy_y = copy_y
    class Mirror_Type():
        """Create reflection templates to use here, either on the
        map or on objects. Using a color sets the whole reflection
        to that color. The brighten variable makes the reflected text
        backgrounds brighter if a positive integer, or darker if
        negative. When flip_sprites is on, the game will look for
        objects in the reflection area and find their sprites and find
        out if those sprites have other sides."""
        def __init__(self,flip_sprites:bool=False,color:int=-1,
        flip_horizontal:bool=False,flip_vertical:bool=False,
        ripple:bool=False,brighten:int=0):
            self.flip_sprites = flip_sprites
            self.color = color
            self.flip_horizontal = flip_horizontal
            self.flip_vertical = flip_vertical
            self.ripple = ripple
            self.brighten = brighten

            if flip_horizontal: self.y_mult = -1
            else:               self.y_mult = 1
            if flip_vertical:   self.x_mult = -1
            else:               self.x_mult = 1
