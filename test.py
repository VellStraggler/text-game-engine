import keyboard as keys
def rotate_map():
    print("alt")

def zoom(_in):
    if _in:
        print("in")
    else:
        print("out")
run = True
while run:
    if keys.is_pressed("alt"):
        rotate_map()
    elif keys.is_pressed("ctrl+up arrow"):
        zoom(True)
    elif keys.is_pressed("ctrl+down arrow"):
        zoom(False)
    elif keys.is_pressed("q"):
        run = False