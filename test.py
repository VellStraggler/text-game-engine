def rotate_right(array):
    """Rotates the object sprite 90 degrees"""
    sprite = []
    for x in range(len(array[0])//2):
        row = []
        for y in range(len(array)*2):
            row.append("_")
        sprite.append(row)
    # The height becomes the width and vice versa. *Flipped*
    # Tricky. Chars are moved in sets of 2.
    for y in range(len(sprite)):
        for x in range(len(sprite[0])//2):
            sprite[y][-((x*2)+2)] = array[x][(y*2)]
            sprite[y][-((x*2)+1)] = array[x][(y*2)+1]
    return sprite

def print_sprite(array):
    for y in array:
        for x in y:
            print(x,end="")
        print()

array = [["1","2","3","4","5","6"],["a","b","c","d","e","f"]]
array = [["[","]"," "," "," "," "],["[","]","[","]","[","]"]]

# 012345
#0[]    
#1[][][]

print_sprite(array)
print()
new_array = rotate_right(array)
print_sprite(new_array)
print()

# 0123
#0[][]
#1[]
#2[]

array = [['[', ']', '[', ']'], ['[', ']', '_', '_'], ['[', ']', '_', '_']]
print_sprite(array)
print()
new_array = rotate_right(array)
print_sprite(new_array)