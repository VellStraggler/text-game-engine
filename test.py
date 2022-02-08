class Sprite():
    def __init__(self,name="", input_char = "", coords = [-1,-1],array = []):
        self.name = name
        self.array = array # Array will be found from the sprite sheet text doc.
        self.originx = coords[0]
        self.originy = coords[1]
        self.geometry = "default"
        self.movement = False
        self.input_char = input_char 
        
sprite = Sprite(name = "Dave",array = ["hey"])
print(sprite.name,sprite.array)
